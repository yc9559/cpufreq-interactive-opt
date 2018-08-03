
import random
import csv
import multiprocessing
import time

WORKLOAD_LENGTH = 1000
POWER_BASE = 300
POWER_TABLE = [180,340,490,680,900,1250,1670,2120,2770,3700] #from anandtech 7420 A57 X3
RANDOM_SEED = 1
CPU_THREAD = 8

def freq_to_targetload(freq,target_loads):
    id = ( freq_to_table(freq) // 100 ) - 1
    return target_loads[id]

def freq_to_table(freq):
    freq = ( freq // 100 + 1 ) * 100
    if freq <= 100:
        freq = 100
    if freq >= 1000:
        freq = 1000
    return freq

def choose_freq(freq,load,target_loads):
    freqmin = 0
    freqmax = 1000
    loadadjfreq = freq * load
    while True:
        prevfreq = freq
        tl = freq_to_targetload(freq,target_loads)
        freq = loadadjfreq // tl
        freq = freq_to_table(freq)
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
    random.seed(RANDOM_SEED)
    for i in range(WORKLOAD_LENGTH):
        t = random.paretovariate(2)-1
        if t > 3:
            t = 3
        workload.append(int(t/3*100*1000))
    return workload
#print(workload_generator())

def calculate_ideal_powersum(workload):
    powersum = 0
    for i in workload:
        freq = i // 100
        freq = freq_to_table(freq)
        powersum = powersum + POWER_BASE + POWER_TABLE[freq//100 - 1]
    return powersum

def target_loads_generator(availble_loads):
    target_loads = []
    for a1 in availble_loads:
        for a2 in availble_loads:
            for a3 in availble_loads:
                for a4 in availble_loads:
                    for a5 in availble_loads:
                        for a6 in availble_loads:
                            for a7 in availble_loads:
                                for a8 in availble_loads:
                                    for a9 in availble_loads:
                                        for a10 in availble_loads:
                                            target_loads.append([a1,a2,a3,a4,a5,a6,a7,a8,a9,a10])
    return target_loads

def benchmark(go_hispeed,hispeed_freq,min_sampling_time,target_loads):
    workload = workload_generator()
    pool = 0
    freq = 1000
    miss = 0
    ideal_powersum = calculate_ideal_powersum(workload)
    powersum = POWER_TABLE[9]
    for i in workload:
        pool = pool + i
        cpuload = pool // freq + 1 #for fully usage of pool
        if cpuload > 100:
            cpuload = 100
        pool = pool - freq * cpuload
        if pool <= 0:
            pool = 0
        if pool > 1000: #10000=100mhz*50%, take it acceptible
            miss = miss + 1
        #interactive part
        prefreq = freq
        min_sampling_time = min_sampling_time -1
        freq = choose_freq(freq,cpuload,target_loads)
        if cpuload >= go_hispeed and freq < hispeed_freq:
            freq = hispeed_freq
        if freq <= prefreq and min_sampling_time > 0 :
            freq = prefreq
        if freq > prefreq:
            min_sampling_time = 4
        powersum = powersum + POWER_BASE + POWER_TABLE[freq//100 - 1]
    return [miss / WORKLOAD_LENGTH , powersum / ideal_powersum]

# def benchmark_thread(go_hispeed_list,hispeed_freq,target_loads_list):
#     min_sampling_time = 2
#     for go_hispeed in go_hispeed_list:
#         for target_loads in target_loads_list:
#             result = benchmark(go_hispeed,hispeed_freq,min_sampling_time,target_loads)
#             #if result[1] == 1.6: 
#             result_buffer.append([result[0],result[1],go_hispeed,hispeed_freq,min_sampling_time,target_loads])
#     return 0

def benchmark_thread(go_hispeed_list,hispeed_freq_list,target_loads):
    min_sampling_time = 2
    result_buffer = []
    for go_hispeed in go_hispeed_list:
        for hispeed_freq in hispeed_freq_list:
            result = benchmark(go_hispeed,hispeed_freq,min_sampling_time,target_loads)
            # if 12 * result[0] + result[1] <= 4.2: 
            if result[0] == 0.18:
                result_buffer.append([result[0],result[1],go_hispeed,hispeed_freq,min_sampling_time,target_loads])
    return result_buffer

def log_result(result):
    result_buffer.extend(result)
    return 0

if __name__ == "__main__":
    start_time = time.time()
    csvfile = open("test.csv","w",newline='')
    writer = csv.writer(csvfile,dialect='excel')
    writer.writerow(['Missed', 'ratio to ideal', 'go_hispeed' , 'hispeed_freq' , 'min_sampling_time' , 'target_loads'])
    result_buffer = []

    go_hispeed_list = (40,50,60,70,80,90,95)
    hispeed_freq_list = (600,700,800,900)
    # min_sampling_time_list = (1,2)
    min_sampling_time = 2
    target_loads_list = target_loads_generator([40,70,85,90])
    #total_circulation = len(go_hispeed_list) * len(hispeed_freq_list) * len(target_loads_list)

    processpool = multiprocessing.Pool(processes = CPU_THREAD)
    for target_loads in target_loads_list:
        processpool.apply_async(benchmark_thread,
        args = (go_hispeed_list,hispeed_freq_list,target_loads,),
        callback = log_result)
    processpool.close()
    processpool.join()
    # count = 1
    # for go_hispeed in go_hispeed_list:
    #     for hispeed_freq in hispeed_freq_list:
    #         for target_loads in target_loads_list:
    #             result = benchmark(go_hispeed,hispeed_freq,min_sampling_time,target_loads)
    #             if result[0] <= 0.2 and result[1] <= 2: 
    #                 result_buffer.append([result[0],result[1],go_hispeed,hispeed_freq,min_sampling_time,target_loads])
    #     print(str(count)+"/7")
    #     count = count + 1
    writer.writerows(result_buffer)
    csvfile.close()
    end_time = time.time()
    print("Finished in "+str((end_time - start_time)/60)+" minutes")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))



