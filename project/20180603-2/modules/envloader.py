#coding:utf-8

from array import array
import random
from interactive import *
from powermodel import *
from conf import *


class Simulation(object):
    def __init__(self, model_name, load_path, idle_path):
        self.model_name = model_name
        model = POWER_TABLE_DICT[model_name]
        self.relative_ipc = model['relative_ipc']
        self.min_freq = model['min_freq']
        self.max_freq = model['max_freq']
        self.freq_table = array('i', model['freq_table'])
        self.freq_step  = self.count_freq_step()
        self.base_power = POWER_TABLE_DICT['phone']
        self.idle_power = POWER_TABLE_DICT['idle']
        self.power_table = array('i', model['power_table'])
        self.enough_capacity = model['enough_capacity']
        # optimize for idle power & additional power leakage
        self.power_table[self.min_freq-1] = int(0.80 * self.power_table[self.min_freq-1])
        self.power_table[self.max_freq-1] = int(1.05 * self.power_table[self.max_freq-1])
        self.enough_capacity = model['enough_capacity']

        self.workload_filename = load_path
        self.idleload_filename = idle_path
        self.workload = self.workload_reader()
        self.workload_bak = tuple(self.workload_reader())
        self.idleload = self.idleload_reader()
        self.idleload_bak = tuple(self.idleload_reader())

        self.ideal_freq_choice = array('i')
        self.ideal_freq_hist = []
        self.ideal_powersum = 0
        self.ideal_idle_powersum = 0
        self.calculate_ideal_powersum()

        # self.tic_actual = self.set_tic()
        self.is_incubating = True

        self.set_ref_value()

    def count_freq_step(self):
        return len(set(self.freq_table))

    def set_tic(self):
        return math.sqrt(sum(x*x for x in self.ideal_freq_choice) / len(self.workload))

    def set_ref_value(self):
        ref_pkg = interactive_benchmark(DEFAULT_PARAM, self, mode='get_ref')
        self.ref_variance = ref_pkg['variance']
        self.ref_miss_2n_sum = ref_pkg['miss_2n_sum']
        self.ref_congestion = ref_pkg['congestion']
        self.ref_square_error = ref_pkg['square_error']
        self.ref_absolute_error = ref_pkg['absolute_error']
        self.ref_max_period_lag = ref_pkg['max_period_lag']
        self.ref_median_period_lag = ref_pkg['median_period_lag']
        self.ref_l2_regularization = ref_pkg['l2_regularization']
        self.ref_demand_congestion_dist_diff = ref_pkg['demand_congestion_dist_diff']
        # self.ref_tic = ref_pkg['tic']
        self.ref_powersum = ref_pkg['powersum']
        self.ref_idle_powersum = ref_pkg['idle_powersum']
        

    def workload_reader(self):
        workload = array('i')
        ipc = self.relative_ipc
        loads = open(self.workload_filename,'r')
        for usage in loads:
            i = int(round(float(usage) * 20.0 / ipc * PERSERVED_RATIO))
            # if ENABLE_ENOUGH_CAPACITY: i = min(i, self.enough_capacity)
            workload.append(i)
        loads.close()
        return workload

    def idleload_reader(self):
        idleload = array('i')
        ipc = self.relative_ipc
        loads = open(self.idleload_filename ,'r')
        for usage in loads:
            i = int(round(float(usage) * 20.0 / ipc * PERSERVED_RATIO))
            # if ENABLE_ENOUGH_CAPACITY: i = min(i, self.enough_capacity)
            idleload.append(i)
        loads.close()
        return idleload

    def workload_shuffle_noise(self, sigma):
        i = 0
        for b_load in self.workload_bak:
            t = b_load + random.gauss(0, sigma/self.relative_ipc)
            self.workload[i] = max(0, int(round(t)))
            i += 1
    def idleload_shuffle_noise(self, sigma):
        i = 0
        for b_load in self.idleload_bak:
            t = b_load + random.gauss(0, sigma/self.relative_ipc)
            self.idleload[i] = max(0, int(round(t)))
            i += 1

    def calculate_ideal_powersum(self):
        powersum = self.base_power * len(self.workload)
        idle_powersum = self.idle_power * len(self.idleload)
        min_freq = self.min_freq
        max_freq = self.max_freq
        low_bus_freq = self.freq_table[self.min_freq]
        freq_table = self.freq_table
        power_table = self.power_table
        ideal_freq_choice = self.ideal_freq_choice
        hist = [0]*20
        for i in self.workload:
            freq = i // 100 + 1
            freq = freq_to_table(freq, freq_table)
            ideal_freq_choice.append(freq)
            f_load = min((i//freq), 100.0) / 100.0
            powersum += power_table[freq - 1] * (f_load + IDLE_PWR_RATIO*(1-f_load))
            hist[freq-1] += 1
        for i in self.idleload:
            freq = i // 100 + 1
            freq = freq_to_table(freq, freq_table)
            ideal_freq_choice.append(freq)
            if freq <= low_bus_freq:
                idle_powersum += power_table[freq - 1] * 0.3
            else:
                idle_powersum += power_table[freq - 1]
        self.ideal_powersum = powersum
        self.ideal_idle_powersum = idle_powersum
        self.ideal_freq_hist = [float(x)/len(self.workload) for x in hist]
        return 0



# def self_loader(ap_name, load_path, idle_path):
#     self = Simulation(ap_name)
#     self.workload_filename = load_path
#     self.idleload_filename = idle_path
#     workload_reader(self)
#     idleload_reader(self)
#     calculate_ideal_powersum(self)
#     set_tic(self)
#     set_ref_value(self)
#     # self.ref_powersum = calculate_ref_powersum(WORKLOAD_FILE)
#     return self


