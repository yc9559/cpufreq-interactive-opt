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
