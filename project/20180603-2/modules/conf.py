#coding:utf-8

# threads of pool.map
CPU_THREAD = 4

# use fixed random seed to produce repeatable results
# 2333 for test, 666666 for release
FIXED_SEED = 2333
# generation number
NGEN = 1200
# population number
MU = 1000
N_OFFSPRING = 1000
# interactive profile todo list
todolist = [
    's821_l',
    's821_b',
    'k950_l',
    'k950_b',
    'k960_l',
    'k960_b',
    'k970_l',
    'k970_b',
    's650_l',
    's650_b',
    's625_uni',
    's835_l',
    's835_b',
    's660_l',
    's660_b',
    #######
    's636_l',
    's636_b',
    's801_uni',
    's810_l',
    's810_b',
    'e8895_l',
    'e8895_b',
    'e8890_l',
    'e8890_b',
    'e7420_l',
    'e7420_b',
    'z3560_uni',
    'mt6797_uni',
    'mt6795_uni',
]

# interactive parameters have 9+16+4 dimensions
NDIM = 29-5
# crossover possibility
# https://github.com/amirmasoudabdol/nsga2/search?utf8=%E2%9C%93&q=eta_&type=
# 0.6-1.0
CXPB = 0.90
# https://github.com/amirmasoudabdol/nsga2/search?utf8=%E2%9C%93&q=eta&type=
# Enter the value of distribution index for crossover (5-20)
# default eta is 20-20
ETA_MATE = 5.0
ETA_MUTATE = 5.0

# workload preprocessing
PERSERVED_RATIO = 1.00
WORKLOAD_SIGMA = 0
IDLELOAD_SIGMA = 0

# interactive simulator parameters
ENABLE_ENOUGH_CAPACITY = 1
CONGEST_LOAD = 99
PRESERVED_CAPACITY = 50
# cpu idle support
# IDLE_PWR_RATIO = 0.80   # 20180330 v3
# IDLE_PWR_RATIO = 0.20   # 20180509 v1
IDLE_PWR_RATIO = 0.10   # 20180509 v2
# IDLE_PWR_RATIO = 0.01   # 20180528
# IDLE_PWR_RATIO = 0.50   # 20180529
# what is too bad
REF_SCORE_CEILING = 0.90
USER_SCORE_CEILING = 1.30
REF_LASTING_FLOOR = 0.90
# REF_LASTING_FLOOR = 0.60    # nolimit
IDLE_LASTING_FLOOR = 1.00
# IDLE_LASTING_FLOOR = 0.20   # nolimit
# REF_VAR_CEILING = 1.50
# REF_2N_CEILING = 2.00
REF_VAR_CEILING = 1.30
REF_2N_CEILING = 99.00
STUCK_LIMIT = 20
TG_STEP_LIMIT = 10
EXIT_INCUBATION_NGEN = 3
# 必须能整除训练序列长度
PERIOD_LEN = 200
# PERIOD_LEN = 500

# parameter value range
# min <= x <= max
above_i = (1, 5)
boostpulse_i = (1, 4)
go_i = (80, 98)
# go_i = (2, 98)  # nolimit
hispeed_i = (8, 16)
min_i = (1, 4)
loads_i = (2, 98)
INIT_RANDOM = True

# input settings
WORKLOAD_DIR = './workload_model/'
# WORKLOAD_FILE = 'Trepn_workload.csv'
# WORKLOAD_FILE = 'Trepn_workload_20171022.csv'   # 斗鱼 30% + bilibili 20% + 启动和滑屏30% + 阅读 20%
# WORKLOAD_FILE = 'Trepn_workload_20171031.csv'   # 斗鱼 1min + bilibili danmu 2min + 启动和滑屏 3min + 阅读 2min
WORKLOAD_FILE = 'Trepn_workload_20180529_mixed.csv' # 由上面三者混合而来
# WORKLOAD_FILE = 'cust-top-20171025-40ms.csv'    # 自定义C代码采集，数据源/proc/stat，40ms间隔，斗鱼 1min + mxplayer 1min + coolapk,zhihu 3min + bilibili danmu 2min + bilibili scroll 1min
# WORKLOAD_FILE = 'custv2-20171124-20ms-6000.csv'   # 20ms采样，1min 酷安头条，0.5min兴趣圈， 0.5min idle
WORKLOAD_FILE = WORKLOAD_DIR + WORKLOAD_FILE
# STANDBY_FILE = WORKLOAD_DIR + 'standby_load_20180308_from_171023.csv'
STANDBY_FILE = WORKLOAD_DIR + 'Trepn_workload_mixed_0v0_standby.csv'
TEST_FILE = WORKLOAD_DIR + 'Trepn_workload_20171023.csv'
# TEST_FILE = WORKLOAD_DIR + 'Trepn_workload_geekbench4_battery.csv'  # 多任务切换1次 + geekbench4 电池测试 1min + 截图1次 + 多任务切换1次

# output settings
CSV_DIR = './csv/'
SHELL_BASE_DIR = './shell/'

# PERF_SCORE = 50
# BALANCED_SCORE = 85
# POWERSAVE_SCORE = 100
# perf_condition = lambda x: x < PERF_SCORE
# bala_condition = lambda x: x < BALANCED_SCORE
# save_condition = lambda x: x < POWERSAVE_SCORE
PERF_SCORE = 60
BALANCED_SCORE = 85
POWERSAVE_SCORE = 115
is_PERFORMANCE = lambda x: x < PERF_SCORE
is_BALANCE = lambda x: x < BALANCED_SCORE
is_POWERSAVE = lambda x: x < POWERSAVE_SCORE

# 16-8+1 = 9
ABOVE_LEVELS = 9
ABOVE_MIN = 8
ABOVE_MAX = 16
# 18-3+1 = 16
TARGETLOADS_LEVELS = 16
TGLOADS_MIN = 3
TGLOADS_MAX = 18
TGLOADS_FIRST = 80      # 0 to turn off
TGLOADS_SAME_THRESHOLD = 3

# up and down limit in NGSA2
low_up = tuple(zip(  
            above_i, above_i, above_i, above_i, above_i, 
            above_i, above_i, above_i, above_i,  
            boostpulse_i, go_i, hispeed_i, min_i, 
            loads_i, loads_i, loads_i, loads_i, loads_i, 
            loads_i, loads_i, loads_i, loads_i, loads_i,
            loads_i, loads_i, loads_i, loads_i, loads_i, 
            loads_i, 
            ))
low = low_up[0]
up = low_up[1]

DEFAULT_PARAM =[1,1,1,1,1,1,1,2,2,
                4,90,12,2,
                85,85,85,85,85,85,85,85,85,85,85,85,90,90,90,90]
# DEFAULT_PARAM =[1,1,1,1,2,2,1,1,1,
#                 4,90,12,2,
#                 85,85,85,85,85,85,85,85,85,85,85,85,90,90,90,90]
