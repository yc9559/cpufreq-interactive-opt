#coding:utf-8

import math
from array import array
from powermodel import *
from conf import *

to_percent = lambda x: 100*x

def freq_to_targetload(freq,target_loads):
    # id = ( freq_to_table(freq) // 100 ) - 1
    id = freq_to_table(freq) - 1
    return target_loads[id]

def freq_to_abovedelay(freq,above_hispeed_delay):
    id = ( freq // 100 ) - 1        # now freq has been fit into freq_table
    return above_hispeed_delay[id]

# fit 780mhz into 800mhz
def freq_to_table(freq, freq_table):
    # if freq < freq_table[0]:
    #     freq = freq_table[0]
    if freq > freq_table[19]:
        freq = freq_table[19]
    return freq_table[freq-1]

class InteractiveParamSeq(object):
    def __init__(self, param, freq_table, override=False):
        self.above_hispeed_delay = tuple(param[0: ABOVE_LEVELS])
        self.boostpulse_duration = param[ABOVE_LEVELS]
        self.go_hispeed          = param[ABOVE_LEVELS+1]
        self.hispeed_freq        = freq_to_table(param[ABOVE_LEVELS+2], freq_table)
        self.min_sampling_time   = param[ABOVE_LEVELS+3]
        if TGLOADS_FIRST > 0 and override == True:
            param[ABOVE_LEVELS+4+ freq_table[0]-TGLOADS_MIN] = TGLOADS_FIRST
        self.target_loads        = tuple(param[ABOVE_LEVELS+4: ABOVE_LEVELS+4+TARGETLOADS_LEVELS])

def count_tgloads_step(target_loads, freq_table):
    prev_f = 0
    f = 0
    prev_tg = -99
    count = 0
    # loads_string = ''
    for i in range(TARGETLOADS_LEVELS):
        prev_f = f
        f = freq_to_table(i+TGLOADS_MIN, freq_table)
        if f != prev_f and f <= TGLOADS_MAX:
            tg = target_loads[f-TGLOADS_MIN]
            if abs(prev_tg - tg) > TGLOADS_SAME_THRESHOLD:
                count += 1
                prev_tg = tg
                # loads_string += ' %i:%i' %(f, tg)
                # if f <= 8:
                #     count += 1.5
                # elif f > 8 and f <= 12:
                #     count += 1
                # elif f > 12 and f <= 15:
                #     count += 0.5
    # print loads_string
    return count

# interactive kernel
def choose_freq(freq, load, target_loads, freq_table):
    freqmin = 0
    freqmax = 99
    min_freq = freq_table[0]
    max_freq = freq_table[19]
    loadadjfreq = freq * load
    while 1:
        prevfreq = freq
        # tl = freq_to_targetload(freq,target_loads)
        if freq < TGLOADS_MAX:  tl = target_loads[freq - TGLOADS_MIN]
        else:                   tl = target_loads[15]
        
        # freq = loadadjfreq // tl + 1, precision fix
        if loadadjfreq % tl == 0:   freq = loadadjfreq // tl
        else:                       freq = loadadjfreq // tl + 1

        # freq = freq_to_table(freq)
        if freq > max_freq: freq = max_freq
        freq = freq_table[freq-1]
        
        if freq > prevfreq:
            freqmin = prevfreq
            if freq >= freqmax:
                freq = freqmax - 1
                # ceiling match, keep moving left until the hightest lower than freqmax, [10, 12, 12, 15, 15, 15]
                while freq_table[freq-1] == freqmax and freq > min_freq:
                    freq -= 1
                if freq == freqmin:
                    freq = freqmax
                    break
        elif freq < prevfreq:
            freqmax = prevfreq
            if freq <= freqmin:
                freq = freqmin + 1
                # floor match
                freq = freq_table[freq-1]
                if freq == freqmax:
                    break
        if prevfreq == freq:
            break
    return freq

def interactive_benchmark(param, ap_env, mode='test'):
    freq_table = ap_env.freq_table
    power_table = ap_env.power_table
    workload = ap_env.workload
    idleload = ap_env.idleload
    ideal_freq_choice = ap_env.ideal_freq_choice
    min_freq = ap_env.min_freq
    low_bus_freq = ap_env.freq_table[ap_env.min_freq]
    if ENABLE_ENOUGH_CAPACITY:  enough_capacity = ap_env.enough_capacity
    else:                       enough_capacity = ap_env.max_freq * 100

    is_override =  TGLOADS_FIRST > 0 and mode != 'diagnosis'
    p = InteractiveParamSeq(param, freq_table, override=is_override)
    above_hispeed_delay = p.above_hispeed_delay
    boostpulse_duration = p.boostpulse_duration
    go_hispeed          = p.go_hispeed
    hispeed_freq        = p.hispeed_freq
    min_sampling_time   = p.min_sampling_time
    target_loads        = p.target_loads

    pool        = 0
    cycle_no    = -1
    freq        = ap_env.max_freq
    stuck       = 0
    shift       = 0
    congestion  = 0
    # recent_miss = -1
    recent_miss         = 0
    miss_2n_sum         = 0
    variance            = 1
    square_error        = 0
    absolute_error      = 0
    period_lag_counter  = 1
    period_lag_arr      = []
    hispeed_validate_no = 0
    floor_validate_no   = 0
    powersum            = ap_env.base_power * len(workload)
    idle_powersum       = ap_env.idle_power * len(idleload)
    freq_choice         = array('i')
    # tic_actual          = ap_env.tic_actual
    # tic_pred_x2         = 0
    cross_entropy       = 0
    congestion_hist     = [0]*20
    # feel                = (0, 0, 3, 7, 999)  # (60, 30, 15, 7.5, 3.75, )
    feel                = (0, 0, 3, 99, 99)  # (60, 30, 15, 7.5, 3.75, )
    feel_max            = len(feel)-1
    if mode == 'diagnosis': diagnosis = 1
    else:                   diagnosis = 0

    for i in workload:
        cycle_no += 1
        # pool += i                     # load can be add
        pool = i                        # test for real task
        #miss decision
        cpuload = (pool//freq) + 1      # for fully usage of pool
        if cpuload > 100:
            cpuload = 100
        # pool -= freq * cpuload
        # if pool < 0:
        #     pool = 0
        # log every freq choices
        if diagnosis == 1:
            freq_choice.append(freq)

        # == is laggy? ===
        if cpuload >= 100:
            variance += (ideal_freq_choice[cycle_no] - freq)**2
        if i <= enough_capacity:           # too high load filiter
            if cpuload >= CONGEST_LOAD:
            # if freq*100 - i <= PRESERVED_CAPACITY:
                congestion += 1
                recent_miss += 1
                congestion_hist[ideal_freq_choice[cycle_no]-1] += 1
                period_lag_counter += 1+recent_miss
                # square_error += (freq - ideal_freq_choice[cycle_no])**2
                # absolute_error += ideal_freq_choice[cycle_no] - freq
            else:
                if recent_miss > feel_max:
                    recent_miss = feel_max
                if recent_miss >= 3:
                    stuck += 1
                miss_2n_sum += feel[recent_miss]
                recent_miss = 0
            # variance += (freq - ideal_freq_choice[cycle_no])**2
        # tic_pred_x2 += freq*freq

        if (cycle_no+1)%PERIOD_LEN == 0:
            period_lag_arr.append(period_lag_counter)
            period_lag_counter = 1

        # === power comsumption ===
        # powersum += power_table[freq - 1]
        f_load = cpuload/100.0
        powersum += power_table[freq - 1] * (f_load + IDLE_PWR_RATIO*(1-f_load))

        # interactive part
        prevfreq = freq
        freq = choose_freq(freq, cpuload, target_loads, freq_table)

        # let's go hispeed
        if cpuload >= go_hispeed:
            if prevfreq < hispeed_freq:
                freq = hispeed_freq
            else:
                freq = max(freq, hispeed_freq)

        # above hispeed delay limit
        if prevfreq < ABOVE_MIN:    cur_ahd = above_hispeed_delay[0]
        elif prevfreq < ABOVE_MAX:  cur_ahd = above_hispeed_delay[prevfreq - ABOVE_MIN]
        else:                       cur_ahd = above_hispeed_delay[8]
        if prevfreq >= hispeed_freq and freq > prevfreq and cycle_no-hispeed_validate_no < cur_ahd:
            freq = prevfreq
            continue

        hispeed_validate_no = cycle_no

        # keep boost, unless the boostpulse duration expires
        # oh fuck, this function is same to touchboost --yc 20180526
        # if freq < hispeed_freq and boostpulse_duration_counter > 0:
        #     freq = hispeed_freq

        # scaling down limit
        if freq < prevfreq and cycle_no-floor_validate_no < min_sampling_time:
            freq = prevfreq
            continue

        # even the freq doesn't change, another floor limit cycle will start
        floor_validate_no = cycle_no

    cycle_no = -1
    pool = 0
    freq = hispeed_freq
    hispeed_validate_no = 0
    floor_validate_no   = 0

    for i in idleload:
        cycle_no += 1
        pool += i                     # load can be add
        # pool = i                        # test for real task
        #miss decision
        cpuload = (pool//freq) + 1      # for fully usage of pool
        if cpuload > 100:
            cpuload = 100
        pool = pool - freq * cpuload
        if pool < 0:
            pool = 0
        # log every freq choices
        if diagnosis == 1:
            freq_choice.append(freq)

        # considering system bus comsumption
        if freq <= low_bus_freq:
            idle_powersum += power_table[freq - 1] * 0.3
        # elif freq > min_freq and freq <= 5:
        #     idle_powersum += power_table[freq - 1] * 0.6
        else:
            idle_powersum += power_table[freq - 1]

        # interactive part
        prevfreq = freq
        freq = choose_freq(freq, cpuload, target_loads, freq_table)

        # let's go hispeed
        if cpuload >= go_hispeed:
            if prevfreq < hispeed_freq:
                freq = hispeed_freq
            else:
                freq = max(freq, hispeed_freq)

        # above hispeed delay limit
        if prevfreq < ABOVE_MIN:    cur_ahd = above_hispeed_delay[0]
        elif prevfreq < ABOVE_MAX:  cur_ahd = above_hispeed_delay[prevfreq - ABOVE_MIN]
        else:                       cur_ahd = above_hispeed_delay[8]
        if prevfreq >= hispeed_freq and freq > prevfreq and cycle_no-hispeed_validate_no < cur_ahd:
            freq = prevfreq
            continue

        hispeed_validate_no = cycle_no

        # keep boost, unless the boostpulse duration expires
        # oh fuck, this function is same to touchboost --yc 20180526
        # if freq < hispeed_freq and boostpulse_duration_counter > 0:
        #     freq = hispeed_freq

        # scaling down limit
        if freq < prevfreq and cycle_no-floor_validate_no < min_sampling_time:
            freq = prevfreq
            continue

        # even the freq doesn't change, another floor limit cycle will start
        floor_validate_no = cycle_no
    
    # miss_2n_sum -= congestion
    # if miss_2n_sum < 0:
    #     miss_2n_sum = 0
    variance = math.sqrt(variance/float(len(workload)))

    # evaluate difference of distribution between congestion and required capacity
    cross_entropy = 0
    for x in range(20):
        p = 1-ap_env.ideal_freq_hist[x]
        q = (congestion_hist[x] + 1) / float(len(workload)+20)
        cross_entropy -= p * math.log(q, 2)
    # bigger the better
    demand_congestion_dist_diff = cross_entropy

    # TIC
    # tic_delta       = math.sqrt(variance / len(workload))
    # tic_predict     = math.sqrt(tic_pred_x2 / len(workload))
    # tic             = tic_delta / (tic_actual+tic_predict)

    period_lag_arr = sorted(period_lag_arr)
    min_period_lag = period_lag_arr[0]
    # max_period_lag = period_lag_arr[-1]
    # max_period_lag = period_lag_arr[-2]     # use 95 percent number
    max_period_lag = (period_lag_arr[-1] + period_lag_arr[-2])/2 # use 98 percent number
    avg_period_lag = sum(period_lag_arr)/float(len(period_lag_arr))
    range_period_lag = max_period_lag - min_period_lag
    median_period_lag = period_lag_arr[len(period_lag_arr)/2+1]
    l2_regularization = math.sqrt( sum([x*x for x in period_lag_arr]) )

    if mode == 'get_ref':
        miss_2n_sum = max(1, miss_2n_sum - stuck * feel[-1])
        ref_pkg = dict()
        ref_pkg['variance'] = float(variance)
        ref_pkg['miss_2n_sum'] = float(miss_2n_sum)
        ref_pkg['congestion'] = float(congestion)
        ref_pkg['square_error'] = float(square_error)
        ref_pkg['absolute_error'] = float(absolute_error)
        ref_pkg['max_period_lag'] = float(max_period_lag)
        ref_pkg['median_period_lag'] = float(median_period_lag)
        ref_pkg['l2_regularization'] = float(l2_regularization)
        ref_pkg['demand_congestion_dist_diff'] = float(demand_congestion_dist_diff)
        # ref_pkg[''] = float(tic)
        ref_pkg['powersum'] = float(powersum)
        ref_pkg['idle_powersum'] = float(idle_powersum)
        return  ref_pkg

    # RMSE MAE
    # rmse = math.sqrt(square_error/ap_env.ref_square_error)
    # mae  = absolute_error/ap_env.ref_absolute_error
    relative_variance = variance/ap_env.ref_variance

    rel_max_period_lag = max_period_lag / ap_env.ref_max_period_lag
    rel_median_period_lag = median_period_lag / ap_env.ref_median_period_lag
    rel_avg_period_lag = congestion / ap_env.ref_congestion
    # relative_period_lag = 0.4*rel_max_period_lag + 0.2*rel_avg_period_lag + 0.4*rel_median_period_lag
    # relative_period_lag = 0.2*rel_max_period_lag + 0.2*rel_avg_period_lag + 0.6*rel_median_period_lag
    relative_period_lag = l2_regularization / ap_env.ref_l2_regularization

    # ref_lasting
    onscreen_lasting = ap_env.ref_powersum / powersum
    idle_lasting = ap_env.ref_idle_powersum / idle_powersum
    # ref_lasting = onscreen_lasting
    # ref_lasting = 0.98*onscreen_lasting + 0.02*idle_lasting
    ref_lasting = 0.99*onscreen_lasting + 0.01*idle_lasting

    # ref_fitness
    tg_step         = count_tgloads_step(target_loads, freq_table)
    # relative_tic    = tic / ap_env.ref_tic
    # relative_step   = float(max(5.0, tg_step)) / max(5, ap_env.freq_step)  # steps less than 5 is unnecessary
    # ref_fitness     = 0.5*tic + 0.5*relative_step
    
    # ref_score
    relative_var        = variance / ap_env.ref_variance
    relative_miss_2n    = miss_2n_sum/ap_env.ref_miss_2n_sum
    relative_congestion = congestion/ap_env.ref_congestion
    relative_hist_diff  = demand_congestion_dist_diff / ap_env.ref_demand_congestion_dist_diff

    # ref_score           = 0.10*relative_miss_2n + 0.70*relative_congestion + 0.15*relative_tic + 0.02*relative_step
    # ref_score   = -0.03*relative_miss_2n - 0.20*relative_congestion + relative_hist_diff
    ref_score   = relative_period_lag 
    # ref_score   = relative_period_lag + 0.025*relative_step
    # ref_score   = relative_period_lag + 0.01*relative_step + 0.01*relative_miss_2n

    # user_score = 0.13*miss_2n_sum/ap_env.ref_miss_2n_sum + 0.85*congestion/ap_env.ref_congestion + 0.02*relative_var
    # user_score  = -0.03*relative_miss_2n - 0.20*relative_congestion + relative_hist_diff
    # user_score  = relative_period_lag + 0.015*relative_miss_2n+ 0.005*relative_step
    # user_score  = relative_period_lag + 0.015*relative_miss_2n
    user_score  = 0.98*relative_period_lag + 0.02*relative_variance

    if mode == 'test':
        # too lag, move to grave
        # waste power at standby, move to grave
        if ap_env.is_incubating == False and (
            user_score > USER_SCORE_CEILING \
            or ref_lasting < REF_LASTING_FLOOR \
            or relative_var > REF_VAR_CEILING \
            or relative_miss_2n > REF_2N_CEILING \
            or idle_lasting < IDLE_LASTING_FLOOR \
            or stuck > STUCK_LIMIT \
            or tg_step > TG_STEP_LIMIT \
        ):
            ref_score = 999
            relative_variance = 999
            ref_lasting = 0
        # return ref_score, onscreen_lasting, idle_lasting
        return ref_score, ref_lasting, relative_variance

    if mode == 'get_result':
        if user_score > USER_SCORE_CEILING \
        or ref_lasting < REF_LASTING_FLOOR \
        or relative_var > REF_VAR_CEILING \
        or relative_miss_2n > REF_2N_CEILING \
        or idle_lasting < IDLE_LASTING_FLOOR \
        or stuck > STUCK_LIMIT \
        or tg_step > TG_STEP_LIMIT: 
            return 0, 0, 0
        return user_score, onscreen_lasting, idle_lasting

    if mode == 'diagnosis':
        print ap_env.model_name
        print '\nvariance'
        print variance
        print '\nmiss_2n_sum'
        print miss_2n_sum
        print '\ncongestion'
        print congestion
        # print '\nmiss'
        # print miss
        print '\nstuck'
        print stuck
        # print '\nRMSE'
        # print rmse
        # print '\nMAE'
        # print mae
        print '\nmax_period_lag'
        print max_period_lag
        print '\nmedian_period_lag'
        print median_period_lag
        print '\nrelative_hist_diff'
        print relative_hist_diff
        # print '\nTIC'
        # print tic
        print '\nuser_score'
        print to_percent(user_score)
        print '\nref_score'
        print to_percent(ref_score)
        print '\nref_lasting'
        print to_percent(ref_lasting)
        print '\nonscreen_lasting'
        print to_percent(onscreen_lasting)
        print '\nidle_lasting'
        print to_percent(idle_lasting)
        # print '\nref_fitness'
        # print to_percent(ref_fitness)
        print ''
        print '----------------'
        print ''
        return freq_choice