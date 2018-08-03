import csv
import time
from conf import *
from interactive import *

def param_csv_output(filename, header, buffer):
    # csvfile = open(CSV_DIR + filename,'w',newline='') #python3
    csvfile = open(CSV_DIR + filename, 'w')
    writer = csv.writer(csvfile,dialect='excel')
    writer.writerow(header)
    writer.writerows(buffer)
    csvfile.close()
    return 0

def param_txt_output(filename, header, buffer):
    txtfile = open(CSV_DIR + filename, 'w')
    # 2 spaces for markdown ending
    buffer = [str(line)+'  \n' for line in buffer]
    txtfile.writelines(buffer)
    txtfile.close()
    return 0

period_to_ns = lambda period: int(period*20e3-2e3)
freq_to_hz = lambda freq: int(freq*100e3-20e3)

def ceiling_match_freq(freq, freq_table):
    if freq > freq_table[19]:
        freq = freq_table[19]
    ceiling = freq_table[freq-1]
    min_freq = freq_table[0]
    if freq == ceiling:
        return freq
    while freq_table[freq-1] == ceiling and freq > min_freq:
        freq -= 1
    return freq

def above_to_str(param_seq_obj, ap_env, ref_score):
    above_hispeed_delay = list(param_seq_obj.above_hispeed_delay)
    hispeed_freq = param_seq_obj.hispeed_freq
    freq_table = ap_env.freq_table
    min_freq = ap_env.min_freq
    max_freq = ap_env.max_freq
    prev_f = 0
    f = 0
    prev_ahd = 0
    above_string = ''

    # add dynamic freq-limit
    local_above_max = ABOVE_MAX
    limit_freq = max_freq - 1
    while freq_table[limit_freq-1] == max_freq and limit_freq > min_freq:
        limit_freq -= 1
    while limit_freq > local_above_max:
        above_hispeed_delay.append(above_hispeed_delay[-1])
        local_above_max += 1
    limit_idx = limit_freq - ABOVE_MIN
    if is_PERFORMANCE(ref_score):
        if max_freq >= 20:  above_hispeed_delay[limit_idx] = 2
        else:               above_hispeed_delay[limit_idx] = 2
    else:
        if max_freq >= 20:  above_hispeed_delay[limit_idx] = 7
        else:               above_hispeed_delay[limit_idx] = 5

    local_above_levels = local_above_max-ABOVE_MIN+1
    for i in range(local_above_levels):
        prev_f = f
        f = freq_to_table(i+ABOVE_MIN, freq_table)
        if f != prev_f and f <= local_above_max:
            ahd = period_to_ns(above_hispeed_delay[f-ABOVE_MIN])
            if f == hispeed_freq:
                above_string += '%i' %(ahd)
                prev_ahd = ahd
            elif f > hispeed_freq and prev_ahd != ahd:
                above_string += ' %i:%i' %(freq_to_hz(f), ahd)
                prev_ahd = ahd
            else:
                pass
    if len(above_string) == 0:
        above_string = '18000'
    return above_string

def tgload_to_str(param_seq_obj, ap_env):
    target_loads = param_seq_obj.target_loads
    freq_table = ap_env.freq_table
    min_freq = ap_env.min_freq
    prev_f = 0
    f = 0
    prev_tg = 0
    loads_string = ''
    for i in range(TARGETLOADS_LEVELS):
        prev_f = f
        f = freq_to_table(i+TGLOADS_MIN, freq_table)
        if f != prev_f and f <= TGLOADS_MAX:
            tg = target_loads[f-TGLOADS_MIN]
            if f == min_freq:
                # loads_string += '%i' %(target_loads[f-TGLOADS_MIN])
                loads_string += '%i' %(tg)
                prev_tg = tg
            elif abs(prev_tg - tg) > TGLOADS_SAME_THRESHOLD:
                loads_string += ' %i:%i' %(freq_to_hz(f), tg)
                prev_tg = tg
            else:
                pass
    return loads_string

def test_individual(individual, ap_env):
    # train_ref_score     = individual.fitness.values[0]
    # train_ref_lasting   = individual.fitness.values[1]
    test_user_score, \
    test_ref_onscreen_lasting, \
    test_idle_lasting   = interactive_benchmark(individual, ap_env, mode='get_result')
    score       = to_percent(test_user_score)
    lasting     = to_percent(test_ref_onscreen_lasting)
    return score, lasting
    
def log_individual(result_buffer, individual, ap_env, mode='csv'):
    result = []
    user_score, ref_lasting = test_individual(individual, ap_env)

    if ref_lasting == 0:
        return

    p = InteractiveParamSeq(individual, ap_env.freq_table)
    param_seq = list(individual)

    if mode == 'csv':
        result.append(user_score)
        result.append(ref_lasting)
        result.append(p.above_hispeed_delay)
        result.append(p.boostpulse_duration)
        result.append(p.go_hispeed)
        result.append(p.hispeed_freq)
        result.append(p.min_sampling_time)
        result.append(p.target_loads)
        result.append(param_seq)
        result_buffer.append(result)

    if mode == 'txt':
        above_string = above_to_str(p, ap_env, user_score)
        loads_string = tgload_to_str(p, ap_env)

        result.append('========')
        result.append(param_seq)
        result.append('_相对感知卡顿百分比_')
        result.append('%.2f' %(user_score))
        result.append('_相对亮屏续航百分比_')
        result.append('%.2f' %(ref_lasting))
        result.append('above_hispeed_delay:')
        result.append(above_string)
        # result.append('boostpulse_duration:')
        # result.append(period_to_ns(p.boostpulse_duration))
        result.append('go_hispeed_load:')
        result.append(p.go_hispeed)
        result.append('hispeed_freq:')
        result.append(freq_to_hz(p.hispeed_freq))
        result.append('min_sample_time:')
        result.append(period_to_ns(p.min_sampling_time))
        result.append('target_loads:')
        result.append(loads_string)
        result_buffer.extend(result)
    return 0

def log_NSGA2_result(population, ap_env):
    buf_csv = []
    buf_txt = []
    time_str = time.strftime('%Y-%m-%d %H%M%S', time.localtime())
    csvfile_name = time_str + '-' + ap_env.model_name +'.csv'
    txtfile_name = time_str + '-' + ap_env.model_name +'.txt'
    param_seq_header = ['Ref Score', 'ideal lasting %', 
                        'above_hi_delay', 'boost_dura', 'go_hi', 'hi_freq', 'min_sample', 
                        'target_loads', 'param_sequence',  ap_env.model_name, 
                        ap_env.workload_filename]
    for ind in population:
        log_individual(buf_csv, ind, ap_env, mode='csv')
        log_individual(buf_txt, ind, ap_env, mode='txt')
    param_csv_output(csvfile_name, param_seq_header, buf_csv)
    param_txt_output(txtfile_name, param_seq_header, buf_txt)
    print ap_env.model_name + ' csv&txt generated'
    return 0

def log_freq_compare(freq_choice_list, ap_env):
    csvfile_name = time.strftime('%Y-%m-%d %H%M%S', time.localtime()) + '-' + \
                    ap_env.model_name + '-compare' +'.csv'
    param_seq_header = ['Optimal', 'config 1', 'config 2', 'config 3', 
                        'config 4', 'config 5', ap_env.model_name, 
                        ap_env.workload_filename]
    param_csv_output(csvfile_name, param_seq_header, zip(*freq_choice_list))
    return 0

def find_first(arr, condition, key):
    for x in arr:
        if condition(key(x)) == True:
            return x
    return arr[-1]

def find_collection(population, ap_env):
    result_list = list()
    for ind in population:
        s, l = test_individual(ind, ap_env)
        if l > 0:
            result_list.append((s, l, ind))
    get_score   = lambda x: x[0]
    get_lasting = lambda x: x[1]
    ordered_list = sorted(result_list, key=get_lasting, reverse=True)
    perf_choice = find_first(ordered_list, is_PERFORMANCE, get_score)
    bala_choice = find_first(ordered_list, is_BALANCE, get_score)
    pwrs_choice = find_first(ordered_list, is_POWERSAVE, get_score)
    return (perf_choice, bala_choice, pwrs_choice)

def log_collection(population, ap_env, collection=None):
    if not collection:
        collection = find_collection(population, ap_env)
    time_str = time.strftime('%Y-%m-%d %H%M%S', time.localtime())
    colfile_name = time_str + '-collection-' + ap_env.model_name +'.txt'
    param_seq_header = 'collection of parameters\n'
    buf_txt = list()
    for choice in collection:
        log_individual(buf_txt, choice[2], ap_env, mode='txt')
    param_txt_output(colfile_name, param_seq_header, buf_txt)
    print ap_env.model_name + ' collection generated'
    return 0