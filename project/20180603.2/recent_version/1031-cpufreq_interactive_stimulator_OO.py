# @Author:	Matt Yang 
# @Date:	2017-10-21 20:46:13 
# @Require: Python 3.6
# simulate interactive behavior

# 20171031 ADD interactive.py, use struct obj to save result
# 20171031 MOD dictionary management
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
from copy import *
from interactive import *
from powermodel import *

CPU_THREAD = 3
# it seems no difference between 3000 and 300, result is almost the same
GREEDY_VM = 3           # 100vm about 4.3 min
GREEDY_VM_MULTIPLIER = 5   # to reduce process create overhead
WORKLOAD_LENGTH = 5000
TARGET_IDEAL_RUNTIME = 110
TARGET_PER_SCORE = 69
# oval cruve has better targeted dirction than circle cruve
exam_exp = lambda ap_simu, param: (param.ideal_runtime - ap_simu.target_rel_runtime)**2 + (param.ideal_runtime - ap_simu.target_score)**2
WORKLOAD_DIR = './workload_model/'
CSV_DIR = './csv/'
# WORKLOAD_FILE = 'Trepn_workload.csv'
# WORKLOAD_FILE = 'Trepn_workload_20171022.csv'   # 斗鱼 30% + bilibili 20% + 启动和滑屏30% + 阅读 20%
WORKLOAD_FILE = 'Trepn_workload_20171031.csv'   # 斗鱼 3min + bilibili danmu 2min + 启动和滑屏 3min + 阅读 2min + 输入法和浏览 3min + 本地视频 1min
# WORKLOAD_FILE = 'cust-top-20171025-40ms.csv'    # 自定义C代码采集，数据源/proc/stat，40ms间隔，斗鱼 1min + mxplayer 1min + coolapk,zhihu 3min + bilibili danmu 2min + bilibili scroll 1min
WORKLOAD_FILE = WORKLOAD_DIR + WORKLOAD_FILE
HIGH_WORKLOAD = 80000
CONGEST_L1 = 90
CONGEST_L2 = 99

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

def workload_reader(filename, ap_simulation):
    ap_simulation.workload = []
    workload_file = open(filename,'r')
    for usage in workload_file:
        i = int(float(usage) * 1000 / ap_simulation.relative_ipc)
        if i < 100000:
            ap_simulation.workload.append(i)
        else:
            ap_simulation.workload.append(100000)
    workload_file.close()
    
    return 0

def calculate_ideal_powersum(ap_simulation):
    powersum = 0
    for i in ap_simulation.workload:
        freq = i // 100
        freq = freq_to_table(freq)
        ap_simulation.ideal_freq_choice.append(freq)
        powersum += ap_simulation.power_table[freq//100 - 1]
    ap_simulation.ideal_powersum = powersum
    return 0

# compare to 835 A73 mobile phones with EAS sched
def calculate_ref_powersum(filename):
    ref_ipc = POWER_TABLE_DICT['s835a73'][0][0]
    ref_power_table_total = POWER_TABLE_DICT['s835a73'][1:]
    ref_power_base = POWER_TABLE_DICT['phone']
    for i in range(10):
        ref_power_table_total[i] += ref_power_base

    ref_workload = []
    workload_file = open(filename,'r')
    for usage in workload_file:
        i = int(float(usage) * 1000 / ref_ipc)
        if i < 100000:
            ref_workload.append(i)
        else:
            ref_workload.append(100000)
    workload_file.close()

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

def benchmark(ap_simulation, param_vm):
    pool = 0
    count = 0
    freq = 1000
    miss = [0,0,0]          #[30fps,15fps,stuck]
    congestion = [0,0]      #[level1,level2]
    # recent_miss = -1
    recent_miss = 0
    miss_2n_sum = 0
    variance = 0
    min_time_counter = param_vm.min_sampling_time
    above_delay_counter = 0
    boostpulse_duration_counter = 0
    powersum = 0

    for i in ap_simulation.workload:
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
            variance += (freq - ap_simulation.ideal_freq_choice[count])**2

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
        count += 1
        # interactive part
        prevfreq = freq
        freq = choose_freq(freq, cpuload, param_vm.target_loads)

        min_time_counter -= 1
        above_delay_counter -= 1
        boostpulse_duration_counter -= 1
        # boost mode
        if cpuload >= param_vm.go_hispeed:
            freq = max(freq, param_vm.hispeed_freq)
            boostpulse_duration_counter = param_vm.boostpulse_duration
        # above hispeed delay limit
        if freq > prevfreq and prevfreq >= param_vm.hispeed_freq and above_delay_counter > 0:
            freq = prevfreq
        # keep boost, unless the boostpulse duration expires
        if freq < param_vm.hispeed_freq and boostpulse_duration_counter > 0:
            freq = param_vm.hispeed_freq
        # scaling down limit
        if freq < prevfreq and min_time_counter > 0:
            freq = prevfreq
        # freq adjustment must keep for this duration
        if freq != prevfreq:
            min_time_counter = param_vm.min_sampling_time
            if freq >= param_vm.hispeed_freq:
                # above_delay_counter = freq_to_abovedelay(freq, above_hispeed_delay)
                above_delay_counter = param_vm.above_hispeed_delay[(freq // 100) - 1]
        powersum += ap_simulation.power_table[freq//100 - 1]
    
    # print(miss_2n_sum)
    # print(variance)
    variance = variance / 300000000                    # 300000000 based on qualcomm default param result
    var             = 0.35 * variance
    lag_statistics  = 0.35 * math.sqrt(miss_2n_sum / 800)       # 800 based on qualcomm default param result
    total_99load    = 0.1 * math.sqrt(congestion[1] / 1500) 
    total_stuck     = 0.1 * math.sqrt(miss[2] / 100)
    fps15           = 0.05 * math.sqrt(miss[1] / 100)
    fps30           = 0.05 * math.sqrt(miss[0] / 900)
    ref_score       = 100 * (var + lag_statistics + total_99load + total_stuck + fps15 + fps30)

    # power comsuption statistics
    param_vm.ideal_runtime = ap_simulation.ideal_powersum / powersum * 100
    param_vm.ref_runtime = ap_simulation.ref_powersum / powersum * 100
    param_vm.miss = miss
    param_vm.congestion = congestion
    param_vm.variance = variance
    param_vm.ref_score = ref_score
    param_vm.mixed_score = exam_exp(ap_simulation, param_vm)

    return 0

def finding_greedy_vm(workload, ideal_powersum, param_init, param_range, vm_id):
    result_buffer = []
    # to reduce process create overhead
    for multiplier in range(GREEDY_VM_MULTIPLIER):
        # init something
        best_score = 999999999
        param = deepcopy(param_init)
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

def log_result(result_buffer, param_vm):
    result = []
    result.extend(param_vm.miss)
    result.extend(param_vm.congestion)
    result.append(param_vm.ref_score)
    result.append(param_vm.ideal_runtime)
    result.append(param_vm.ref_runtime)
    result.append(param_vm.variance)
    result.append(param_vm.mixed_score)
    result.append(param_vm.above_hispeed_delay)
    result.append(param_vm.boostpulse_duration)
    result.append(param_vm.go_hispeed)
    result.append(param_vm.hispeed_freq)
    result.append(param_vm.min_sampling_time)
    result.append(param_vm.target_loads)

    result_buffer.append(result)
    return 0

def show_progress():
    while count.value <= total_circulation:
        print('progress: %.2f %%' % (count.value / total_circulation * 100) , end='\r')
        time.sleep(10)
    return 0

def csv_output(filename, buffer, ap_simulation):
    csvfile = open(CSV_DIR + filename,"w",newline='')
    writer = csv.writer(csvfile,dialect='excel')
    writer.writerow(['30fps', '15fps', 'stuck', CONGEST_L1, CONGEST_L2, 'Ref Score', 
                    'ideal Runtime %', 'ref Runtime %', 'Variance', 'Mixed Score', 
                    'above_hi_delay', 'boost_dura', 'go_hi', 'hi_freq', 'min_sample', 
                    'target_loads',  ap_simulation.model_name, WORKLOAD_FILE])
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

        finding_greedy(workload, ideal_powersum)

        # write results to csv
        csvfile_name = time.strftime("%Y-%m-%d %H%M", time.localtime()) + '-' + AP + '-runtime-' + str(TARGET_IDEAL_RUNTIME) + '-score-' + str(TARGET_PER_SCORE) +'.csv'
        csv_output(csvfile_name, result_buffer)

        end_time = time.time()
        print("Finished in %.4f minutes" %((end_time - start_time)/60))
        print('')
    return 0

def finding_greedy_vm_v2(ap_simulation, param_vm, result_buffer):
    above_hispeed_delay_value_list = range(1, 10+1)
    boostpulse_duration_list = range(1,5+1)
    go_hispeed_list = range(40, 98+1, 2)
    hispeed_freq_list = range(400, 600+1, 100)
    min_sampling_time_list = range(1, 4+1)
    target_loads_value_list = range(98, 2, -2)

    for x in range(50):
        param_vm_best = deepcopy(param_vm)
        benchmark(ap_simulation, param_vm_best)

        for i in range(10):
            for value in above_hispeed_delay_value_list:
                bak = param_vm.above_hispeed_delay[i]
                param_vm.above_hispeed_delay[i] = value
                benchmark(ap_simulation, param_vm)
                if param_vm.mixed_score < param_vm_best.mixed_score:
                    param_vm_best = deepcopy(param_vm)
                param_vm.above_hispeed_delay[i] = bak
        
        for value in min_sampling_time_list:
                bak = param_vm.min_sampling_time
                param_vm.min_sampling_time = value
                benchmark(ap_simulation, param_vm)
                if param_vm.mixed_score < param_vm_best.mixed_score:
                    param_vm_best = deepcopy(param_vm)
                param_vm.min_sampling_time = bak

        param_vm = deepcopy(param_vm_best)
        log_result(result_buffer, param_vm)


def finding_greedy_v2():
    result_buffer = []
    best_score = 99999999
    ap = 's821'
    # init Simulation obj
    power_table = POWER_TABLE_DICT[ap][1:]
    for i in range(10):
        power_table[i] += POWER_TABLE_DICT['phone']
    ap_simulation = Simulation('s821', 50, 150)
    ap_simulation.relative_ipc = POWER_TABLE_DICT[ap][0][0]
    ap_simulation.power_table = power_table
    workload_reader(WORKLOAD_FILE, ap_simulation)
    calculate_ideal_powersum(ap_simulation)
    ap_simulation.ref_powersum = ref_powersum

    # init InteractiveParam obj
    param_vm = InteractiveParam()
    param_vm.above_hispeed_delay = [1,1,1,1,1,2,2,2,2,8]
    param_vm.boostpulse_duration = 4
    param_vm.go_hispeed = 90
    param_vm.hispeed_freq = 600
    param_vm.min_sampling_time = 2
    param_vm.target_loads = [85,80,80,80,80,80,80,80,80,98]

    above_hispeed_delay_value_list = range(1, 10+1)
    boostpulse_duration_list = range(1,5+1)
    go_hispeed_list = range(40, 98+1, 2)
    hispeed_freq_list = range(400, 600+1, 100)
    min_sampling_time_list = range(1, 4+1)
    target_loads_value_list = range(98, 2, -2)

    param_range = [
        above_hispeed_delay_value_list,
        boostpulse_duration_list,
        go_hispeed_list,
        hispeed_freq_list,
        min_sampling_time_list,
        target_loads_value_list
    ]

    # finding_greedy_vm_v2(ap_simulation, param_vm, result_buffer)

    # write results to csv
    csvfile_name = time.strftime("%Y-%m-%d %H%M", time.localtime()) + \
                    '-' + ap_simulation.model_name + \
                    '-runtime-' + str(ap_simulation.target_rel_runtime) + \
                    '-score-' + str(ap_simulation.target_score) +'.csv'
    csv_output(csvfile_name, result_buffer, ap_simulation)
    return 0

if __name__ == "__main__":
    batch_start_time = time.time()
    ref_powersum = calculate_ref_powersum(WORKLOAD_FILE)
    # ap_list = ['s821', '7420a57', '7420a53', 's810a57', 's810a53', 's835a73', 's835a53', 's801', '950a72']
    # ap_list = ['s821', 's810a53']
    # ap_list = ['s835a53']
    # batch_finding_greedy(ap_list)
    finding_greedy_v2()

    batch_end_time = time.time()
    print("Finished in %.4f minutes" %((batch_end_time - batch_start_time)/60))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # csvfile = open("wordloadmodel.csv","w",newline='')
    # writer = csv.writer(csvfile,dialect='excel')
    # writer.writerow(['seq', 'workload'])
    # for i in range(len(workload)):
    #     writer.writerow([i,workload[i]])
    # csvfile.close()

