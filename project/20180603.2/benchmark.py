#coding:utf-8
from modules import *
import sys

def append(list_, name):
    list_.append((name, sys._getframe().f_back.f_locals[name]))

ap_env = Simulation('s821_b', WORKLOAD_FILE, STANDBY_FILE)

lazy = [1,1,1,1,2,2,2,1,1,
        2,80,6,2,
        85,85,85,85,85,85,85,85,85,85,85,85,90,90,90,90]


ref1104 = [1,1,1,1,1,1,1,1,1,1,
            1,1,1,1,1,10,10,20,20,1,
            1,97,14,1,
            95,95,95,2,2,44,44,52,52,84,
            84,82,82,97,97,98,98,96,96,90]

ref1104 = [1, 1, 1, 1, 1, 6, 1, 10, 8, 1, 1, 97, 14, 1, 95, 2, 44, 52, 84, 82, 97, 98, 97, 96]

balance1202 = [1, 1, 1, 1, 1, 2, 2, 5, 8, 1, 99, 12, 1, 64, 36, 11, 14, 79, 75, 87, 80, 49, 95, 68, 84, 92, 99, 99, 99]

stay_boost = [1, 1, 1, 1, 1, 1, 1, 1, 2, 233, 1, 15, 1, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 97]  
t0602_bal = [2, 2, 4, 4, 1, 1, 1, 5, 5, 2, 98, 14, 1, 80, 9, 26, 22, 54, 63, 66, 73, 76, 89, 94, 92, 98, 98, 97, 96]  
t0602_pwr = [3, 4, 5, 4, 1, 5, 3, 5, 5, 3, 98, 12, 1, 80, 22, 25, 48, 72, 75, 88, 89, 88, 98, 85, 85, 92, 98, 98, 98]  

compare_list = [
    'DEFAULT_PARAM',
    # 'lazy',
    # 'balance1202',
    'stay_boost',
    # 't0602_bal',
    # 't0602_pwr',
]

pending_list = list()
for x in compare_list:
    append(pending_list, x)

buf = [ap_env.ideal_freq_choice, ]
for name, param_sequence in pending_list:
    print name
    buf.append(interactive_benchmark(param_sequence, ap_env, mode='diagnosis'))

log_freq_compare(buf, ap_env)