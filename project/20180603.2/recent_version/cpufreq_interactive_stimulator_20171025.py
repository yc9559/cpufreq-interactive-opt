# @Author:	Matt Yang 
# @Date:	2017-10-21 20:46:13 
# @Require: Python 3.6
# stimulate interactive behavior，brute force

# 20171026 MOD fallback to circle cruve to score the result, move to wider range(target: 0,270), seems has better ability to get best result
# 20171025 ADD cust-top-20171025-40ms, new workload test model, 40ms interval rather than 100ms, but perfom badly according to the test
# 20171023 ADD new workload test model, 斗鱼 3min + bilibili danmu 2min + 启动和滑屏 3min + 阅读 2min + 输入法和浏览 3min + 本地视频 1min
# 20171022 MOD reference score f(x), emphasis on long serial lag
# 20171022 ADD new workload test model, 斗鱼 30% + bilibili 20% + 启动和滑屏30% + 阅读 20%
# 20171021 ADD boostpulse_duration support
# 20171021 ADD calculate_ref_powersum(), compare to a fixed competitor
# 20171021 ADD POWER_TABLE_DICT, better format of processor power&ipc model
# 20171016 ADD bit cover to filiter such as [1,1,1,2,1,1,1,1,1,1] when hispeed=500, decrease useless benchmark created, about saving 60%
# 20171016 MOD decrease target_loads_generator complexity, 6->5 degree of freedom
# 20171015 MOD freq_to_table function call -> inline, 10% less time comsuption
# 20171015 ADD reference score f(x), i dont know it fit real world or not
# 20171014 MOD change miss&congestion decision, too high load (800mhz*100%) will be ignored
# 20171013 ADD real time mode, workload now wont be sum up
# 20171012 ADD congestion log, to predict lag

import random
import csv
import multiprocessing
import time
import math
import operator
import copy
import os

CPU_THREAD = 3
# it seems no difference between 3000 and 300, result is almost the same
GREEDY_VM = 6            # 100vm about 4.3 min
GREEDY_VM_MULTIPLIER = 400   # to reduce process create overhead
WORKLOAD_LENGTH = 5000
TARGET_IDEAL_RUNTIME = 110
TARGET_PER_SCORE = 69
# oval cruve has better targeted dirction than circle cruve
exam_exp = lambda result: (result[3]-TARGET_IDEAL_RUNTIME)**2 + (result[2]-TARGET_PER_SCORE)**2
# WORKLOAD_FILE = 'Trepn_workload.csv'
# WORKLOAD_FILE = 'Trepn_workload_20171022.csv'   # 斗鱼 30% + bilibili 20% + 启动和滑屏30% + 阅读 20%
WORKLOAD_FILE = 'Trepn_workload_20171023.csv'   # 斗鱼 3min + bilibili danmu 2min + 启动和滑屏 3min + 阅读 2min + 输入法和浏览 3min + 本地视频 1min
# WORKLOAD_FILE = 'cust-top-20171025-40ms.csv'    # 自定义C代码采集，数据源/proc/stat，40ms间隔，斗鱼 1min + mxplayer 1min + coolapk,zhihu 3min + bilibili danmu 2min + bilibili scroll 1min
HIGH_WORKLOAD = 80000
CONGEST_L1 = 90
CONGEST_L2 = 99
POWER_TABLE_DICT = {
    'phone':    400,
    'tablet':   950,
    's820':     [[1.05,69,115],130,260,450,640,850,980,1430,1890,2430,3050],      # S820 kryo HP single x 1.3
    's821':     [[1.05,0,250],180,220,310,480,750,1040,1370,1900,2380,2980],     # S821 kryo HP single x 2, big is the same as LITTLE credit by 叶落情殇 in coolapk
    '7420a57':  [[1.0,0,280],150,240,350,480,630,880,1170,1490,1950,2600],      # anandtech 7420 A57 x 2
    '7420a53':  [[0.8,0,270],50,70,130,210,330,490,710,1000,1350,1820],         # anandtech 7420 A53 X3 INSERT VALUE
    '950a72':   [[1.1,0,300],150,260,380,500,650,850,1120,1300,1650,2100],     # Kirin 950 A72 X2 https://www.anandtech.com/show/9878/the-huawei-mate-8-review/3
    's810a57':  [[1.0,0,250],150,290,440,630,890,1180,1580,2170,3130,4900],     # S810 A57 x 2 https://www.anandtech.com/show/8933/snapdragon-810-performance-preview/4  http://tieba.baidu.com/p/4244007169?see_lz=1
    's810a53':  [[0.8,0,225],100,110,130,230,390,630,1010,1600,1800,1800],       # S810 A53 x 3 the same as above 1.8g-2.0g does not exist
    's801':     [[0.7,0,320],240,350,520,700,960,1180,1450,1800,2150,2550],     # S800 krait 400 pvs4 single x 2.5
    'denverk1': [[1.0,69,110],550,950,1300,1850,2550,3150,4350,4550,5550,6250],  # nexus9 x 2 100%
    's835a73':  [[1.15,0,320],170,230,360,490,620,730,880,1090,1380,1750],      # S835 A73 x 2 MI6 credit by 叶落情殇 in coolapk
    's835a53':  [[0.8,0,400],160,200,310,410,500,570,650,770,870,1000]          # S835 A53 x 3 MI6 credit by 叶落情殇 in coolapk
}
AP = 's821'
RELATIVE_IPC = POWER_TABLE_DICT[AP][0][0]
TARGET_PER_SCORE = POWER_TABLE_DICT[AP][0][1]
TARGET_IDEAL_RUNTIME = POWER_TABLE_DICT[AP][0][2]
POWER_TABLE_TOTAL = POWER_TABLE_DICT[AP][1:]
POWER_BASE = POWER_TABLE_DICT['phone']
# for i in range(10):
#     POWER_TABLE_TOTAL[i] += POWER_BASE


def freq_to_targetload(freq,target_loads):
    id = ( freq_to_table(freq) // 100 ) - 1
    return target_loads[id]

def freq_to_abovedelay(freq,above_hispeed_delay):
    id = ( freq // 100 ) - 1        # now freq has been fit into freq_table
    return above_hispeed_delay[id]

# fit 780mhz into 800mhz
def freq_to_table(freq):
    freq = ( freq // 100 + 1 ) * 100
    # if freq < 100:
    #     freq = 100
    if freq > 1000:
        freq = 1000
    return freq

# interactive kernel
def choose_freq(freq,load,target_loads):
    freqmin = 0
    freqmax = 1000
    loadadjfreq = freq * load
    while 1:
        prevfreq = freq
        # tl = freq_to_targetload(freq,target_loads)
        t = ( freq // 100 + 1 ) * 100   # the same as above
        if t > 1000:                    # the same as above
            t = 1000                    # the same as above
        tl = target_loads[t//100 - 1]   # the same as above
        freq = loadadjfreq // tl
        # freq = freq_to_table(freq)
        freq = ( freq // 100 + 1 ) * 100    # the same as above
        if freq > 1000:                     # the same as above
            freq = 1000                     # the same as above
        if freq > prevfreq:
            freqmin = prevfreq
            if freq >= freqmax:
                freq = freqmax - 100
                if freq == freqmin:
                    freq = freqmax
                    break
        elif freq < prevfreq:
            freqmax = prevfreq
            if freq <= freqmin:
                freq = freqmin + 100
                if freq == freqmax:
                    break
        else:
            break
    return freq

# def workload_generator():
#     workload = []
#     for i in range(WORKLOAD_LENGTH):
#         workload.append(random.randint(1*100,99*1000))
#     return workload

#using Pareto distributions to stimulate 20/80 in real world
def workload_generator():
    workload = []
    # random.seed(RANDOM_SEED)      #due to result unstable
    for i in range(WORKLOAD_LENGTH):
        t = random.paretovariate(1) - 1
        if t > 2:
            t = random.paretovariate(1) - 1
            if t > 2:
                t = 2
            # t = 3
        workload.append(int(t/2*97*1000 + 3000))
    return workload

def workload_reader(filename, relative_performance):
    workload = []
    workload_file = open(filename,'r')
    for usage in workload_file:
        i = int(float(usage) * 1000 / relative_performance)
        if i < 100000:
            workload.append(i)
        else:
            workload.append(100000)
    workload_file.close()
    return workload

def calculate_ideal_powersum(workload):
    powersum = 0
    for i in workload:
        freq = i // 100
        freq = freq_to_table(freq)
        powersum += POWER_TABLE_TOTAL[freq//100 - 1]
    return powersum

# compare to 835 A73 mobile phones with EAS schd
def calculate_ref_powersum():
    ref_ipc = POWER_TABLE_DICT['s835a73'][0][0]
    ref_power_table_total = POWER_TABLE_DICT['s835a73'][1:]
    ref_power_base = POWER_TABLE_DICT['phone']
    for i in range(10):
        ref_power_table_total[i] += ref_power_base

    ref_workload = workload_reader(WORKLOAD_FILE, ref_ipc)
    powersum = 0
    for i in ref_workload:
        freq = i // 100
        freq = freq_to_table(freq)
        powersum += ref_power_table_total[freq//100 - 1]
    return powersum

def target_loads_generator(availble_loads):
    target_loads = []
    for a4 in availble_loads:
        for a5 in availble_loads:
            for a6 in availble_loads:
                for a7 in availble_loads:
                    for a8 in availble_loads:
                        target_loads.append([50,60,50,a4,a5,a6,a7,a8,70,90])
    return target_loads

def above_hispeed_delay_generator(availble_delays):
    above_hispeed_delay = []
    for a4 in availble_delays:
        for a5 in availble_delays:
            for a6 in availble_delays:
                for a7 in availble_delays:
                    for a8 in availble_delays:
                        above_hispeed_delay.append([1,1,1,a4,a5,a6,a7,a8,3,2])
    return above_hispeed_delay

def benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration, 
                go_hispeed, hispeed_freq, min_sampling_time, target_loads):
    pool = 0
    freq = 1000
    miss = [0,0,0]          #[30fps,15fps,stuck]
    congestion = [0,0]      #[level1,level2]
    # recent_miss = -1
    recent_miss = 0
    miss_2n_sum = 0
    min_time_counter = min_sampling_time
    above_delay_counter = 0
    boostpulse_duration_counter = 0
    powersum = POWER_TABLE_TOTAL[9]
    for i in workload:
        # pool += i                     # load can be add
        pool = i                        # test for real task
        #miss decision
        cpuload = pool // freq + 1      # for fully usage of pool
        if cpuload > 100:
            cpuload = 100
        pool = pool - freq * cpuload

        if i < HIGH_WORKLOAD:           # too high load filiter
            if cpuload >= CONGEST_L2:
                congestion[1] += 1
            if cpuload >= CONGEST_L1:
                congestion[0] += 1

        if pool <= 0:
            # smooth
            if pool < 0:
                pool = 0
            # write miss
            if recent_miss > 0:
                miss_2n_sum += 2**recent_miss
                if recent_miss > 3:
                    recent_miss = 3
                miss[recent_miss-1] += 1
                recent_miss = 0
        else:
            # lag
            if i < HIGH_WORKLOAD:           # too high load filiter
                recent_miss += 1
            else:
                # write miss
                if recent_miss > 0:
                    miss_2n_sum += 2**recent_miss
                    if recent_miss > 3:
                        recent_miss = 3
                    miss[recent_miss-1] += 1
                    recent_miss = 0

        # interactive part
        prevfreq = freq
        freq = choose_freq(freq, cpuload, target_loads)

        min_time_counter -= 1
        above_delay_counter -= 1
        boostpulse_duration_counter -= 1
        # boost mode
        if cpuload >= go_hispeed:
            freq = max(freq, hispeed_freq)
            boostpulse_duration_counter = boostpulse_duration
        # above hispeed delay limit
        if freq > prevfreq and prevfreq >= hispeed_freq and above_delay_counter > 0:
            freq = prevfreq
        # keep boost, unless the boostpulse duration expires
        if freq < hispeed_freq and boostpulse_duration_counter > 0:
            freq = hispeed_freq
        # scaling down limit
        if freq < prevfreq and min_time_counter > 0:
            freq = prevfreq
        # freq adjustment must keep for this duration
        if freq != prevfreq:
            min_time_counter = min_sampling_time
            if freq >= hispeed_freq:
                # above_delay_counter = freq_to_abovedelay(freq, above_hispeed_delay)
                above_delay_counter = above_hispeed_delay[(freq // 100) - 1]
        powersum += POWER_TABLE_TOTAL[freq//100 - 1]

    # power comsuption statistics
    relative_ideal_runtime = ideal_powersum / powersum * 100
    relative_ref_runtime = ref_powersum / powersum * 100

    # smooth score function v20171016
    # if miss[2] > 5:
    #     average_lag = (congestion[1] - miss[0] - miss[1]*2) / miss[2]
    # else:
    #     average_lag = (congestion[1] - miss[0] - miss[1]*2) / 5
    # if average_lag-1 > 1:
    #     average_lag = math.log10(average_lag - 1)
    # else:
    #     average_lag = 0
    # total_congestion = congestion[1] / 1000
    # total_lag = math.sqrt(miss[2] / 100)
    # fps15 = miss[1] / 125
    # fps30 = miss[0] / 250
    # ref_score = 40*average_lag + 25*total_congestion + 20*total_lag + 10*fps15 + 5*fps30

    # print(miss_2n_sum)
    # smooth score function v20171022
    lag_statistics  = 0.5 * math.sqrt(miss_2n_sum / 1500)       # 1000 based on qualcomm default param result
    total_99load    = 0.2 * math.sqrt(congestion[1] / 1500) 
    total_stuck     = 0.15 * math.sqrt(miss[2] / 100)
    fps15           = 0.1 * math.sqrt(miss[1] / 100)
    fps30           = 0.05 * math.sqrt(miss[0] / 900)
    ref_score       = 100 * (lag_statistics + total_99load + total_stuck + fps15 + fps30)

    return [miss, congestion, ref_score, relative_ideal_runtime, relative_ref_runtime]

def benchmark_thread(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration_list,
                    go_hispeed_list, hispeed_freq, min_sampling_time_list, target_loads_list):
    result_buffer = []
    for boostpulse_duration in boostpulse_duration_list:
        for go_hispeed in go_hispeed_list:
            for min_sampling_time in min_sampling_time_list:
                for target_loads in target_loads_list:
                    if boostpulse_duration >= min_sampling_time:
                        result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                                            go_hispeed, hispeed_freq, min_sampling_time, target_loads)
                        miss = result[0]
                        cong = result[1]
                        score = exam_exp(result)
                        # if result[2] <= 60 and result[3] >= 83:
                        result_buffer.append([miss[0],miss[1],miss[2],cong[0],cong[1],result[2],result[3],result[4],
                            above_hispeed_delay,boostpulse_duration,go_hispeed,hispeed_freq,min_sampling_time,target_loads,score])
    # count.value += 1
    return result_buffer

def finding_greedy_vm(workload, ideal_powersum, param_init, param_range, vm_id):
    result_buffer = []
    # to reduce process create overhead
    for multiplier in range(GREEDY_VM_MULTIPLIER):
        # init something
        best_score = 999999999
        param = copy.deepcopy(param_init)
        random.seed(time.time() + vm_id)    # better first random number
        # it come to its end in 3-6 iteration
        for loops in range(8):     
            list6 = [0,1,2,3,4,5]
            random.shuffle(list6)
            for x in list6:
                # for different types of parameters
                if isinstance(param[x], int):
                    # regular param
                    partial_best = param[x]
                    for possible_value in param_range[x]:
                        param[x] = possible_value
                        # result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                        #                     go_hispeed, hispeed_freq, min_sampling_time, target_loads)
                        result = benchmark(workload, ideal_powersum, param[0], param[1],
                                            param[2], param[3], param[4], param[5])
                        score = exam_exp(result)
                        # score = -((result[4]-target_ref_runtime)**2 + (result[2]-target_ref_score)**2)
                        # score = -((result[3]-105)**2 + (result[2]-65)**2)
                        if score < best_score:
                            best_score = score
                            partial_best = possible_value
                    param[x] = partial_best
                else:
                    # internal list
                    list10 = [1,2,3,4,5,6,7,8]  # the lowest and highest is useless for above and target
                    random.shuffle(list10)
                    for i in list10:
                        partial_best = param[x][i]
                        for possible_value in param_range[x]:
                            param[x][i] = possible_value
                            # result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                            #                     go_hispeed, hispeed_freq, min_sampling_time, target_loads)
                            result = benchmark(workload, ideal_powersum, param[0], param[1],
                                                param[2], param[3], param[4], param[5])
                            score = exam_exp(result)
                            # score = -((result[4]-target_ref_runtime)**2 + (result[2]-target_ref_score)**2)
                            # score = -((result[3]-105)**2 + (result[2]-65)**2)
                            if score < best_score:
                                best_score = score
                                partial_best = possible_value
                        param[x][i] = partial_best
            
        # log the route of change
        result = benchmark(workload, ideal_powersum, param[0], param[1],
                        param[2], param[3], param[4], param[5]) 
        miss = result[0]
        cong = result[1]
        score = exam_exp(result)
        result_buffer.append([miss[0],miss[1],miss[2],cong[0],cong[1],result[2],result[3],result[4],
                                param[0], param[1],param[2], param[3], param[4], param[5],score])
    return result_buffer

def finding_greedy(workload, ideal_powersum):
    result_buffer = []

    above_hispeed_delay_value_list = range(1, 10+1)
    boostpulse_duration_list = range(1,5+1)
    go_hispeed_list = range(40, 98+1, 2)
    hispeed_freq_list = range(400, 600+1, 100)
    min_sampling_time_list = range(1, 3+1)
    target_loads_value_list = range(98, 2, -2)

    above_hispeed_delay = [1,1,1,1,1,2,2,2,2,8]
    boostpulse_duration = 4
    go_hispeed = 90
    hispeed_freq = 600
    min_sampling_time = 2
    target_loads = [85,80,80,80,80,80,80,80,80,98]

    param_range = [
        above_hispeed_delay_value_list,
        boostpulse_duration_list,
        go_hispeed_list,
        hispeed_freq_list,
        min_sampling_time_list,
        target_loads_value_list
    ]

    param_init = [
        above_hispeed_delay, 
        boostpulse_duration,
        go_hispeed, 
        hispeed_freq, 
        min_sampling_time, 
        target_loads
    ]
    
    in_start_time = time.time()
    estimate_time_pypy3 = GREEDY_VM * GREEDY_VM_MULTIPLIER / 1800 * 77 * 60
    print('Started at: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('Working on it...' + str(CPU_THREAD) + ' Thread(s)')
    print('Method: Greedy VMs %i' % (GREEDY_VM * GREEDY_VM_MULTIPLIER))
    print('Processor: ' + AP)
    print('Remaining time(PyPy3): %.4f hour(s)' %(estimate_time_pypy3 / 3600))
    print('Estimated finish time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(in_start_time + estimate_time_pypy3)))

    processpool = multiprocessing.Pool(processes = CPU_THREAD)
    for vm_id in range(GREEDY_VM):
        processpool.apply_async(finding_greedy_vm,
                    args = (workload, ideal_powersum, param_init, param_range, vm_id, ),
                    callback = log_result)
    processpool.close()
    processpool.join()
    
    return result_buffer

def log_result(result):
    result_buffer.extend(result)
    return 0

def show_progress():
    while count.value <= total_circulation:
        print('progress: %.2f %%' % (count.value / total_circulation * 100) , end='\r')
        time.sleep(10)
    return 0

def csv_output(filename,buffer):
    csvfile = open(filename,"w",newline='')
    writer = csv.writer(csvfile,dialect='excel')
    writer.writerow(['30fps', '15fps', 'stuck', CONGEST_L1, CONGEST_L2, 'Ref Score', 'ideal Runtime %', 'ref Runtime %', 
                    'above_hi_delay', 'boost_dura', 'go_hi', 'hi_freq', 'min_sample', 'target_loads', 'Mixed Score', AP])
    writer.writerows(buffer)
    csvfile.close()
    return 0

def batch_finding_greedy(ap_list):
    # some function depend on GLOBAL VAR
    global AP
    global RELATIVE_IPC
    global POWER_TABLE_TOTAL
    global POWER_BASE
    global result_buffer
    global TARGET_PER_SCORE
    global TARGET_IDEAL_RUNTIME
    for ap in ap_list:
        start_time = time.time()

        # load ap model parameters
        AP = ap
        RELATIVE_IPC = POWER_TABLE_DICT[AP][0][0]
        TARGET_PER_SCORE = POWER_TABLE_DICT[AP][0][1]
        TARGET_IDEAL_RUNTIME = POWER_TABLE_DICT[AP][0][2]
        POWER_TABLE_TOTAL = POWER_TABLE_DICT[AP][1:]
        POWER_BASE = POWER_TABLE_DICT['phone']
        for i in range(10):
            POWER_TABLE_TOTAL[i] += POWER_BASE

        # init variables
        result_buffer = []
        workload = []
        ideal_powersum = 0

        # load workload test model
        workload = workload_reader(WORKLOAD_FILE, RELATIVE_IPC)
        ideal_powersum = calculate_ideal_powersum(workload)

        # give 4 chances, execute interactive optimal parameter with greedy method
        # for t in range(4):
        #     print("loop: %i/4" %(t+1))
        finding_greedy(workload, ideal_powersum)

        # write results to csv
        csvfile_name = time.strftime("%Y-%m-%d %H%M", time.localtime()) + '-' + AP + '-runtime-' + str(TARGET_IDEAL_RUNTIME) + '-score-' + str(TARGET_PER_SCORE) +'.csv'
        csv_output(csvfile_name,result_buffer)

        end_time = time.time()
        print("Finished in %.4f minutes" %((end_time - start_time)/60))
        print('')
    return 0

if __name__ == "__main__":
    batch_start_time = time.time()
    # workload = workload_reader('Trepn_workload_bilibili.csv')
    # workload = workload_reader(WORKLOAD_FILE, RELATIVE_IPC)
    # ideal_powersum = calculate_ideal_powersum(workload)
    ref_powersum = calculate_ref_powersum()
    # result_buffer = []

    # go_hispeed_list = (60,70,80,90,99)
    # boostpulse_duration_list = (1,2,4)
    # hispeed_freq_list = (400,500,600,700,800)
    # min_sampling_time_list = (1,2,3,4)
    # target_loads_list = target_loads_generator((50,60,70,80))
    # target_loads_list = [[60,45,68,85,56,68,79,85,95,95]]
    # target_loads_list = [[50, 60, 50, 50, 85, 85, 85, 80, 85, 90]]
    # target_loads_list = [[80, 90, 90, 90, 85, 85, 85, 80, 85, 90]]
    # above_hispeed_delay_list = above_hispeed_delay_generator((1,2,4,8))
    # workload = workload_generator()
    # estimate_time_pypy3 = 8 * len(go_hispeed_list) * len(hispeed_freq_list) * len(min_sampling_time_list) * len(boostpulse_duration_list) * len(target_loads_list) * len(above_hispeed_delay_list) / 50 / 1024
    # print('Started at: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # print('Remaining time(PyPy3): %.3f hour(s)' %(estimate_time_pypy3 / 3600))
    # print('Estimated finish time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time + estimate_time_pypy3)))
    # print('Working on it...' + str(CPU_THREAD) + ' Thread(s)')
    # print('')
    # processpool = multiprocessing.Pool(processes = CPU_THREAD)
    # processpool.apply_async(benchmark_thread,
    #             args = (workload,ideal_powersum,[1, 1, 1, 1, 1, 1, 2, 2, 1, 1],[4],[90],600,[2],[[85, 85, 85, 85, 85, 85, 90, 90, 90, 90]],),
    #             callback = log_result)
    # processpool.apply_async(benchmark_thread,
    #             args = (workload,ideal_powersum,[1, 1, 1, 1, 1, 1, 6, 10, 10, 2],[6],[70],400,[1],[[80, 4, 8, 70, 72, 80, 78, 84, 98, 98]],),
    #             callback = log_result)
    
    # ref_list = [1,1,1,1,1,1,1,1,1,1]        # bit cover, filiter such as [1,1,1,2,1,1,1,1,1,1] for hispeed 500
    # for hispeed_freq in hispeed_freq_list:
    #     n = hispeed_freq//100 - 1           # get bit cover range, last bit is list[n-1]
    #     for above_hispeed_delay in above_hispeed_delay_list:
    #         if operator.eq(above_hispeed_delay[0:n], ref_list[0:n]):
    #             processpool.apply_async(benchmark_thread,
    #             args = (workload,ideal_powersum, above_hispeed_delay, boostpulse_duration_list, 
    #                     go_hispeed_list,hispeed_freq, min_sampling_time_list, target_loads_list,),
    #             callback = log_result)
    # processpool.close()
    # processpool.join()
    # 810 runtime 60(limit)+15 score 65
    # 7420a53 runtime 90(limit)+10 score 60
    # 821 runtime 70(limit)+15 score 65
    # target_ref_runtime = 75
    # target_ref_score = 65

    # for t in range(4):  # give 4 chances
    #     print("loop: %i/4" %(t+1))
    #     finding_greedy(workload, ideal_powersum)

    # csvfile_name = time.strftime("%Y-%m-%d %H%M", time.localtime()) + '-' + AP + '-runtime-' + str(TARGET_IDEAL_RUNTIME) + '-score-' + str(TARGET_PER_SCORE) +'.csv'
    # csv_output(csvfile_name,result_buffer)
    ap_list = ['s821', '7420a57', '7420a53', 's810a57', 's810a53', 's835a73', 's835a53', 's801', '950a72']
    # ap_list = ['s821', 's810a53']
    # ap_list = ['s835a53']
    batch_finding_greedy(ap_list)
    # a = [1,2,3,4,5]
    # for i in range(5):
    #     random.shuffle(a)
    #     print(a)

    batch_end_time = time.time()
    print("Finished in %.4f minutes" %((batch_end_time - batch_start_time)/60))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # csvfile = open("wordloadmodel.csv","w",newline='')
    # writer = csv.writer(csvfile,dialect='excel')
    # writer.writerow(['seq', 'workload'])
    # for i in range(len(workload)):
    #     writer.writerow([i,workload[i]])
    # csvfile.close()

