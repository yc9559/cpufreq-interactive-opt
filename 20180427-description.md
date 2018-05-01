# Project WIPE

Workload-based Interactive Parameter Explorer  
DEV 20180330 V3 V3 V3 

Snapdragon 835, 820/821, 810/808, 801/800/805, 660, 636, 652/650, 625/626  
Exynos 8895, 8890, 7420  
Kirin 970, 960, 950/955  
Helio X20/X25, X10  
Atom z3560/z3580  
Snapdragon 845(效果未确认，不属于WIPE)

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

- 基于 Project WIPE 20180330 v2
- ADD 评分函数主体改为基于概率分布的模型，继续挣扎不做咸鱼带来不一样的卡顿手感
- ADD 微工具箱性能配置文件工具链支持，三档配置和分应用配置喜闻乐见
- ADD HMP参数调整集成到微工具箱性能配置文件，或许现在不再需要知道HMP怎么调了
- ADD 小火龙636，法克X10频率表支持
- MOD 优化器执行时间缩短30%，可能是新的评分函数梯度比较大
- MOD `target_loads`第一个数值限制为85来控制待机耗电，因为新评分函数大概率待机耗电尿崩
- MOD 新做了一张与高通默认interactive参数效果的对比图，补上了之前的横纵坐标标题
- ERR 更多的一些自己改了太多就忘记了

## 操作指南

1. 如果提问**下面已有的内容**，**不再回答**
2. 几乎没有对内核的要求，官方内核即可
3. 在本仓库`/tools`目录提供了有用的调试工具
4. 待机耗电一般在0.5-1.0%/h，耗电过多先检查唤醒锁，使用 Wakelock Detector 或者 3C Toolbox
5. 本版本推荐使用微工具箱，使用之前确保 EX Kernel Manager 和 Kernel Auditor 不会带来干扰
6. 微工具箱性能配置文件下载后重命名为`powercfg`，复制到`/data`，最终该文件路径为`/data/powercfg`，权限设置为755
7. 启动微工具箱，删除系统的温控，启用并设置自动服务，重启设备，用全新安装的 EX Kernel Manager 检查参数是否生效
8. 省电->卡顿，均衡->均衡，游戏->费电，极速->还没有做
9. 一般经典的使用搭配是，游戏使用费电版，小说和视频软件使用卡顿版
10. 微工具箱的其他功能并非必需，了解风险之后再使用
11. 喜欢手动挡的玩家，下载文件后使用文本编辑器打开即可找到想要的参数

## 链接

https://github.com/yc9559/cpufreq-interactive-opt/blob/master/20180427-description.md  

Disscussion & Testing in Coolapk：https://www.coolapk.com/feed/6306612  

## 对比

![与高通默认参数对比](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/DEV180412.png)

### 微工具箱性能配置下载(Powered by RawGit)

- [Snapdragon 835](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_835/powercfg.apk)
- [Snapdragon 820 821](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_820_821/powercfg.apk)
- [Snapdragon 810 808](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_810_808/powercfg.apk)
- [Snapdragon 801 800 805](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_801_800_805/powercfg.apk)
- [Snapdragon 660](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_660/powercfg.apk)
- [Snapdragon 636](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_660/powercfg.apk)
- [Snapdragon 652 650](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_652_650/powercfg.apk)
- [Snapdragon 625 626](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_625_626/powercfg.apk)
- [Exynos 8895](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/exynos_8895/powercfg.apk)
- [Exynos 8890](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/exynos_8890/powercfg.apk)
- [Exynos 7420](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/exynos_7420/powercfg.apk)
- [Kirin 970](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/kirin_970/powercfg.apk)
- [Kirin 960](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/kirin_960/powercfg.apk)
- [Kirin 950 955](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/kirin_950_955/powercfg.apk)
- [Helio X20 X25](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/helio_x20_x25/powercfg.apk)
- [Helio X10](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/helio_x10/powercfg.apk)
- [Atom z3560 z3580](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/atom_z3560_z3580/powercfg.apk)
- [Snapdragon 845(效果未确认，不属于WIPE)](https://cdn.rawgit.com/yc9559/cpufreq-interactive-opt/bc137555/vtools-powercfg/20180427/sd_845/powercfg.apk)
