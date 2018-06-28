#!/system/bin/sh
# Project WIPE https://github.com/yc9559/cpufreq-interactive-opt
# Author: yc9559
# Platform: sd_801_800_805
# Generated at: Thu Jun 28 03:43:49 2018

C0_GOVERNOR_DIR="/sys/devices/system/cpu/cpufreq/interactive"
C1_GOVERNOR_DIR=""
C0_CPUFREQ_DIR="/sys/devices/system/cpu/cpu0/cpufreq"
C1_CPUFREQ_DIR=""

# $1:timer_rate $2:value
function set_param_little() 
{
	echo ${2} > ${C0_GOVERNOR_DIR}/${1}
}

# $1:timer_rate $2:value
function set_param_big() 
{
	:
}

# $1:timer_rate
function print_param() 
{
	print_value "${1}" ${C0_GOVERNOR_DIR}/${1}
}

function unify_environment() 
{
	# SELinux permissive
	setenforce 0
	# disable hotplug to switch governor
	set_value 0 /sys/module/msm_thermal/core_control/enabled
	set_value N /sys/module/msm_thermal/parameters/enabled
	# in case of using ondemand as default governor
	lock_value "interactive" ${C0_CPUFREQ_DIR}/scaling_governor
}

function runonce_custom()
{
	setprop ro.qualcomm.perf.cores_online 2
	lock_value 2500 /sys/module/cpu_boost/parameters/input_boost_ms
}

function before_modify()
{
	stop mpdecision
	chown 0.0 ${C0_GOVERNOR_DIR}/*
	chmod 0666 ${C0_GOVERNOR_DIR}/*
	set_value 1 /sys/devices/system/cpu/cpu0/online
	set_value 1 /sys/devices/system/cpu/cpu1/online
	set_value 1 /sys/devices/system/cpu/cpu2/online
	set_value 1 /sys/devices/system/cpu/cpu3/online
	lock_value 280000 /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
	lock_value 280000 /sys/devices/system/cpu/cpu1/cpufreq/scaling_min_freq
	lock_value 280000 /sys/devices/system/cpu/cpu2/cpufreq/scaling_min_freq
	lock_value 280000 /sys/devices/system/cpu/cpu3/cpufreq/scaling_min_freq
}

function after_modify()
{
	chmod 0444 ${C0_GOVERNOR_DIR}/*
	start mpdecision
	verify_param
}

function powersave_custom()
{
	lock_value "380000" /sys/module/cpu_boost/parameters/input_boost_freq
}

function balance_custom()
{
	lock_value "380000" /sys/module/cpu_boost/parameters/input_boost_freq
}

function performance_custom()
{
	lock_value "380000" /sys/module/cpu_boost/parameters/input_boost_freq
}

function fast_custom()
{
	:
}



# $1:value $2:file path
function set_value() 
{
	if [ -f $2 ]; then
		echo $1 > $2
	fi
}

# $1:value $2:file path
function lock_value() 
{
	if [ -f $2 ]; then
		# chown 0.0 $2
		chmod 0666 $2
		echo $1 > $2
		chmod 0444 $2
	fi
}

# $1:io-scheduler $2:block-path
function set_io() 
{
	if [ -f $2/queue/scheduler ]; then
		if [ `grep -c $1 $2/queue/scheduler` = 1 ]; then
			echo $1 > $2/queue/scheduler
			echo 512 > $2/queue/read_ahead_kb
			lock_value 0 $2/queue/iostats
			lock_value 256 $2/queue/nr_requests
			lock_value 0 $2/queue/iosched/slice_idle
		fi
	fi
}

# $1:display-name $2:file path
function print_value() 
{
	if [ -f $2 ]; then
		echo $1
		cat $2
	fi
}

function verify_param() 
{
	expected_target=${C0_GOVERNOR_DIR}/target_loads
	if [ "$action" = "powersave" ]; then
		expected_value="80 380000:6 580000:25 680000:43 880000:61 980000:86 1180000:97"
	elif [ "$action" = "balance" ]; then
		expected_value="80 380000:32 580000:47 680000:82 880000:32 980000:39 1180000:83 1480000:79 1680000:98"
	elif [ "$action" = "performance" ]; then
		expected_value="80 380000:32 580000:45 680000:81 880000:63 980000:47 1180000:89 1480000:79 1680000:98"
	elif [ "$action" = "fast" ]; then
		expected_value="80 1980000:90"
	fi
	if [ "`cat ${expected_target}`" = "${expected_value}" ]; then
		echo "${action} OK"
	else
		echo "${action} FAIL"
	fi
}

action=$1
if [ ! -n "$action" ]; then
    action="balance"
fi

if [ "$action" = "debug" ]; then
	echo "Project WIPE https://github.com/yc9559/cpufreq-interactive-opt"
	echo "Author: yc9559"
	echo "Platform: sd_801_800_805"
	echo "Generated at: Thu Jun 28 03:43:49 2018"
	echo ""
	print_value "Cluster 0: min_freq" ${C0_CPUFREQ_DIR}/scaling_min_freq
	print_param above_hispeed_delay
	print_param target_loads
	print_value "sched_spill_load" /proc/sys/kernel/sched_spill_load
	print_value "eMMC IO scheduler" /sys/block/mmcblk0/queue/scheduler
	print_value "UFS IO scheduler" /sys/block/sda/queue/scheduler
	which perfd
	exit 0
fi

if [ ! -f /dev/.project_wipe ]; then
	unify_environment
fi

before_modify

# RunOnce
if [ ! -f /dev/.project_wipe ]; then
	# set flag
	touch /dev/.project_wipe

	runonce_custom

	set_io cfq /sys/block/mmcblk0
	set_io cfq /sys/block/sda

	# shared interactive parameters
	set_param_little timer_rate 20000
	set_param_little timer_slack 180000
	set_param_little boost 0
	set_param_little boostpulse_duration 0
	set_param_big timer_rate 20000
	set_param_big timer_slack 180000
	set_param_big boost 0
	set_param_big boostpulse_duration 0
fi

if [ "$action" = "powersave" ]; then
	powersave_custom
	set_param_little above_hispeed_delay "18000 1680000:98000 1880000:138000"
	set_param_little hispeed_freq 1180000
	set_param_little go_hispeed_load 97
	set_param_little target_loads "80 380000:6 580000:25 680000:43 880000:61 980000:86 1180000:97"
	set_param_little min_sample_time 18000
	set_param_big above_hispeed_delay "18000 1680000:98000 1880000:138000"
	set_param_big hispeed_freq 1180000
	set_param_big go_hispeed_load 97
	set_param_big target_loads "80 380000:6 580000:25 680000:43 880000:61 980000:86 1180000:97"
	set_param_big min_sample_time 18000
fi

if [ "$action" = "balance" ]; then
	balance_custom
	set_param_little above_hispeed_delay "38000 1480000:78000 1680000:98000 1880000:138000"
	set_param_little hispeed_freq 1180000
	set_param_little go_hispeed_load 97
	set_param_little target_loads "80 380000:32 580000:47 680000:82 880000:32 980000:39 1180000:83 1480000:79 1680000:98"
	set_param_little min_sample_time 18000
	set_param_big above_hispeed_delay "38000 1480000:78000 1680000:98000 1880000:138000"
	set_param_big hispeed_freq 1180000
	set_param_big go_hispeed_load 97
	set_param_big target_loads "80 380000:32 580000:47 680000:82 880000:32 980000:39 1180000:83 1480000:79 1680000:98"
	set_param_big min_sample_time 18000
fi

if [ "$action" = "performance" ]; then
	performance_custom
	set_param_little above_hispeed_delay "18000 1480000:98000 1880000:38000"
	set_param_little hispeed_freq 1180000
	set_param_little go_hispeed_load 97
	set_param_little target_loads "80 380000:32 580000:45 680000:81 880000:63 980000:47 1180000:89 1480000:79 1680000:98"
	set_param_little min_sample_time 38000
	set_param_big above_hispeed_delay "18000 1480000:98000 1880000:38000"
	set_param_big hispeed_freq 1180000
	set_param_big go_hispeed_load 97
	set_param_big target_loads "80 380000:32 580000:45 680000:81 880000:63 980000:47 1180000:89 1480000:79 1680000:98"
	set_param_big min_sample_time 38000
fi

if [ "$action" = "fast" ]; then
	fast_custom
	lock_value 1480000 ${C0_CPUFREQ_DIR}/scaling_min_freq
	set_param_little above_hispeed_delay "18000 1880000:198000"
	set_param_little hispeed_freq 1480000
	set_param_little target_loads "80 1980000:90"
	set_param_little min_sample_time 38000
	lock_value 1480000 ${C1_CPUFREQ_DIR}/scaling_min_freq
	set_param_big above_hispeed_delay "18000 1880000:198000"
	set_param_big hispeed_freq 1480000
	set_param_big target_loads "80 1980000:90"
	set_param_big min_sample_time 38000
fi

after_modify

exit 0