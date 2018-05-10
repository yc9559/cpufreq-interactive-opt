# Project WIPE

Workload-based Interactive Parameter Explorer  
20180509 均衡 卡顿 费电 低延迟  

## 支持如下SOC

Snapdragon 835, 820/821, 810/808, 801/800/805, 660, 636, 652/650, 625/626  
Exynos 8895, 8890, 7420  
Kirin 970, 960, 950/955  
Helio X20/X25, X10  
Atom z3560/z3580  
Snapdragon 845(手工调整)

## 警告(Warning)

勿作商业用途，禁止转载内容和内嵌参数  
Do not use for commercial purposes, prohibit reproducing content and embedding parameters in custom ROM and kernel  
酷安ID：@yc9559  

## 这是什么(What is it)

通过人工凭感觉调整interactive参数的方式，有如下问题：  
Adjusting the interactive parameters by our feeling, there are the following problems:  

- 调参难以有明确的反馈(difficulties to have clear feedback)
- 本身功耗和性能顾此失彼(hard to reach the balance of power consumption and performance)
- 参数自由度很高互相纠缠使得难以分离主要因素(complex parameters)

本计划旨在通过如下方式，制作自动化程序，来解决上述问题：  
This project aims to solve the problems above by creating automated programs as follows:  

- 现实负载采集(real world workload capture)
- interactive调速器流程仿真(interactive governor process simulation)
- 卡顿和耗电评分函数(cost function of lag and power comsuption)
- 迭代取得局部最优(iteration to obtain local optimum)

## 有啥不同

- 基于 Project WIPE 20171202
- 评分函数主体改为分区检测，取代原本整体统计信息
- 均一化的性能评分可以跨SOC衡量相对默认参数的卡顿程度，有助于统一质量

- 待机耗电相比20171202显著改进，亮屏续航指标更加接近真实使用表现
- 标准化全部处理器的功耗模型，由821功耗曲线变换而来，为大量SOC支持提供基础和不错的近似效果
- 独立的待机检测和负载模型，混合了0v0和视频硬解码的负载序列，更好地模拟低频连续负载波动效果
- 仿真器支持CPU idle状态耗电比例，CPU在高频处闲置并没有那么耗电

- 负载序列支持添加高斯噪声，但是没有开启因为影响了前后关联的预测
- `target_loads`动态长度输出支持，改善一点interactive执行效率
- 市面主流SOC基本全部支持，适应不同的频率表和功耗特征

- 优化器执行耗时相比20171202降低85%
- 参数序列无损降维，从44降低到29，加速收敛过程和更好的拟合效果
- 大种群数量和低迭代次数，改善种群多样性避免过拟合以及改善执行效率
- 允许前几代种群硬指标筛选关闭，改善初值的多样性

- 平台从 Kernel Auditor 切换到脚本执行，实现目前最佳的调整自由度
- 微工具箱的动态响应通过检测前台应用，异步执行性能配置切换，实现分应用打磨
- 多配置的脚本除了调整interactive参数，也可调整HMP，热插拔，温控，触摸升频，IO，cpuset，Perfd，hps

## 操作指南(微工具箱)

前提条件：

1. 没有对内核的要求，官方内核即可
2. 如果原本的温控过于激进，为了避免影响效果，需要删除原本的温控
3. 使用过 EX Kernel Manager 或 Kernel Auditor 调整参数
4. 已经解决好待机异常频繁唤醒
5. 已经取得ROOT权限，以及解锁system可写

如何操作：

1. 在下面找到适用的SOC，复制链接到ADM下载器，新建下载任务完成下载
2. 复制这个文件到`/data`，重命名为`powercfg`，权限设置为755
3. 安装微工具箱，启动后开启自动行为和动态响应，启用对应的无障碍服务，把微工具箱加入到后台限制的白名单里
4. 在性能配置选择每个应用对应使用的配置
5. 安装 Kernel Auditor，在微工具箱设定它使用省电模式，启动后检查参数是否成功应用
6. 卸载 Kernel Auditor

补充说明：

1. 均衡 = 均衡版，推荐使用这个，以往的DEV版本只提供这个档位，相对感知卡顿为86
2. 省电 = 卡顿版，带来更多的卡顿，如果硬是要节省一点电量，相对感知卡顿为110
3. 游戏 = 费电版，可能比默认的更加费电，如果均衡的流畅度不能满意，相对感知卡顿为65
4. 极速 = 低延迟，相当的费电，如果需要稳定的性能调控，固定最低频率在1.6Ghz上下
5. 微工具箱的其他功能并非必需，了解风险之后再使用
6. 喜欢手动挡的玩家，下载文件后使用文本编辑器打开即可找到想要的参数

## 操作指南(Tasker)

前提条件：

1. 没有对内核的要求，官方内核即可
2. 如果原本的温控过于激进，为了避免影响效果，需要删除原本的温控
3. 使用过 EX Kernel Manager 或 Kernel Auditor 调整参数
4. 已经解决好待机异常频繁唤醒
5. 已经取得ROOT权限，以及已经安装busybox

如何操作：

1. 在下面找到适用的SOC，复制链接到ADM下载器，新建下载任务完成下载
2. 复制这个文件到`/data`，重命名为`powercfg`，权限设置为755
3. Tasker 支持运行shell脚本，用法如下：
    - `sh /data/powercfg balance`切换到均衡版
    - `sh /data/powercfg powersave`切换到卡顿版
    - `sh /data/powercfg performance`切换到费电版
    - `sh /data/powercfg fast`切换到低延迟版

补充说明：

1. 均衡 = 均衡版，推荐使用这个，以往的DEV版本只提供这个档位，相对感知卡顿为86
2. 省电 = 卡顿版，带来更多的卡顿，如果硬是要节省一点电量，相对感知卡顿为110
3. 游戏 = 费电版，可能比默认的更加费电，如果均衡的流畅度不能满意，相对感知卡顿为65
4. 极速 = 低延迟，相当的费电，如果需要稳定的性能调控，固定最低频率在1.6Ghz上下
5. 相比微工具箱更加干净，可以避免某些微工具箱的蜜汁bug，支持的事件也更加多样，例如开关屏幕时执行操作

## 对比

![与高通默认参数对比](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/20180509.png)

## 链接

https://github.com/yc9559/cpufreq-interactive-opt/blob/master/20180509-description.md  

Disscussion & Testing in Coolapk：https://www.coolapk.com/feed/6440134  

### 性能配置下载

- [Snapdragon 835](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_835/powercfg.apk)
- [Snapdragon 820 821](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_820_821/powercfg.apk)
- [Snapdragon 810 808](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_810_808/powercfg.apk)
- [Snapdragon 801 800 805](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_801_800_805/powercfg.apk)
- [Snapdragon 660](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_660/powercfg.apk)
- [Snapdragon 636](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_660/powercfg.apk)
- [Snapdragon 652 650](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_652_650/powercfg.apk)
- [Snapdragon 625 626](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_625_626/powercfg.apk)
- [Exynos 8895](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/exynos_8895/powercfg.apk)
- [Exynos 8890](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/exynos_8890/powercfg.apk)
- [Exynos 7420](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/exynos_7420/powercfg.apk)
- [Kirin 970](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/kirin_970/powercfg.apk)
- [Kirin 960](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/kirin_960/powercfg.apk)
- [Kirin 950 955](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/kirin_950_955/powercfg.apk)
- [Helio X20 X25](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/helio_x20_x25/powercfg.apk)
- [Helio X10](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/helio_x10/powercfg.apk)
- [Atom z3560 z3580](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/atom_z3560_z3580/powercfg.apk)
- [Snapdragon 845(手工调整)](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180509/sd_845/powercfg.apk)
