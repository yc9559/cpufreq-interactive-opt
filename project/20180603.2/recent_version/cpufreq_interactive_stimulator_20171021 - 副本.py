# @Author:	Matt Yang 
# @Date:	2017-10-21 20:46:13 
# @Require: Python 3.6
# stimulate interactive behavior，brute force

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

CPU_THREAD = 4
WORKLOAD_LENGTH = 5000
WORKLOAD_FILE = 'Trepn_workload.csv'
HIGH_WORKLOAD = 80000
CONGEST_L1 = 90
CONGEST_L2 = 99
POWER_TABLE_DICT = {
    'phone':    400,
    'tablet':   950,
    's820':     [1.0,130,260,450,640,850,980,1430,1890,2430,3050],      # S820 kryo HP single x 1.3
    's821':     [1.0,180,220,310,480,750,1040,1370,1900,2380,2980],     # S821 kryo HP single x 2, big is the same as LITTLE credit by 叶落情殇 in coolapk
    '7420a57':  [1.0,150,240,350,480,630,880,1170,1490,1950,2600],      # anandtech 7420 A57 x 2
    '7420a53':  [0.8,50,70,130,210,330,490,710,1000,1350,1820],         # anandtech 7420 A53 X3 INSERT VALUE
    '950a72':   [1.1,190,360,550,700,850,1050,1220,1400,1750,2100],     # Kirin 950 A72 X3 https://www.anandtech.com/show/9878/the-huawei-mate-8-review/3
    's810a57':  [1.0,150,290,440,630,890,1180,1580,2170,3130,4900],     # S810 A57 x 2 https://www.anandtech.com/show/8933/snapdragon-810-performance-preview/4  http://tieba.baidu.com/p/4244007169?see_lz=1
    's801':     [0.7,240,350,520,700,960,1180,1450,1800,2150,2550],     # S800 krait 400 pvs4 single x 2.5
    'denverk1': [1.0,550,950,1300,1850,2550,3150,4350,4550,5550,6250],  # nexus9 x 2 100%
    's835a73':  [1.15,170,230,360,490,620,730,880,1090,1380,1750],      # S835 A73 x 2 MI6 credit by 叶落情殇 in coolapk
    's835a53':  [0.8,170,220,330,430,520,570,650,770,870,1000]          # S835 A53 x 3 MI6 credit by 叶落情殇 in coolapk
}
AP = 's821'
RELATIVE_IPC = POWER_TABLE_DICT[AP][0]
POWER_TABLE_TOTAL = POWER_TABLE_DICT[AP][1:]
POWER_BASE = POWER_TABLE_DICT['phone']
for i in range(10):
    POWER_TABLE_TOTAL[i] += POWER_BASE


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
        i = int(int(usage) * 1000 / relative_performance)
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
    ref_relative_performance = POWER_TABLE_DICT['s835a73'][0]
    ref_power_table_total = POWER_TABLE_DICT['s835a73'][1:]
    ref_power_base = POWER_TABLE_DICT['phone']
    for i in range(10):
        ref_power_table_total[i] += ref_power_base

    ref_workload = workload_reader(WORKLOAD_FILE, ref_relative_performance)
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
            if recent_miss > 3:
                recent_miss = 3
            if recent_miss > 0:
                miss[recent_miss-1] += 1
                recent_miss = 0
        else:
            # lag
            if i < HIGH_WORKLOAD:           # too high load filiter
                recent_miss += 1
            else:
                # write miss
                if recent_miss > 3:
                    recent_miss = 3
                if recent_miss > 0:
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

    relative_ideal_runtime = ideal_powersum / powersum * 100
    relative_ref_runtime = ref_powersum / powersum * 100

    if miss[2] > 5:
        average_lag = (congestion[1] - miss[0] - miss[1]*2) / miss[2]
    else:
        average_lag = (congestion[1] - miss[0] - miss[1]*2) / 5
    if average_lag-1 > 1:
        average_lag = math.log10(average_lag - 1)
    else:
        average_lag = 0
    total_congestion = congestion[1] / 1000
    total_lag = math.sqrt(miss[2] / 100)
    fps15 = miss[1] / 125
    fps30 = miss[0] / 250
    ref_score = 40*average_lag + 25*total_congestion + 20*total_lag + 10*fps15 + 5*fps30
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
                        # if result[2] <= 60 and result[3] >= 83:
                        result_buffer.append([miss[0],miss[1],miss[2],cong[0],cong[1],result[2],result[3],result[4],
                            above_hispeed_delay,boostpulse_duration,go_hispeed,hispeed_freq,min_sampling_time,target_loads])
    # count.value += 1
    return result_buffer

def exam_exp(result):
    # return result[4] - 0.8*result[2]
    return -((result[4]-85)**2 + (result[2]-50)**2)

def finding_greedy(workload, ideal_powersum):
    result_buffer = []

    above_hispeed_delay_value_list = range(1, 16+1)
    boostpulse_duration_list = range(1,16+1)
    go_hispeed_list = range(30, 98+1, 2)
    hispeed_freq_list = range(300, 900+1, 100)
    min_sampling_time_list = range(1, 8+1)
    target_loads_value_list = range(10, 98+1, 2)

    above_hispeed_delay = [1,1,1,1,1,2,2,2,2,2]
    boostpulse_duration = 4
    go_hispeed = 90
    hispeed_freq = 600
    min_sampling_time = 2
    target_loads = [80,80,80,80,80,80,80,80,80,80]
    best_score = -65536

    param_range = [
        above_hispeed_delay_value_list,
        boostpulse_duration_list,
        go_hispeed_list,
        hispeed_freq_list,
        min_sampling_time_list,
        target_loads_value_list
    ]

    param = [
        above_hispeed_delay, 
        boostpulse_duration,
        go_hispeed, 
        hispeed_freq, 
        min_sampling_time, 
        target_loads
    ]

    for y in range(10):

        # internal list
        for i in range(0,10):
            partial_best = param[x][i]
            for possible_value in param_range[x]:
                param[x][i] = possible_value
                # result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                #                     go_hispeed, hispeed_freq, min_sampling_time, target_loads)
                result = benchmark(workload, ideal_powersum, param[0], param[1],
                                    param[2], param[3], param[4], param[5])
                score = exam_exp(result)
                if score > best_score:
                    best_score = score
                    partial_best = i
            param[x][i] = partial_best


        for x in range(0,10):
            partial_best = target_loads[x]
            for i in target_loads_value_list:
                target_loads[x] = i
                result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                                    go_hispeed, hispeed_freq, min_sampling_time, target_loads)
                score = exam_exp(result)
                if score > best_score:
                    best_score = score
                    partial_best = i
            target_loads[x] = partial_best
        
        for x in range(0,10):
            partial_best = above_hispeed_delay[x]
            for i in above_hispeed_delay_value_list:
                above_hispeed_delay[x] = i
                result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                                    go_hispeed, hispeed_freq, min_sampling_time, target_loads)
                score = exam_exp(result)
                if score > best_score:
                    best_score = score
                    partial_best = i
            above_hispeed_delay[x] = partial_best
        
        # regular param
        partial_best = param[x]
        for possible_value in param_range[x]:
            param[x] = possible_value
            # result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
            #                     go_hispeed, hispeed_freq, min_sampling_time, target_loads)
            result = benchmark(workload, ideal_powersum, param[0], param[1],
                                param[2], param[3], param[4], param[5])
            score = exam_exp(result)
            if score > best_score:
                best_score = score
                partial_best = i
        param[x] = partial_best


        partial_best = go_hispeed
        for i in go_hispeed_list:
            go_hispeed = i
            result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                                go_hispeed, hispeed_freq, min_sampling_time, target_loads)
            score = exam_exp(result)
            if score > best_score:
                best_score = score
                partial_best = i
        go_hispeed = partial_best

        partial_best = boostpulse_duration
        for i in boostpulse_duration_list:
            boostpulse_duration = i
            result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                                go_hispeed, hispeed_freq, min_sampling_time, target_loads)
            score = exam_exp(result)
            if score > best_score:
                best_score = score
                partial_best = i
        boostpulse_duration = partial_best

        partial_best = min_sampling_time
        for i in min_sampling_time_list:
            min_sampling_time = i
            result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                                go_hispeed, hispeed_freq, min_sampling_time, target_loads)
            score = exam_exp(result)
            if score > best_score:
                best_score = score
                partial_best = i
        min_sampling_time = partial_best

        partial_best = hispeed_freq
        for i in hispeed_freq_list:
            hispeed_freq = i
            result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                                go_hispeed, hispeed_freq, min_sampling_time, target_loads)
            score = exam_exp(result)
            if score > best_score:
                best_score = score
                partial_best = i
        hispeed_freq = partial_best

        result = benchmark(workload, ideal_powersum, above_hispeed_delay, boostpulse_duration,
                            go_hispeed, hispeed_freq, min_sampling_time, target_loads)
        miss = result[0]
        cong = result[1]
        score = exam_exp(result)
        result_buffer.append([miss[0],miss[1],miss[2],cong[0],cong[1],result[2],result[3],result[4],
            above_hispeed_delay,boostpulse_duration,go_hispeed,hispeed_freq,min_sampling_time,target_loads,score])
    
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
                    'above_hi_delay', 'boost_dura', 'go_hi', 'hi_freq', 'min_sample', 'target_loads', 'Real time S810'])
    writer.writerows(buffer)
    csvfile.close()
    return 0

if __name__ == "__main__":
    start_time = time.time()
    # workload = workload_reader('Trepn_workload_bilibili.csv')
    workload = workload_reader(WORKLOAD_FILE, RELATIVE_IPC)
    ideal_powersum = calculate_ideal_powersum(workload)
    ref_powersum = calculate_ref_powersum()
    result_buffer = []

    go_hispeed_list = (60,70,80,90,99)
    boostpulse_duration_list = (1,2,4)
    hispeed_freq_list = (400,500,600,700,800)
    min_sampling_time_list = (1,2,3,4)
    # target_loads_list = target_loads_generator((50,60,70,80))
    # target_loads_list = [[60,45,68,85,56,68,79,85,95,95]]
    target_loads_list = [[50, 60, 50, 50, 85, 85, 85, 80, 85, 90]]
    # target_loads_list = [[80, 90, 90, 90, 85, 85, 85, 80, 85, 90]]
    above_hispeed_delay_list = above_hispeed_delay_generator((1,2,4,8))
    # workload = workload_generator()
    estimate_time_pypy3 = 8 * len(go_hispeed_list) * len(hispeed_freq_list) * len(min_sampling_time_list) * len(boostpulse_duration_list) * len(target_loads_list) * len(above_hispeed_delay_list) / 50 / 1024
    print('Started at: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('Remaining time(PyPy3): %.3f hour(s)' %(estimate_time_pypy3 / 3600))
    print('Estimated finish time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time + estimate_time_pypy3)))
    print('Working on it...' + str(CPU_THREAD) + ' Thread(s)')
    print('')
    # processpool = multiprocessing.Pool(processes = CPU_THREAD)
    # processpool.apply_async(benchmark_thread,
    #             args = (workload,ideal_powersum,[1, 1, 1, 1, 1, 1, 2, 2, 1, 1],[4],[90],600,[2],[[85, 85, 85, 85, 85, 85, 90, 90, 90, 90]],),
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

    result_buffer.extend(finding_greedy(workload, ideal_powersum))

    csvfile_name = time.strftime("%Y-%m-%d %H%M%S", time.localtime()) + '.csv'
    csv_output(csvfile_name,result_buffer)

    end_time = time.time()
    print("Finished in "+str((end_time - start_time)/60)+" minutes")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # csvfile = open("wordloadmodel.csv","w",newline='')
    # writer = csv.writer(csvfile,dialect='excel')
    # writer.writerow(['seq', 'workload'])
    # for i in range(len(workload)):
    #     writer.writerow([i,workload[i]])
    # csvfile.close()

