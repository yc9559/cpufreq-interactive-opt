# Project WIPE

Workload-based Interactive Parameter Explorer  
20180603 均衡 卡顿 费电 低延迟  

## 支持如下SOC

Snapdragon 835, 820/821, 810/808, 801/800/805, 660, 636, 652/650, 625/626  
Exynos 8895, 8890, 7420  
Kirin 970, 960, 950/955  
Helio X20/X25, X10  
Atom z3560/z3580  
Snapdragon 845(非程序生成)

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

Update 20180603.2：  

- misc：新的输入升频风格，略微提升最低频率保持2.5s，使得在触摸后interactive选频倾向于保留更多余量
- misc：低延迟模式的频率动态锁从2.0G降低到1.9G
- template：powercfg执行之后可以输出是否成功，如`balance OK`
- template：修复由关闭perfd引起的最低频设置过高
- template：新的架构设计更加抽象，易于移植，易于阅读

## 对比

![与高通默认参数对比](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/20180603.png)

## 传送门

适用于 EX/内核调教 的操作： <https://github.com/yc9559/cpufreq-interactive-opt/blob/master/20180603-KA-balance.md>  

Disscussion & Testing in Coolapk：<https://www.coolapk.com/feed/6756482>  

## 如何执行性能配置

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
3. 在设置-"界面"取消勾选"初学者模式"
4. 在设置-"监视器"修改"所有检查秒数"为3600
5. 在设置-"杂项"勾选"减少资源消耗"
6. Tasker 支持运行shell脚本，用法如下：
    - `sh /data/powercfg balance`切换到均衡
    - `sh /data/powercfg powersave`切换到卡顿
    - `sh /data/powercfg performance`切换到费电
    - `sh /data/powercfg fast`切换到低延迟
    - `sh /data/powercfg debug`输出脚本和参数信息
7. 执行shell脚本时需要勾选使用root权限

给几个例子：

1.显示参数应用是否生效，不再依赖于 Kernel Auditor 之类的工具
![tasker-debug-detail](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/tasker-debug-detail.png)
![tasker-debug](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/tasker-debug.jpg)

2.快捷模式切换
![tasker-quick-config](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/tasker-quick1.jpg)
![tasker-quick-switch](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/tasker-quick2.jpg)

3.基于前台进程名称，低电量，关闭屏幕，开机完成的事件触发，其中前台进程名称依赖于 Tasker 的无障碍服务
![tasker-ondemand](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/tasker-ondemand.jpg)

补充说明：

1. 均衡版，推荐使用这个，以往的DEV版本只提供这个档位，相对感知卡顿为85
2. 卡顿版，带来更多的卡顿，如果硬是要节省一点电量，相对感知卡顿为115
3. 费电版，可能比默认的更加费电，如果均衡的流畅度不能满意，相对感知卡顿为60
4. 低延迟，相当的费电，如果需要稳定的性能调控例如专业多媒体，固定最低频率在1.6Ghz上下

## 操作指南(微工具箱)

前提条件：与Tasker的相同

如何操作：

1. 在下面找到适用的SOC，复制链接到ADM下载器，新建下载任务完成下载
2. 复制这个文件到`/data`，重命名为`powercfg`，权限设置为755
3. 安装微工具箱，启动后开启自动行为和动态响应，启用对应的无障碍服务，把微工具箱加入到后台限制的白名单里
4. 在性能配置选择每个应用对应使用的配置
5. 安装 Kernel Auditor，在微工具箱设定它使用省电模式，启动后检查参数是否成功应用
6. 卸载 Kernel Auditor

补充说明：

1. 均衡 = 均衡版，省电 = 卡顿版，游戏 = 费电版，极速 = 低延迟
2. 微工具箱的其他功能并非必需，了解风险之后再使用

## 操作指南(Kernel Auditor模拟init.d)

前提条件：与Tasker的相同

如何操作：

1. 在下面找到适用的SOC，复制链接到ADM下载器，新建下载任务完成下载
2. 复制这个文件到`/system/etc/init.d`，重命名为`wipe20180603_balance`，权限设置为755
3. 安装 Kernel Auditor，在模拟init.d选择`wipe20180603_balance`执行，设置为开机自启

补充说明：

1. 由于这个方式不支持参数，只能应用均衡版
2. Kernel Auditor 很可能会出现CPU 100%的bug

## 操作指南(WIPE_flashable)

由 @cjybyjk 制作的多合一卡刷包：  

<https://github.com/cjybyjk/WIPE_flashable>  

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

## 性能配置下载

- [Snapdragon 835](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_835/powercfg.apk)
- [Snapdragon 820 821](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_820_821/powercfg.apk)
- [Snapdragon 810 808](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_810_808/powercfg.apk)
- [Snapdragon 801 800 805](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_801_800_805/powercfg.apk)
- [Snapdragon 660](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_660/powercfg.apk)
- [Snapdragon 636](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_660/powercfg.apk)
- [Snapdragon 652 650](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_652_650/powercfg.apk)
- [Snapdragon 625 626](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_625_626/powercfg.apk)
- [Exynos 8895](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/exynos_8895/powercfg.apk)
- [Exynos 8890](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/exynos_8890/powercfg.apk)
- [Exynos 7420](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/exynos_7420/powercfg.apk)
- [Kirin 970](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/kirin_970/powercfg.apk)
- [Kirin 960](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/kirin_960/powercfg.apk)
- [Kirin 950 955](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/kirin_950_955/powercfg.apk)
- [Helio X20 X25](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/helio_x20_x25/powercfg.apk)
- [Helio X10](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/helio_x10/powercfg.apk)
- [Atom z3560 z3580](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/atom_z3560_z3580/powercfg.apk)
- [Snapdragon 845(非程序生成)](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/vtools-powercfg/20180603/sd_845/powercfg.apk)

## Credit

[Distributed Evolutionary Algorithms in Python](https://github.com/DEAP/deap)  
@ft1858336  跟他交流意识到从201710开始一直存在的仿真逻辑和interactive的不一致，直接导致了180526版没有发出来  
@Yoooooo    瞬时性能意见，比如MIUI多任务切换，性能释放合页标准差，测试S835的参数，跟上了日更的节奏，协助测试20180603.2  
@僞裝灬     测试S821的参数，基本跟上了日更的节奏  
@xujiyuan723测试S808的参数，启发统一S810/808最高频率  
@HELISIGN   测试S821的参数，启发above_hispeed_delay改进  
@揪你鸡儿   测试S808的参数  
@zqyhqw     提供借助install-recovery.sh执行脚本的方法    
@HHHGTTT    提供Exynos HMP和热插拔修改的点子  
@嘟嘟斯基   参考了他的Exynos的shell脚本  

## 捐赠

并不在乎捐赠的这点钱，之后也不会有更新，如果你实在愿意，下面是感谢~~云讨饭~~通道(写上你的ID和来源平台)：  

![支付宝捐赠QR](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/alipay-qr.png)

[1]: https://www.coolapk.com/feed/3712488
[2]: https://www.coolapk.com/feed/4355087
[3]: https://www.coolapk.com/feed/4570875
[4]: https://www.coolapk.com/feed/4796254
[5]: https://www.coolapk.com/feed/5328381
[6]: https://www.coolapk.com/feed/5838948
[7]: https://www.coolapk.com/feed/6440134
[8]: https://www.coolapk.com/feed/2278724