# Project WIPE

Workload-based Interactive Parameter Explorer  
20180603 均衡(适用于 EX Kernel Manager/ Kernel Aduitor)   

## 支持如下SOC

Snapdragon 835, 820/821, 810/808, 801/800/805, 660, 636, 652/650, 625/626  
Exynos 8895, 8890, 7420  
Kirin 970, 960, 950/955  
Helio X20/X25, X10  
Atom z3560/z3580  

## 警告(Warning)

勿作商业用途，禁止转载内容和内嵌参数  
Do not use for commercial purposes, prohibit reproducing content and embedding parameters in custom ROM and kernel  
酷安ID：@yc9559  

## 结束语

在这上面耗费的时间太多，是时候结束这个项目了。  

这个项目从去年[7月][1]开始，但是直到9月效果都是存在严重问题的。[10月份][2]我重启了这个项目，完善参数支持后做出了[1104版][3]，进一步细化打磨后做出了[1202版][4]。本来打算到此结束，因为已经证明了计算科学在这个目标上的可行性和效果，下一代EAS将在主流平台实装，但是有人希望我继续做下去。随后[今年1月][5]尝试了一段时间的HMP分支，结果是仿真逻辑与实际代码效果相差太多走了弯路。从[3月][6]开始终止HMP分支，并且合并一些来自HMP分支的新特性到1202版，但是再次陷入卡顿代价函数模型与实际体验对不上的问题。或许是巧合，或许是内测同志的高质量反馈，在4月底找到了一个比较合适的函数组合，于是有了赶鸭子上架的[180509生日版][7]，以及进一步小改流畅度的180526版。然而180526版本没能发出来，因为发现了一直以来严重的失误，本来可以养老去了但还是把所有不符合的逻辑全改了，得到180603版。这一路上效果的进步，离不开在酷安网积极反馈高质量体验的同志。  

在结果上，我还是可以吹点牛皮的。一台笔记本电脑，一台非主流的Nexus 9和噪音高的不得了的讨论社区，如何做出覆盖所有主流平台、解决玄学参数回馈、质量可控的参数组合的？通过代码实现它，替代人调整参数，像一个工厂，效果可控可复现，是这个项目的目标。做出来的参数能够适应各类场景，而不是仅仅适用于某种游戏或日常应用。兼顾平滑度和能耗，虽然性能和能耗是矛盾的，存在着省电就是卡顿的偏见，但是总有相同能耗下更加平滑的参数组合，也总有相同平滑性能表现下更加节能的参数组合。不过做到最后，似乎只是卡在了一个合适的位置，谈不上是最佳方案，也比不上EAS带来的变革效果。所以可以解释，为什么不做刷机包，为什么不帮帮萌新一步步教学，为什么DEV版本参数做崩了被喷还能继续做下去，因为我不太在意这些。  

在酷安有8k+的粉丝，这可以说是意外的收获了。一开始我也是默默下载软件的潜水员，在 Kernel Auditor 讨论区发布[第一篇心得帖子][8]得到了零星的关注，这样子一点点开始。与绝大多数的公众号不同，在一个不常用软件的讨论区发一些技术性文章，最后能做成这样也是挺神奇的了。大家比较熟悉的是参数帖子，其实教程帖子也挺有意思的。  

其实还是有些后悔做了这个项目，这么长的时间足以从一个萌新变成小半个热门领域的专家，而我错失了这个机会。  

至此，给这个项目画个句号。当然在酷安的交流还是会继续的 :)  

![实际上有40%的回复数是我的](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/coolapk-trend-180602.png)

## 有啥不同

- 基于 Project WIPE 20180509
- **interactive仿真器逻辑修正，包含对所有参数的理解更正**
- 性能代价函数1，使用分区带连续卡顿检测的混合计数的L2正则，对异常值敏感
- 性能代价函数2，使用频率选择合页标准差，对性能释放不及时敏感
- 代价函数加入连续卡顿评价的约束，以及排除对应的归一化分母中过大的卡顿
- 以上调整带来显著更宽的参数效果范围
- 调整`hispeed_freq`的取值范围
- `target_loads`参数长度硬限制为10，降低过拟合可能
- 混合负载模型，高变化负载场景占比更多，负载状态转移情况更加充实
- 启发式优化器迭代参数调整，改善一点搜索效率
- 脚本模板加入调试信息接口
- S801脚本模板考虑aSMP特性，S810/808脚本模板最高频率一致化
- Kirin 950/955 最低频假设修复
- 减小频率动态锁的限制，标准化不同最大频率下的动态锁
- cpuset的限制调整，避免任务强制在核心迁移引入卡顿
- 增加一点低延迟模式的频率限制
- 平台从微工具箱切换到 Tasker，保持对微工具箱的兼容，实现目前最佳的调整和事件自由度
- 支持 Kernel Auditor 的模拟init.d

## 对比

![与高通默认参数对比](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/20180603.png)

## 操作指南

1. 老司机不需要指南
2. 卡顿版，费电版的参数可以在原帖的性能配置里找到

## 传送门

使用脚本执行： <https://github.com/yc9559/cpufreq-interactive-opt/blob/master/20180603-description.md>  

Disscussion & Testing in Coolapk：<https://www.coolapk.com/feed/6757382>  

## FAQ

1. 开机后CPU运行频率很高

    > 即使不执行脚本，开机后的3-10分钟负载也是很高的

2. 开机后半小时以上，CPU很难落到最低频率

    > 在部分机型上，由于微工具箱导致的问题，卸载重启后使用Tasker执行问题解决
    > 观察到负载不低，可能是 Kernel Auditor 或者其他在后台占用CPU资源

3. 待机太耗电

    > 如果待机耗电在1%/h以内，认为是正常表现
    > 使用 Wakelock Detector 检查占用唤醒锁时间最长的程序，深度睡眠时间应该>95%

4. 游戏还是一样卡

    > 如果CPU占用率高于90%但是CPU运行频率在1.2g左右，需要解除温控
    > 切换到低延迟模式运行游戏，问题依旧说明CPU最大性能不足或者当前游戏版本优化不足

5. 用起来好麻烦

    > 那就不要用了

## 目录

- [Snapdragon 835](#snapdragon-835)
- [Snapdragon 820 821](#snapdragon-820-821)
- [Snapdragon 810 808](#snapdragon-810-808)
- [Snapdragon 801 800 805](#snapdragon-801-800-805)
- [Snapdragon 660](#snapdragon-660)
- [Snapdragon 636](#snapdragon-636)
- [Snapdragon 652 650](#snapdragon-652-650)
- [Snapdragon 625 626](#snapdragon-625-626)
- [Exynos 8895](#exynos-8895)
- [Exynos 8890](#exynos-8890)
- [Exynos 7420](#exynos-7420)
- [Kirin 970](#kirin-970)
- [Kirin 960](#kirin-960)
- [Kirin 950 955](#kirin-950-955)
- [Helio X20 X25](#helio-x20-x25)
- [Helio X10](#helio-x10)
- [Atom z3560 z3580](#atom-z3560-z3580)

### 公共的部分

interactive
```
timer_rate: 20000
timer_slack: 180000
boostpulse_duration: 0
max_freq_hysteresis: 38000
enable_prediction: 0
io_is_busy: 无所谓是多少
ignore_hispeed_on_notif: 0
use_sched_load: 1
use_migration_notif: 1
```

HMP
```
sched_freq_aggregate: 0
sched_spill_load: 90
sched_prefer_sync_wakee_to_waker: 1
```

IO
```
scheduler: CFQ
read_ahead_kb: 512
nr_requests: 256
slice_idle： 0
```

### Snapdragon 835

小核最低频率设置为3xx Mhz  
大核最低频率设置为3xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.11  
_相对亮屏续航百分比_  
102.74  
above_hispeed_delay:  
18000 1580000:98000  
go_hispeed_load:  
98  
hispeed_freq:  
1180000  
min_sample_time:  
18000  
target_loads:  
80 380000:30 480000:41 580000:29 680000:4 780000:60 1180000:88 1280000:70 1380000:78 1480000:97  

大核心：  
_相对感知卡顿百分比_  
84.82  
_相对亮屏续航百分比_  
103.40  
above_hispeed_delay:  
18000 1380000:78000 1480000:18000 1580000:98000 1880000:138000  
go_hispeed_load:  
98  
hispeed_freq:  
1280000  
min_sample_time:  
18000  
target_loads:  
80 380000:39 580000:58 780000:63 980000:81 1080000:92 1180000:77 1280000:98 1380000:86 1580000:98  

### Snapdragon 820 821

小核最低频率设置为3xx Mhz  
大核最低频率设置为3xx Mhz  

小核心：  
_相对感知卡顿百分比_  
83.77  
_相对亮屏续航百分比_  
112.48  
above_hispeed_delay:  
58000 1280000:98000 1580000:58000  
go_hispeed_load:  
98  
hispeed_freq:  
1180000  
min_sample_time:  
18000  
target_loads:  
80 380000:9 580000:36 780000:62 880000:71 980000:87 1080000:75 1180000:98  

大核心：  
_相对感知卡顿百分比_  
84.90  
_相对亮屏续航百分比_  
107.65  
above_hispeed_delay:  
38000 1480000:98000 1880000:138000  
go_hispeed_load:  
98  
hispeed_freq:  
1380000  
min_sample_time:  
18000  
target_loads:  
80 380000:39 480000:35 680000:29 780000:63 880000:71 1180000:91 1380000:83 1480000:98  

### Snapdragon 810 808

小核最低频率设置为3xx Mhz  
大核最低频率设置为3xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.51  
_相对亮屏续航百分比_  
104.21  
above_hispeed_delay:  
98000 1280000:38000  
go_hispeed_load:  
95  
hispeed_freq:  
1180000  
min_sample_time:  
38000  
target_loads:  
80 580000:62 680000:28 780000:66 880000:90 1180000:98  

大核心：  
_相对感知卡顿百分比_  
83.98  
_相对亮屏续航百分比_  
108.79  
above_hispeed_delay:  
18000 1180000:98000 1380000:18000  
go_hispeed_load:  
97  
hispeed_freq:  
880000  
min_sample_time:  
58000  
target_loads:  
80 480000:44 580000:61 780000:22 880000:94 1180000:98  

### Snapdragon 801 800 805

最低频率设置为3xx Mhz  

不区分大小核心：  
_相对感知卡顿百分比_  
84.80  
_相对亮屏续航百分比_  
103.21  
above_hispeed_delay:  
18000 1480000:38000 1680000:98000 1880000:138000  
go_hispeed_load:  
92  
hispeed_freq:  
1180000  
min_sample_time:  
18000  
target_loads:  
80 380000:18 580000:40 880000:34 980000:66 1180000:84 1680000:98  

### Snapdragon 660

小核最低频率设置为6xx Mhz  
大核最低频率设置为11xx Mhz  

小核心：  
83.85  
_相对亮屏续航百分比_  
103.75  
above_hispeed_delay:  
98000  
go_hispeed_load:  
98  
hispeed_freq:  
1480000  
min_sample_time:  
38000  
target_loads:  
80 880000:59 1080000:90 1380000:78 1480000:98  

大核心：  
_相对感知卡顿百分比_  
84.73  
_相对亮屏续航百分比_  
101.77  
above_hispeed_delay:  
18000 1680000:98000 1880000:138000  
go_hispeed_load:  
83  
hispeed_freq:  
1080000  
min_sample_time:  
18000  
target_loads:  
80 1380000:70 1680000:98  

### Snapdragon 636

小核最低频率设置为6xx Mhz  
大核最低频率设置为11xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.20  
_相对亮屏续航百分比_  
101.81  
above_hispeed_delay:  
18000 1380000:98000 1580000:18000  
go_hispeed_load:  
97  
hispeed_freq:  
1080000  
min_sample_time:  
58000  
target_loads:  
80 880000:62 1080000:92 1380000:77 1480000:98  

大核心：  
_相对感知卡顿百分比_  
84.94  
_相对亮屏续航百分比_  
100.77  
above_hispeed_delay:  
18000 1680000:98000  
go_hispeed_load:  
81  
hispeed_freq:  
1080000  
min_sample_time:  
18000  
target_loads:  
80 1380000:70 1680000:98  

### Snapdragon 652 650

小核最低频率设置为4xx Mhz  
大核最低频率设置为4xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.96  
_相对亮屏续航百分比_  
101.23  
above_hispeed_delay:  
98000 1380000:58000  
go_hispeed_load:  
97  
hispeed_freq:  
1180000  
min_sample_time:  
58000  
target_loads:  
80 680000:68 780000:60 980000:97 1180000:63 1280000:97 1380000:84  

大核心：  
_相对感知卡顿百分比_  
84.67  
_相对亮屏续航百分比_  
102.87  
above_hispeed_delay:  
18000 1580000:98000  
go_hispeed_load:  
98  
hispeed_freq:  
1280000  
min_sample_time:  
18000  
target_loads:  
80 880000:47 980000:68 1280000:74 1380000:92 1580000:98  

### Snapdragon 625 626

小核最低频率设置为6xx Mhz  
大核最低频率设置为6xx Mhz  

不区分大小核心：  
_相对感知卡顿百分比_  
84.32  
_相对亮屏续航百分比_  
102.69  
above_hispeed_delay:  
98000 1880000:138000  
go_hispeed_load:  
97  
hispeed_freq:  
1680000  
min_sample_time:  
18000  
target_loads:  
80 980000:63 1380000:72 1680000:97  

### Exynos 8895

小核最低频率设置为4xx Mhz  
大核最低频率设置为7xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.70  
_相对亮屏续航百分比_  
102.65  
above_hispeed_delay:  
38000 1380000:98000  
go_hispeed_load:  
97  
hispeed_freq:  
1180000  
min_sample_time:  
58000  
target_loads:  
80 780000:54 880000:66 980000:39 1180000:71 1380000:97  

大核心：  
_相对感知卡顿百分比_  
84.83  
_相对亮屏续航百分比_  
101.03  
above_hispeed_delay:  
18000 1680000:98000 1880000:138000  
go_hispeed_load:  
95  
hispeed_freq:  
1380000  
min_sample_time:  
18000  
target_loads:  
80 780000:38 880000:12 980000:47 1080000:66 1180000:73 1380000:89 1680000:98  

### Exynos 8890

小核最低频率设置为4xx Mhz  
大核最低频率设置为7xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.75  
_相对亮屏续航百分比_  
102.24  
above_hispeed_delay:  
18000 1480000:98000 1580000:78000  
go_hispeed_load:  
98  
hispeed_freq:  
1180000  
min_sample_time:  
18000  
target_loads:  
80 480000:51 680000:38 780000:62 880000:37 980000:63 1080000:69 1180000:93 1280000:87 1480000:98  

大核心：  
_相对感知卡顿百分比_  
84.08  
_相对亮屏续航百分比_  
102.02  
above_hispeed_delay:  
18000 1580000:98000 1880000:138000  
go_hispeed_load:  
98  
hispeed_freq:  
1480000  
min_sample_time:  
18000  
target_loads:  
80 780000:29 880000:68 980000:12 1080000:84 1180000:68 1280000:93 1380000:77 1480000:98  

### Exynos 7420

小核最低频率设置为4xx Mhz  
大核最低频率设置为8xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.08  
_相对亮屏续航百分比_  
101.36  
above_hispeed_delay:  
38000 1380000:98000 1480000:18000  
go_hispeed_load:  
95  
hispeed_freq:  
1180000  
min_sample_time:  
38000  
target_loads:  
80 480000:26 680000:69 780000:59 880000:27 980000:18 1080000:76 1180000:89 1280000:83 1480000:70  

大核心：  
_相对感知卡顿百分比_  
84.72  
_相对亮屏续航百分比_  
103.82  
above_hispeed_delay:  
18000 1580000:98000 1880000:138000  
go_hispeed_load:  
93  
hispeed_freq:  
1380000  
min_sample_time:  
18000  
target_loads:  
80 880000:22 980000:57 1080000:34 1180000:75 1480000:87 1580000:97  

### Kirin 970

小核最低频率设置为5xx Mhz  
大核最低频率设置为6xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.70  
_相对亮屏续航百分比_  
99.60  
above_hispeed_delay:  
18000 1480000:38000 1680000:98000  
go_hispeed_load:  
97  
hispeed_freq:  
1180000  
min_sample_time:  
38000  
target_loads:  
80 980000:61 1180000:88 1380000:70 1480000:96  

大核心：  
_相对感知卡顿百分比_  
83.77  
_相对亮屏续航百分比_  
102.75  
above_hispeed_delay:  
18000 1580000:98000 1780000:138000  
go_hispeed_load:  
94  
hispeed_freq:  
1280000  
min_sample_time:  
18000  
target_loads:  
80 980000:72 1280000:77 1580000:98  

### Kirin 960

小核最低频率设置为5xx Mhz  
大核最低频率设置为9xx Mhz  

小核心：  
_相对感知卡顿百分比_  
82.62  
_相对亮屏续航百分比_  
99.09  
above_hispeed_delay:  
38000 1680000:98000  
go_hispeed_load:  
97  
hispeed_freq:  
1380000  
min_sample_time:  
78000  
target_loads:  
80 980000:97 1380000:78 1680000:98  

大核心：  
_相对感知卡顿百分比_  
84.94  
_相对亮屏续航百分比_  
98.15  
above_hispeed_delay:  
18000 1380000:98000 1780000:138000  
go_hispeed_load:  
95  
hispeed_freq:  
880000  
min_sample_time:  
38000  
target_loads:  
80 1380000:59 1780000:98  

### Kirin 950 955

小核最低频率设置为4xx Mhz  
大核最低频率设置为4xx Mhz  

小核心：  
_相对感知卡顿百分比_  
84.56  
_相对亮屏续航百分比_  
100.33  
above_hispeed_delay:  
18000 1480000:98000  
go_hispeed_load:  
97  
hispeed_freq:  
1280000  
min_sample_time:  
58000  
target_loads:  
80 780000:69 980000:76 1280000:80 1480000:96  

大核心：  
_相对感知卡顿百分比_  
84.76  
_相对亮屏续航百分比_  
99.19  
above_hispeed_delay:  
18000 1780000:138000  
go_hispeed_load:  
80  
hispeed_freq:  
1180000  
min_sample_time:  
38000  
target_loads:  
80 1180000:75 1480000:93 1780000:98  

### Helio X20 X25

最低频率使用默认值  

不区分大小核心：  
_相对感知卡顿百分比_  
84.95  
_相对亮屏续航百分比_  
107.76  
above_hispeed_delay:  
98000  
go_hispeed_load:  
97  
hispeed_freq:  
1380000  
min_sample_time:  
18000  
target_loads:  
80 380000:34 680000:21 780000:72 880000:10 980000:42 1080000:62 1180000:88 1380000:93 1480000:98  

### Helio X10

最低频率使用默认值  

不区分大小核心：  
_相对感知卡顿百分比_  
84.97  
_相对亮屏续航百分比_  
107.74  
above_hispeed_delay:  
18000 1280000:38000 1480000:98000  
go_hispeed_load:  
95  
hispeed_freq:  
1180000  
min_sample_time:  
38000  
target_loads:  
80 780000:63 1180000:93 1280000:75 1480000:98  

### Atom z3560 z3580

最低频率设置为5xx Mhz  

不区分大小核心：  
_相对感知卡顿百分比_  
84.96  
_相对亮屏续航百分比_  
108.32  
above_hispeed_delay:  
18000 1480000:78000 1580000:98000  
go_hispeed_load:  
98  
hispeed_freq:  
1380000  
min_sample_time:  
18000  
target_loads:  
80 580000:55 680000:42 780000:56 880000:39 980000:61 1180000:67 1480000:96  

## Credit

[Distributed Evolutionary Algorithms in Python](https://github.com/DEAP/deap)  
@ft1858336  跟他交流意识到从201710开始一直存在的仿真逻辑和interactive的不一致，直接导致了180526版没有发出来  
@Yoooooo    瞬时性能意见，比如MIUI多任务切换，性能释放合页标准差，测试S835的参数，跟上了日更的节奏  
@僞裝灬     测试S821的参数，基本跟上了日更的节奏   
@xujiyuan723测试S808的参数，启发统一S810/808最高频率  
@HELISIGN   测试S821的参数，启发above_hispeed_delay改进  
@揪你鸡儿   测试S808的参数  
@zqyhqw     提供借助install-recovery.sh执行脚本的方法    
@HHHGTTT    提供Exynos HMP和热插拔修改的点子  
@嘟嘟斯基   参考了他的Exynos的shell脚本  

## 捐赠

并不在乎捐赠的这点钱，之后也不会有更新，如果你实在愿意，下面是感谢~~云讨饭~~通道：  

![支付宝捐赠QR](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/alipay-qr.png)

[1]: https://www.coolapk.com/feed/3712488
[2]: https://www.coolapk.com/feed/4355087
[3]: https://www.coolapk.com/feed/4570875
[4]: https://www.coolapk.com/feed/4796254
[5]: https://www.coolapk.com/feed/5328381
[6]: https://www.coolapk.com/feed/5838948
[7]: https://www.coolapk.com/feed/6440134
[8]: https://www.coolapk.com/feed/2278724