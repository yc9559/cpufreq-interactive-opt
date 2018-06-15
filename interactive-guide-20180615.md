# interactive从入门到精（fang）通（qi）

v20180615

> 警告：
> 仅供酷安平台交流，勿作商业用途，禁止转载
> 如果是想深入了解interactive是如何决策的，一定看得懂
> 酷安ID：@yc9559

## 【 学习之前需要了解的 】

1. 对interactive参数有感性了解，比如知道修改`go_hispeed_load`对应的效果
2. 接触过任意一门编程语言，不理解`if`和赋值会严重影响阅读
3. 没有对于英语能力的要求，绝大多数的含义已用中文写成

## 【 是什么 】

众所周知现在手机SOC性能都是过剩的，但是卡顿仍然是甩不掉的困惑，这种情况我们归于优化不好。
性能优化包含很多方面，比如LMK、调度器，CPU调速器（CPU Governor）就是其中一个卡顿之源。
它控制什么时候释放多少性能，什么时候需要提升频率，什么时候需要降低频率。
interactive是一个基于采样的CPU频率调节器，采集上一周期的CPU工作时间，决定下一周期CPU的工作主频。

## 【 背景知识 】

1. 与频率监视器(如Perfmon)看到的不同，实际负载波动非常大，这也是卡顿和费电的来源
2. interactive存在响应速度慢(至少20ms)，历史数据窗口小的问题(历史数据窗口数=1)
3. CPU功耗曲线是近似指数函数的，超过一定频率功耗会飙升，意味着越往高频，性能收益远小于功耗带来的代价
4. HMP是任务调度器，不是某种文明用语
5. 使用HMP调度器之后，它拥有每个任务5个(默认)历史数据窗口的负载信息，由它提供负载信息给CPU调速器
6. 由于同个簇内的核心负载不可能完全相等，簇内核心频率一致，interactive取簇内核心的负载最大值

## 【 为什么写这篇 】

其实上一版20171208已经说得比较详细，但是上一版仍然存在不少逻辑错误，然而这些错误直到20180526才意识到。  
了解一个系统如何工作的最佳方式，仍然是"Read the Fxxking code"，因为这才是第一手资料。  
阅读源码可以解答参数在interactive决策中起到的作用，然而阅读源码比较高的门槛把很多有兴趣的人挡在了外面。  
这一版会写的尽可能直白、简化，以及给出明确的频率选择逻辑，方便深入阅读源码。  
本版本使用伪代码的形式，略去实际代码的大量细节实现，保留了核心逻辑过程。  

## 【 伪代码流程 】

```python
我们先声明有下面这些功能块，先不管功能块里面是什么，但是应该有如下功能：

当前CPU频率, 当前CPU占用率 -> cpufreq_interactive_timer -> 下一CPU频率
当前CPU频率, 当前CPU占用率 -> choose_freq               -> 根据target_loads选择的频率
CPU频率 -> freq_to_above_hispeed_delay -> 这个CPU频率对应的above_hispeed_delay
CPU频率 -> freq_to_targetload          -> 这个CPU频率对应的target_loads
```

```python
freq_to_above_hispeed_delay(CPU频率)
{

# 比如"19000 1500000:39000 1800000:79000"
if CPU频率 < 1500000:
    return 19000      # 如果执行到这一行，直接结束该功能块，不再往下执行
if CPU频率 < 1800000:
    return 39000      # 如果执行到这一行，直接结束该功能块，不再往下执行
return 79000          # 如果上面都不匹配

}

freq_to_targetload(CPU频率)
{
跟上面同一个模式
}
```

```python
# CPU处于正常工作时，这个功能块每过 timer_rate 执行一次
# CPU处于待机状态时，这个功能块每过 timer_rate + timer_slack 执行一次(比如关闭屏幕的时候)
# 如果使用了高通HMP，use_sched_load=1时，当前CPU占用率由调度器提供，否则使用传统的忙闲统计
# 如果io_is_busy=1，等待IO的时间也会算在CPU工作时间里(此时CPU处于等待空闲状态)
# 如果 当前需要的性能 - 当前提供的性能 > sched_freq_inc_notify，则notif_pending=1，否则notif_pending=0
# 如果 当前需要的性能 - 当前提供的性能 < sched_freq_dec_notify，则notif_pending=1，否则notif_pending=0
cpufreq_interactive_timer(当前CPU频率, 当前CPU占用率)
{

是否收到调度器通知  = use_sched_load == 1 and use_migration_notif == 1 and notif_pending == 1 
是否跳过hispeed逻辑 = 是否收到调度器通知 and ignore_hispeed_on_notif == 1
是否跳过降频逻辑    = 是否收到调度器通知 and fast_ramp_down == 1

下一CPU频率 = choose_freq(当前CPU频率, 当前CPU占用率)
if  use_sched_load == 1 and use_migration_notif == 1 and enable_prediction == 1:
    瞎蒙的下一CPU频率 = choose_freq(当前CPU频率, 瞎蒙的下一CPU占用率)
    下一CPU频率 = 取最大(下一CPU频率, 瞎蒙的下一CPU频率)

if 是否跳过hispeed逻辑 == False:
    if 当前CPU占用率 >= go_hispeed_load:
        if 当前CPU频率 < hispeed_freq:
            下一CPU频率 = hispeed_freq
        else:
            下一CPU频率 = 取最大(hispeed_freq, 下一CPU频率)
下一CPU频率 = 在频率表选一个大于等于它的频率里最小的(下一CPU频率)

above_hispeed_delay = freq_to_above_hispeed_delay(当前CPU频率)

if 是否跳过hispeed逻辑 == False:
    if 当前CPU频率 >= hispeed_freq and 下一CPU频率 > 当前CPU频率:
        if 当前时刻 - 上次hispeed状态允许提升频率的时刻 < above_hispeed_delay:
            下一CPU频率 = 当前CPU频率
            return 下一CPU频率      # 如果执行到这一行，直接结束该功能块，不再往下执行

上次hispeed状态允许提升频率的时刻 = 当前时刻

if 是否跳过降频逻辑 == False:
    if 下一CPU频率 < 当前CPU频率 and 当前时刻 - 上次允许降频的时刻 < min_sampling_time:
        下一CPU频率 = 当前CPU频率
        return 下一CPU频率      # 如果执行到这一行，直接结束该功能块，不再往下执行

上次允许降频的时刻 = 当前时刻

return 下一CPU频率

}
```

```python
# 由于“这次”与“上次”的视觉区分度低，用 prev_freq 代替 上次，用 freq 代替 这次
choose_freq(当前CPU频率, 当前CPU占用率)
{

下边界频率 = 0
上边界频率 = 999999999
当前负载 = 当前CPU频率 * 当前CPU占用率
prev_freq = 当前CPU频率
freq = 当前CPU频率

这是循环的头
{
    prev_freq = freq
    freq对应的targetload = freq_to_targetload(freq)
    freq = 在频率表选一个比它大的频率里最小的(当前负载 / freq对应的targetload)

    if freq > prev_freq:
        下边界频率 = prev_freq
        if freq >= 上边界频率:
            freq = 上边界频率 - 1
            freq = 在频率表选一个小于等于它的频率里最大的(freq)
            if freq == 下边界频率:
                freq = 上边界频率
                break   # 跳出这个循环，去循环的尾
    elif freq < prev_freq:
        上边界频率 = prev_freq
        if freq <= 下边界频率:
            freq = 下边界频率 + 1
            freq = 在频率表选一个大于等于它的频率里最小的(freq)
            if freq == 上边界频率:
                break   # 跳出这个循环，去循环的尾
    if prev_freq == freq:
        break   # 跳出这个循环，去循环的尾巴
}
这是循环的尾

return freq

}
```

## 【 让我们实际跑一跑 】

```python
使用的interactive参数：
timer_rate: 20000
above_hispeed_delay:  "38000 1480:98000 1680:138000"  
go_hispeed_load:  98  
hispeed_freq:  1380  
min_sample_time:  18000  
target_loads:  "80 380:39 480:35 680:29 780:63 880:71 1180:91 1380:83 1480:98"  
use_sched_load:  1 
use_migration_notif:  1
ignore_hispeed_on_notif:  0
fast_ramp_down:  0

设备的频率表：
307, 460, 537, 614, 748, 825, 902, 1056, 1132, 1209, 1363, 1440, 1516, 1670, 1747, 1824
```

### 场景1

```python
当前的频率： 825
当前的负载： 99
上次hispeed状态允许提升频率的时刻:  1980000
上次允许降频的时刻:  1980000
当前时刻:  2000000

进入 cpufreq_interactive_timer
是否收到调度器通知 = True
是否跳过hispeed逻辑 = False
是否跳过降频逻辑 = False

进入 choose_freq
当前负载 = 825 * 99 = 81675
prev_freq = 825
freq = 825
循环开始

# 一周目
prev_freq = freq = 825
freq对应的targetload = 63
当前负载 / freq对应的targetload = 1296
freq = 在频率表选一个比它大的频率里最小的(1296) = 1363
检查 freq > prev_freq
符合 1363 > 825
下边界频率 = prev_freq = 825
检查 freq >= 上边界频率
不符合 1363 >= 999999999
检查 prev_freq == freq
不符合 825 == 1363
回循环开头

# 二周目
prev_freq = freq = 1363
freq对应的targetload = 91
当前负载 / freq对应的targetload = 897
freq = 在频率表选一个比它大的频率里最小的(897) = 902
检查 freq > prev_freq
不符合 902 > 1363
检查 freq < prev_freq
符合 902 < 1363
上边界频率 = prev_freq = 1363
检查 freq <= 下边界频率
不符合 902 <= 825
检查 prev_freq == freq
不符合 1363 == 902
回循环开头

# 三周目
prev_freq = freq = 902
freq对应的targetload = 71
当前负载 / freq对应的targetload = 1150
freq = 在频率表选一个比它大的频率里最小的(1150) = 1209
检查 freq > prev_freq
符合 1209 > 902
下边界频率 = prev_freq = 902
检查 freq >= 上边界频率
不符合 1209 >= 1363
检查 prev_freq == freq
不符合 902 == 1209
回循环开头

# 四周目
prev_freq = freq = 1209
freq对应的targetload = 91
当前负载 / freq对应的targetload = 897
freq = 在频率表选一个比它大的频率里最小的(897) = 902
检查 freq > prev_freq
不符合 902 > 1209
检查 freq < prev_freq
符合 902 < 1209
上边界频率 = prev_freq = 1209
检查 freq <= 下边界频率
符合 902 <= 902
freq = 下边界频率 + 1 = 903
freq = 在频率表选一个大于等于它的频率里最小的(903) = 1056
检查 freq == 上边界频率
不符合 1056 == 1209
检查 prev_freq == freq
不符合 1209 == 1056
回循环开头

# 五周目
prev_freq = freq = 1056
freq对应的targetload = 71
当前负载 / freq对应的targetload = 1150
freq = 在频率表选一个比它大的频率里最小的(1150) = 1209
检查 freq > prev_freq
符合 1209 > 1056
下边界频率 = prev_freq = 1056
检查 freq >= 上边界频率
符合 1209 >= 1209
freq = 上边界频率 - 1 = 1208
freq = 在频率表选一个小于等于它的频率里最大的(1208) = 1132
检查 freq == 下边界频率
不符合 1132 == 1056
检查 prev_freq == freq
不符合 1056 == 1132

# 六周目
prev_freq = freq = 1132
freq对应的targetload = 71
当前负载 / freq对应的targetload = 1150
freq = 在频率表选一个比它大的频率里最小的(1150) = 1209
检查 freq > prev_freq
符合 1209 > 1132
下边界频率 = prev_freq = 1132
检查 freq >= 上边界频率
符合 1209 >= 1209
freq = 上边界频率 - 1 = 1208
freq = 在频率表选一个小于等于它的频率里最大的(1208) = 1132
检查 freq == 下边界频率
符合 1132 == 1132
freq = 上边界频率 = 1209
跳出循环
输出 freq = 1209

回到 cpufreq_interactive_timer
下一CPU频率 = 1209
检查 use_sched_load == 1 and use_migration_notif == 1 and enable_prediction == 1
不符合 1 == 1 and 1 == 1 and 0 == 1
符合 是否跳过hispeed逻辑 == False
检查 当前CPU占用率 >= go_hispeed_load
符合 99 >= 98
检查 当前CPU频率 < hispeed_freq
符合 1209 < 1380
下一CPU频率 = hispeed_freq = 1380
下一CPU频率 = 在频率表选一个大于等于它的频率里最小的(1380) = 1440
above_hispeed_delay = freq_to_above_hispeed_delay(1440) = 38000
符合 是否跳过hispeed逻辑 == False
检查 当前CPU频率 >= hispeed_freq and 下一CPU频率 > 当前CPU频率
不符合 825 >= 1380 and 1440 > 825
上次hispeed状态允许提升频率的时刻 = 当前时刻 = 2000000
符合 是否跳过降频逻辑 == False
检查 下一CPU频率 < 当前CPU频率
不符合 1440 < 825
上次允许降频的时刻 = 当前时刻 = 2000000
输出 下一CPU频率 = 1440
```

### 场景2

> 使用“e3”代替3个“0”，以便观察到时间上的限制

```python
当前的频率： 1747
当前的负载： 99
上次hispeed状态允许提升频率的时刻:  1980e3
上次允许降频的时刻:  1980e3
当前时刻:  2000e3

考虑 当前时刻 - 上次hispeed状态允许提升频率的时刻 < above_hispeed_delay
由于 2000e3 - 1980e3 < 138e3
选择的下一CPU频率： 1747

当前的频率： 1747
当前的负载： 70
上次hispeed状态允许提升频率的时刻:  1980e3
上次允许降频的时刻:  2000e3
当前时刻:  2020e3

考虑 下一CPU频率 > 当前CPU频率
由于 1363 < 1747
上次hispeed状态允许提升频率的时刻 = 当前时刻 = 2020e3

当前的频率： 1363
当前的负载： 99
上次hispeed状态允许提升频率的时刻:  2020e3
上次允许降频的时刻:  2020e3
当前时刻:  2040e3

考虑 当前时刻 - 上次hispeed状态允许提升频率的时刻 < above_hispeed_delay
由于 2040e3 - 2020e3 < 38e3
选择的下一CPU频率： 1363

当前的频率： 1363
当前的负载： 99
上次hispeed状态允许提升频率的时刻:  2020e3
上次允许降频的时刻:  2040e3
当前时刻:  2060e3

考虑 当前时刻 - 上次hispeed状态允许提升频率的时刻 < above_hispeed_delay
由于 2060e3 - 2020e3 > 38e3
选择的下一CPU频率： 1516
# 如果通过choose_freq选择的频率更高，比如1824，就能升频到1824
# 尽管此时 2060e3-2000e3 = 60e3 < 138e3，但绕开了开头的限制
```

## 【 上文没有提到的Tunable解释 】

1. boostpulse_duration
类型：时长  
说起来，为什么`interactive`调速器是这个交互式的名字？  
因为相比纯属靠采样的调速器比如`ondemand`，`interactive`自带了触摸升频的功能  
触摸的中断服务可以调用interactive提供的功能，进入boost状态，保持`boostpulse_duration`这个时长  
与`input_boost`不同的，`input_boost`通过修改最低频率实现类似的功能  
`boost`的实现方式类似于`min_sampling_time`，选择的频率不低于`hispeed_freq`  
这两者在`choose_freq`流程中会有差异  
不过如今已经有了独立的`input_boost`，这个功能可能不被触摸的中断服务调用了  
例如 80000，表示一次boost的时长为80ms  

2. boost
类型：是否  
一直保持boost状态  

3. io_is_busy
类型：是否  
把I/O时间计入CPU工作时长  
CPU状态分为工作(busy)和空闲(idle)  
上一周期负载值 = CPU工作时长 / 周期时长  
如果I/O性能与CPU主频关系密切，启用它  
另外，这个参数与HMP Scheduler的负载统计的`io_is_busy`保持一致  

4. sampling_down_factor
类型：倍率  
当前频率为最高频时，保底时间为 `sampling_down_factor` x `min_sample_time`  
例如 3，表示 3x39000 = 117000(圆整到6个`timer_rate`)  
例如 0，表示 1 倍  

5. max_freq_hysteresis
类型：时长  
相当于在最高频时的`min_sampling_time`  

6. align_windows
类型：是否  
对齐`interactive`的定时器时间窗口，以前用于骁龙600,800这类aSMP处理器的参数  
由于异步多核心的各个核心的调速器各自独立，需要对齐时间窗口  
如果`use_sched_load`设置为1，那么时间窗口自然是对齐的  

## 【 参考 】

Qualcomm cpufreq_interactive.c 源代码  
<https://android.googlesource.com/kernel/msm/+/android-lego-6.0.1_r0.2/drivers/cpufreq/cpufreq_interactive.c>  
HMP Scheduler 文档  
<https://github.com/OnePlusOSS/android_kernel_oneplus_msm8996/raw/oneplus3/6.0.1/Documentation/scheduler/sched-hmp.txt>  
早起的虫儿被鸟儿吃：DVFS Interactive-choose_freq()函数解析  
<http://blog.csdn.net/chongyang198999/article/details/49451587>  
jerry_ms：linux cpufreq interactive调频代码实现  
<http://blog.csdn.net/u014089131/article/details/68490573>  
showstopper_x：CPU动态调频二：interactive governor  
<http://blog.csdn.net/yin262/article/details/45697221>  

2018.06.15
yc