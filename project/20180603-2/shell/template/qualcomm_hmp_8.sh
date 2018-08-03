#!/system/bin/sh
# [project_name] [github_url]
# Author: [yourname]
# Platform: [platform_name]
# Generated at: [generated_time]

C0_GOVERNOR_DIR="/sys/devices/system/cpu/cpufreq/interactive"
C1_GOVERNOR_DIR=""
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
	# Perfd, nothing to worry about, if error the script will continue
	stop perfd
}

function runonce_custom()
{
	set_value [sched_spill_load] /proc/sys/kernel/sched_spill_load
	set_value [sched_boost] /proc/sys/kernel/sched_boost
	set_value [sched_prefer_sync_wakee_to_waker] /proc/sys/kernel/sched_prefer_sync_wakee_to_waker
	set_value [sched_init_task_load] /proc/sys/kernel/sched_init_task_load
	set_value [sched_freq_inc_notify] /proc/sys/kernel/sched_freq_inc_notify

	# avoid permission problem, do not set 0444
	set_value 2-3 /dev/cpuset/background/cpus
	set_value 0-3 /dev/cpuset/system-background/cpus
	set_value 0-3,4-7 /dev/cpuset/foreground/cpus
	set_value 0-3,4-7 /dev/cpuset/top-app/cpus

	set_value 25 /proc/sys/kernel/sched_downmigrate
	set_value 45 /proc/sys/kernel/sched_upmigrate

	lock_value [input_boost_ms] /sys/module/cpu_boost/parameters/input_boost_ms
	lock_value 0 /sys/module/msm_performance/parameters/touchboost

	set_param_little use_sched_load [use_sched_load]
	lock_value [ignore_hispeed_on_notif] ${C0_GOVERNOR_DIR}/ignore_hispeed_on_notif
	lock_value [enable_prediction] ${C0_GOVERNOR_DIR}/enable_prediction
}

function before_modify()
{
	chown 0.0 ${C0_GOVERNOR_DIR}/*
	chmod 0666 ${C0_GOVERNOR_DIR}/*
	lock_value [uni_min_freq] ${C0_CPUFREQ_DIR}/scaling_min_freq
	set_value 1 /sys/devices/system/cpu/cpu4/online
}

function after_modify()
{
	chmod 0444 ${C0_GOVERNOR_DIR}/*
	verify_param
}

function powersave_custom()
{
	lock_value "0:[powersave_uni_input_boost_freq]" /sys/module/cpu_boost/parameters/input_boost_freq
}

function balance_custom()
{
	lock_value "0:[balance_uni_input_boost_freq]" /sys/module/cpu_boost/parameters/input_boost_freq
}

function performance_custom()
{
	lock_value "0:[performance_uni_input_boost_freq]" /sys/module/cpu_boost/parameters/input_boost_freq
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
		expected_value="[powersave_uni_target_loads]"
	elif [ "$action" = "balance" ]; then
		expected_value="[balance_uni_target_loads]"
	elif [ "$action" = "performance" ]; then
		expected_value="[performance_uni_target_loads]"
	elif [ "$action" = "fast" ]; then
		expected_value="[fast_uni_target_loads]"
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
	echo "[project_name] [github_url]"
	echo "Author: [yourname]"
	echo "Platform: [platform_name]"
	echo "Generated at: [generated_time]"
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
	set_param_little timer_rate [timer_rate]
	set_param_little timer_slack [timer_slack]
	set_param_little boost 0
	set_param_little boostpulse_duration [boostpulse_duration]
	set_param_big timer_rate [timer_rate]
	set_param_big timer_slack [timer_slack]
	set_param_big boost 0
	set_param_big boostpulse_duration [boostpulse_duration]
fi

if [ "$action" = "powersave" ]; then
	powersave_custom
	set_param_little above_hispeed_delay "[powersave_uni_above_hispeed_delay]"
	set_param_little hispeed_freq [powersave_uni_hispeed_freq]
	set_param_little go_hispeed_load [powersave_uni_go_hispeed_load]
	set_param_little target_loads "[powersave_uni_target_loads]"
	set_param_little min_sample_time [powersave_uni_min_sample_time]
	set_param_big above_hispeed_delay "[powersave_uni_above_hispeed_delay]"
	set_param_big hispeed_freq [powersave_uni_hispeed_freq]
	set_param_big go_hispeed_load [powersave_uni_go_hispeed_load]
	set_param_big target_loads "[powersave_uni_target_loads]"
	set_param_big min_sample_time [powersave_uni_min_sample_time]
fi

if [ "$action" = "balance" ]; then
	balance_custom
	set_param_little above_hispeed_delay "[balance_uni_above_hispeed_delay]"
	set_param_little hispeed_freq [balance_uni_hispeed_freq]
	set_param_little go_hispeed_load [balance_uni_go_hispeed_load]
	set_param_little target_loads "[balance_uni_target_loads]"
	set_param_little min_sample_time [balance_uni_min_sample_time]
	set_param_big above_hispeed_delay "[balance_uni_above_hispeed_delay]"
	set_param_big hispeed_freq [balance_uni_hispeed_freq]
	set_param_big go_hispeed_load [balance_uni_go_hispeed_load]
	set_param_big target_loads "[balance_uni_target_loads]"
	set_param_big min_sample_time [balance_uni_min_sample_time]
fi

if [ "$action" = "performance" ]; then
	performance_custom
	set_param_little above_hispeed_delay "[performance_uni_above_hispeed_delay]"
	set_param_little hispeed_freq [performance_uni_hispeed_freq]
	set_param_little go_hispeed_load [performance_uni_go_hispeed_load]
	set_param_little target_loads "[performance_uni_target_loads]"
	set_param_little min_sample_time [performance_uni_min_sample_time]
	set_param_big above_hispeed_delay "[performance_uni_above_hispeed_delay]"
	set_param_big hispeed_freq [performance_uni_hispeed_freq]
	set_param_big go_hispeed_load [performance_uni_go_hispeed_load]
	set_param_big target_loads "[performance_uni_target_loads]"
	set_param_big min_sample_time [performance_uni_min_sample_time]
fi

if [ "$action" = "fast" ]; then
	fast_custom
	lock_value [fast_uni_hispeed_freq] ${C0_CPUFREQ_DIR}/scaling_min_freq
	set_param_little above_hispeed_delay "[fast_uni_above_hispeed_delay]"
	set_param_little hispeed_freq [fast_uni_hispeed_freq]
	set_param_little target_loads "[fast_uni_target_loads]"
	set_param_little min_sample_time 38000
	lock_value [fast_uni_hispeed_freq] ${C1_CPUFREQ_DIR}/scaling_min_freq
	set_param_big above_hispeed_delay "[fast_uni_above_hispeed_delay]"
	set_param_big hispeed_freq [fast_uni_hispeed_freq]
	set_param_big target_loads "[fast_uni_target_loads]"
	set_param_big min_sample_time 38000
fi

after_modify

exit 0