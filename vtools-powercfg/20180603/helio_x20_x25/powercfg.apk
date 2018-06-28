#!/system/bin/sh
# Project WIPE https://github.com/yc9559/cpufreq-interactive-opt
# Author: yc9559
# Platform: helio_x20_x25
# Generated at: Thu Jun 28 06:18:15 2018

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
	# in case of using ondemand as default governor
	lock_value "interactive" ${C0_CPUFREQ_DIR}/scaling_governor
}

function runonce_custom()
{
	# CORE CONTROL
	lock_value 40 /proc/hps/down_threshold
	# avoid permission problem, do not set 0444
	set_value 2-3 /dev/cpuset/background/cpus
	set_value 0-3 /dev/cpuset/system-background/cpus
	set_value 0-3,4-7,8 /dev/cpuset/foreground/cpus
	set_value 0-3,4-7,8 /dev/cpuset/top-app/cpus
}

function before_modify()
{
	chown 0.0 ${C0_GOVERNOR_DIR}/*
	chmod 0666 ${C0_GOVERNOR_DIR}/*
	lock_value 280000 ${C0_CPUFREQ_DIR}/scaling_min_freq
}

function after_modify()
{
	chmod 0444 ${C0_GOVERNOR_DIR}/*
	verify_param
}

function powersave_custom()
{
	lock_value 90 /proc/hps/up_threshold
	lock_value "2 2 0" /proc/hps/num_base_perf_serv
}

function balance_custom()
{
	lock_value 80 /proc/hps/up_threshold
	lock_value "3 3 0" /proc/hps/num_base_perf_serv
}

function performance_custom()
{
	lock_value 70 /proc/hps/up_threshold
	lock_value "3 3 1" /proc/hps/num_base_perf_serv
}

function fast_custom()
{
	lock_value 60 /proc/hps/up_threshold
	lock_value "4 4 1" /proc/hps/num_base_perf_serv
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
		expected_value="80 380000:15 480000:25 780000:36 880000:80 980000:66 1180000:91 1280000:96"
	elif [ "$action" = "balance" ]; then
		expected_value="80 380000:8 580000:14 680000:9 780000:41 880000:56 1080000:65 1180000:92 1380000:85 1480000:97"
	elif [ "$action" = "performance" ]; then
		expected_value="80 380000:10 780000:57 1080000:27 1180000:65 1280000:82 1380000:6 1480000:80 1580000:98"
	elif [ "$action" = "fast" ]; then
		expected_value="80 1780000:90"
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
	echo "Platform: helio_x20_x25"
	echo "Generated at: Thu Jun 28 06:18:15 2018"
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
	set_param_little above_hispeed_delay "18000 1380000:98000"
	set_param_little hispeed_freq 1180000
	set_param_little go_hispeed_load 94
	set_param_little target_loads "80 380000:15 480000:25 780000:36 880000:80 980000:66 1180000:91 1280000:96"
	set_param_little min_sample_time 18000
	set_param_big above_hispeed_delay "18000 1380000:98000"
	set_param_big hispeed_freq 1180000
	set_param_big go_hispeed_load 94
	set_param_big target_loads "80 380000:15 480000:25 780000:36 880000:80 980000:66 1180000:91 1280000:96"
	set_param_big min_sample_time 18000
fi

if [ "$action" = "balance" ]; then
	balance_custom
	set_param_little above_hispeed_delay "18000 1380000:98000"
	set_param_little hispeed_freq 1180000
	set_param_little go_hispeed_load 93
	set_param_little target_loads "80 380000:8 580000:14 680000:9 780000:41 880000:56 1080000:65 1180000:92 1380000:85 1480000:97"
	set_param_little min_sample_time 18000
	set_param_big above_hispeed_delay "18000 1380000:98000"
	set_param_big hispeed_freq 1180000
	set_param_big go_hispeed_load 93
	set_param_big target_loads "80 380000:8 580000:14 680000:9 780000:41 880000:56 1080000:65 1180000:92 1380000:85 1480000:97"
	set_param_big min_sample_time 18000
fi

if [ "$action" = "performance" ]; then
	performance_custom
	set_param_little above_hispeed_delay "18000 1380000:58000 1480000:98000 1680000:38000"
	set_param_little hispeed_freq 1180000
	set_param_little go_hispeed_load 85
	set_param_little target_loads "80 380000:10 780000:57 1080000:27 1180000:65 1280000:82 1380000:6 1480000:80 1580000:98"
	set_param_little min_sample_time 18000
	set_param_big above_hispeed_delay "18000 1380000:58000 1480000:98000 1680000:38000"
	set_param_big hispeed_freq 1180000
	set_param_big go_hispeed_load 85
	set_param_big target_loads "80 380000:10 780000:57 1080000:27 1180000:65 1280000:82 1380000:6 1480000:80 1580000:98"
	set_param_big min_sample_time 18000
fi

if [ "$action" = "fast" ]; then
	fast_custom
	lock_value 1280000 ${C0_CPUFREQ_DIR}/scaling_min_freq
	set_param_little above_hispeed_delay "18000 1680000:198000"
	set_param_little hispeed_freq 1280000
	set_param_little target_loads "80 1780000:90"
	set_param_little min_sample_time 38000
	lock_value 1280000 ${C1_CPUFREQ_DIR}/scaling_min_freq
	set_param_big above_hispeed_delay "18000 1680000:198000"
	set_param_big hispeed_freq 1280000
	set_param_big target_loads "80 1780000:90"
	set_param_big min_sample_time 38000
fi

after_modify

exit 0