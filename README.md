# cpufreq-interactive-opt

optimize the interactive parameters of cpufreq driver

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

## 项目源码(Source code)

<https://github.com/yc9559/cpufreq-interactive-opt/tree/master/project/20180603.2>

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
