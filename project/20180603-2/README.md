# Project WIPE

> Workload-based Interactive Parameter Explorer  
> Programme Version:    20180603.2  
> Document Version:     20180725  

## Warning

Customization is allowed, but the information below MUST be notated at the beginning of your intro:  
- Original Author：[Coolapk@yc9559](https://github.com/yc9559/)  
- Original Project：Project WIPE  
- Original Project URL：<https://github.com/yc9559/cpufreq-interactive-opt/>  

允许二次开发和内嵌，但是需要在帖子、项目、插件或者刷机包之类的介绍的第一段显眼位置标注：  
- 原作者：[酷安@yc9559](https://github.com/yc9559/)  
- 原项目名称：Project WIPE  
- 原项目地址：<https://github.com/yc9559/cpufreq-interactive-opt/>  


## Welcome

TERRIBLE [Project WIPE](https://github.com/yc9559/cpufreq-interactive-opt/) source code :), but it surely works.  
DIY your AUTO interactive parameter optimizer!  

What you can do:  
- add CPU support, such as Snapdragon 615
- customize target function
- find bugs
- etc...

## Introduction

Adjusting the interactive parameters by our feeling, there are the following problems:  

- difficulties to have clear feedback
- hard to reach the balance of power consumption and performance
- complex interactive parameters

This project aims to solve the problems above by creating automated programs as follows:  

- real world workload capture
- interactive governor process simulation
- cost function of lag and power comsuption
- iteration to obtain local optimum using NSGA2

## Requirement

- Python 2.7
- [Deap 1.2.2](https://github.com/deap/deap)

## Usage

1. edit `modules/conf.py`, keep what you want to run in the optimizer  

```python
todolist = [
    # 's821_l',
    's821_b',
    # 'k950_l',
    # 'k950_b',
    # 'k960_l',
    # 'k960_b',
    # 'k970_l',
    # 'k970_b',
    # 's650_l',
    # 's650_b',
    # 's625_uni',
    # 's835_l',
    # 's835_b',
    # 's660_l',
    # 's660_b',
]
```

2. execute

```shell
python 0428.py
```

## File Description

- `csv`: csv & txt output dir
- `modules`: function modules
    - `__init__.py`: includes
    - `conf.py`: static parameters of project WIPE
    - `envloader.py`: convert profiles to runtime data structure
    - `interactive.py`: cpufreq interactive governor simulation & parameter evaluation
    - `logger.py`: log a list of results to a text file
    - `misc.py`: progress bar
    - `nsga2int.py`: enable NSGA2 to support integer datatype
    - `powermodel.py`: Application Processor profiles, including power models and available performance steps
    - `shellconfig.py`: write the best 3 parameters to a shell script
- `powermodel`: some datasheets about CPUs
    - `freq_table.xlsx`: frequency tables of CPUs
    - `generic-180320.xlsx`: powertable generator
- `recent_version`: some old version before 20171104
- `shell`: files about shell script
    - `output`: shell script output dir
    - `template`: shell script template
- `workload_model`: workload sequence files
- `0428.py`: main(), branch from 20180428
- `benchmark.py`: interactive parameters testing tool
- `README.md`: document

## Credit

酷安积极反馈的同志(按时间升序)：  

@Fdss45  
@yy688go (TSU守望者)  
@Jouiz  
@lpc3123191239  
@小方叔叔  
@星辰紫光  
@ℳ๓叶落情殇  
@屁屁痒  
@发热不卡算我输  
@予北  
@選擇遺忘  
@想飞的小伙  
@白而出清  
@AshLight  
@微风阵阵  
@半阳半心  
@AhZHI  
@悲欢余生有人听  
@YaomiHwang  
@花生味  
@胡同口卖菜的  
@gce8980  
@vesakam  
@q1006237211  
@Runds  
@lmentor  
@萝莉控の胜利  
@iMeaCore  
@Dfift半島鐵盒  
@wenjiahong  
@星空未来  
@水瓶  
@瓜瓜皮  
@默认用户名8  
@影灬无神  
@橘猫520  
@此用户名已存在  
@ピロちゃん  
@Jaceﮥ  
@黑白颠倒的年华0  
@九日不能贱  
@fineable  
@哑剧  
@zokkkk  
@永恒的丶齿轮  
@L风云  
@Immature_H  
@xujiyuan723  
@Ace蒙奇  
@ちぃ  
@木子茶i同学  
@HEX_Stan  
@_暗香浮动月黄昏  
@子喜  
@ft1858336  
@xxxxuanran  
@Scorpiring  
@猫见  
@僞裝灬  
@请叫我芦柑  
@吃瓜子的小白  
@HELISIGN  
@鹰雏  
@贫家boy有何贵干  
@Yoooooo  
@揪你鸡儿  

## Donate

并不在乎捐赠的这点钱，之后也不会有更新，如果你实在愿意，下面是感谢~~云讨饭~~通道(写上你的ID和来源平台)：  

![支付宝捐赠QR](https://github.com/yc9559/cpufreq-interactive-opt/raw/master/src/alipay-qr.png)
