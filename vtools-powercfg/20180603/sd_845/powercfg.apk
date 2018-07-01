#!/system/bin/sh
# EAS parameter adjustment for SDM 845
# https://github.com/yc9559/cpufreq-interactive-opt
# Author: yc9559
# Platform: sd_845
# Generated at: Sat Jun 30 12:28:56 2018

C0_GOVERNOR_DIR="/sys/devices/system/cpu/cpu0/cpufreq/schedutil"
C1_GOVERNOR_DIR="/sys/devices/system/cpu/cpu4/cpufreq/schedutil"
C0_CPUFREQ_DIR="/sys/devices/system/cpu/cpu0/cpufreq"
C1_CPUFREQ_DIR="/sys/devices/system/cpu/cpu4/cpufreq"

# $1:timer_rate $2:value
function set_param_little() 
{
	echo ${2} > ${C0_GOVERNOR_DIR}/${1}
}

# $1:timer_rate $2:value
function set_param_big() 
{
	echo ${2} > ${C1_GOVERNOR_DIR}/${1}
}

# $1:timer_rate
function print_param() 
{
	print_value "LITTLE: ${1}" ${C0_GOVERNOR_DIR}/${1}
	print_value "big: ${1}" ${C1_GOVERNOR_DIR}/${1}
}

function unify_environment() 
{
	# SELinux permissive
	setenforce 0
	# disable hotplug to switch governor
	set_value 0 /sys/module/msm_thermal/core_control/enabled
	set_value N /sys/module/msm_thermal/parameters/enabled
	# in case of using ondemand as default governor
	lock_value "schedutil" ${C0_CPUFREQ_DIR}/scaling_governor
	lock_value "schedutil" ${C1_CPUFREQ_DIR}/scaling_governor
	# Perfd, nothing to worry about, if error the script will continue
	stop perfd
}

function runonce_custom()
{
	set_value 90 /proc/sys/kernel/sched_spill_load
	set_value 1 /proc/sys/kernel/sched_prefer_sync_wakee_to_waker
	set_value 3000000 /proc/sys/kernel/sched_freq_inc_notify

	# avoid permission problem, do not set 0444
	set_value 2-3 /dev/cpuset/background/cpus
	set_value 0-3 /dev/cpuset/system-background/cpus
	set_value 0-3,4-7 /dev/cpuset/foreground/cpus
	set_value 0-3,4-7 /dev/cpuset/top-app/cpus

	# set_value 85 /proc/sys/kernel/sched_downmigrate
	# set_value 95 /proc/sys/kernel/sched_upmigrate

	lock_value 80 /sys/module/cpu_boost/parameters/input_boost_ms
	lock_value 0 /sys/module/msm_performance/parameters/touchboost
}

function before_modify()
{
	# chown 0.0 ${C0_GOVERNOR_DIR}/*
	chmod 0666 ${C0_GOVERNOR_DIR}/*
	lock_value 480000 ${C0_CPUFREQ_DIR}/scaling_min_freq

	set_value 1 /sys/devices/system/cpu/cpu4/online
	# chown 0.0 ${C1_GOVERNOR_DIR}/*
	chmod 0666 ${C1_GOVERNOR_DIR}/*
	lock_value 480000 ${C1_CPUFREQ_DIR}/scaling_min_freq
}

function after_modify()
{
	# chmod 0444 ${C0_GOVERNOR_DIR}/*
	# chmod 0444 ${C1_GOVERNOR_DIR}/*
	verify_param
}

function powersave_custom()
{
	lock_value "0:1680000 4:1880000" /sys/module/msm_performance/parameters/cpu_max_freq
	lock_value "0:1080000 4:0" /sys/module/cpu_boost/parameters/input_boost_freq
	lock_value 2 /sys/devices/system/cpu/cpu4/core_ctl/min_cpus
	lock_value 2 /sys/devices/system/cpu/cpu4/core_ctl/max_cpus
}

function balance_custom()
{
	lock_value "0:1780000 4:2280000" /sys/module/msm_performance/parameters/cpu_max_freq
	lock_value "0:1080000 4:0" /sys/module/cpu_boost/parameters/input_boost_freq
	lock_value 2 /sys/devices/system/cpu/cpu4/core_ctl/min_cpus
	lock_value 4 /sys/devices/system/cpu/cpu4/core_ctl/max_cpus
}

function performance_custom()
{
	lock_value "0:1780000 4:2880000" /sys/module/msm_performance/parameters/cpu_max_freq
	lock_value "0:1180000 4:0" /sys/module/cpu_boost/parameters/input_boost_freq
	lock_value 2 /sys/devices/system/cpu/cpu4/core_ctl/min_cpus
	lock_value 4 /sys/devices/system/cpu/cpu4/core_ctl/max_cpus
}

function fast_custom()
{
	lock_value "0:1780000 4:2280000" /sys/module/msm_performance/parameters/cpu_max_freq
	lock_value "0:1480000 4:1680000" /sys/module/cpu_boost/parameters/input_boost_freq
	lock_value 4 /sys/devices/system/cpu/cpu4/core_ctl/min_cpus
	lock_value 4 /sys/devices/system/cpu/cpu4/core_ctl/max_cpus
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
	expected_target=${C0_GOVERNOR_DIR}/hispeed_freq
	if [ "$action" = "powersave" ]; then
		expected_value="1180000"
	elif [ "$action" = "balance" ]; then
		expected_value="1280000"
	elif [ "$action" = "performance" ]; then
		expected_value="1380000"
	elif [ "$action" = "fast" ]; then
		expected_value="1480000"
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
	echo "EAS parameter adjustment for SDM 845"
	echo "https://github.com/yc9559/cpufreq-interactive-opt"
	echo "Author: yc9559"
	echo "Generated at: Sat Jun 30 12:28:56 2018"
	echo ""
	print_value "big: max_freq" ${C1_CPUFREQ_DIR}/scaling_max_freq
	print_param hispeed_freq
	print_param pl
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
fi

if [ "$action" = "powersave" ]; then
	powersave_custom
	set_param_little hispeed_freq 1180000
	set_param_little hispeed_load 90
	set_param_little pl 0
	set_param_big hispeed_freq 1080000
	set_param_big hispeed_load 90
	set_param_big pl 0
fi

if [ "$action" = "balance" ]; then
	balance_custom
	set_param_little hispeed_freq 1280000
	set_param_little hispeed_load 90
	set_param_little pl 0
	set_param_big hispeed_freq 1280000
	set_param_big hispeed_load 90
	set_param_big pl 0
fi

if [ "$action" = "performance" ]; then
	performance_custom
	set_param_little hispeed_freq 1380000
	set_param_little hispeed_load 90
	set_param_little pl 1
	set_param_big hispeed_freq 1480000
	set_param_big hispeed_load 95
	set_param_big pl 1
fi

if [ "$action" = "fast" ]; then
	fast_custom
	set_param_little hispeed_freq 1480000
	set_param_little hispeed_load 85
	set_param_little pl 1
	set_param_big hispeed_freq 1480000
	set_param_big hispeed_load 90
	set_param_big pl 1
fi

after_modify

exit 0