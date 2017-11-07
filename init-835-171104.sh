#!/system/bin/sh
# Copyright (c) 2012-2013, 2016, The Linux Foundation. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of The Linux Foundation nor
#       the names of its contributors may be used to endorse or promote
#       products derived from this software without specific prior written
#       permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NON-INFRINGEMENT ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# @Author:	Matt Yang 
# @Date:	2017-11-06 09:04:29 
# cpufreq interactive profile for Qualcomm Snapdragon 835
# LITTLE:   1104 performance
# big:      1104 balanced

target=`getprop ro.board.platform`

case "$target" in
    "msm8998")

	echo 2 > /sys/devices/system/cpu/cpu4/core_ctl/min_cpus
	# echo 60 > /sys/devices/system/cpu/cpu4/core_ctl/busy_up_thres
	echo 70 > /sys/devices/system/cpu/cpu4/core_ctl/busy_up_thres
	echo 30 > /sys/devices/system/cpu/cpu4/core_ctl/busy_down_thres
	echo 100 > /sys/devices/system/cpu/cpu4/core_ctl/offline_delay_ms
	echo 1 > /sys/devices/system/cpu/cpu4/core_ctl/is_big_cluster
	echo 4 > /sys/devices/system/cpu/cpu4/core_ctl/task_thres

	# Setting b.L scheduler parameters
	echo 1 > /proc/sys/kernel/sched_migration_fixup
	echo 95 > /proc/sys/kernel/sched_upmigrate
	echo 90 > /proc/sys/kernel/sched_downmigrate
	echo 100 > /proc/sys/kernel/sched_group_upmigrate
	echo 95 > /proc/sys/kernel/sched_group_downmigrate
	echo 0 > /proc/sys/kernel/sched_select_prev_cpu_us
	echo 400000 > /proc/sys/kernel/sched_freq_inc_notify
	echo 400000 > /proc/sys/kernel/sched_freq_dec_notify
	echo 5 > /proc/sys/kernel/sched_spill_nr_run
	echo 1 > /proc/sys/kernel/sched_restrict_cluster_spill
	#start iop

        # disable thermal bcl hotplug to switch governor
        chmod 0644 /sys/module/msm_thermal/core_control/enabled
        echo 0 > /sys/module/msm_thermal/core_control/enabled
        chmod 0444 /sys/module/msm_thermal/core_control/enabled

    # from init.rc in xiaomi mi 6
    chown root root /sys/devices/root/cpu/cpufreq/interactive/timer_rate
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/timer_rate
    chown root root /sys/devices/root/cpu/cpufreq/interactive/timer_slack
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/timer_slack
    chown root root /sys/devices/root/cpu/cpufreq/interactive/min_sample_time
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/min_sample_time
    chown root root /sys/devices/root/cpu/cpufreq/interactive/hispeed_freq
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/hispeed_freq
    chown root root /sys/devices/root/cpu/cpufreq/interactive/target_loads
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/target_loads
    chown root root /sys/devices/root/cpu/cpufreq/interactive/go_hispeed_load
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/go_hispeed_load
    chown root root /sys/devices/root/cpu/cpufreq/interactive/above_hispeed_delay
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/above_hispeed_delay
    chown root root /sys/devices/root/cpu/cpufreq/interactive/boost
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/boost
    chown root root /sys/devices/root/cpu/cpufreq/interactive/boostpulse
    chown root root /sys/devices/root/cpu/cpufreq/interactive/input_boost
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/input_boost
    chown root root /sys/devices/root/cpu/cpufreq/interactive/boostpulse_duration
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/boostpulse_duration
    chown root root /sys/devices/root/cpu/cpufreq/interactive/io_is_busy
    chmod 0660 /sys/devices/root/cpu/cpufreq/interactive/io_is_busy

        # online CPU0
        echo 1 > /sys/devices/system/cpu/cpu0/online
	# configure governor settings for little cluster
	echo "interactive" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
    chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/use_sched_load
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/use_migration_notif
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/above_hispeed_delay
    chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/boostpulse_duration
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/go_hispeed_load
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/timer_rate
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/hispeed_freq
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/io_is_busy
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/target_loads
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/min_sample_time
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/max_freq_hysteresis
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
	chmod 0644 /sys/devices/system/cpu/cpu0/cpufreq/interactive/ignore_hispeed_on_notif
	echo 1 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/use_sched_load
	echo 0 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/use_migration_notif
	echo "19000 1600000:99000" > /sys/devices/system/cpu/cpu0/cpufreq/interactive/above_hispeed_delay
    echo 19000 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/boostpulse_duration
	echo 97 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/go_hispeed_load
	echo 20000 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/timer_rate
	echo 1248000 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/hispeed_freq
	echo 0 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/io_is_busy
	echo "40 400000:2 550000:60 800000:37 1000000:52 1200000:77 1400000:72 1600000:73 1800000:96" > /sys/devices/system/cpu/cpu0/cpufreq/interactive/target_loads
	echo 19000 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/min_sample_time
	echo 19000 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/max_freq_hysteresis
	echo 300000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
	echo 0 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/ignore_hispeed_on_notif
    chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/use_sched_load
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/use_migration_notif
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/above_hispeed_delay
    chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/boostpulse_duration
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/go_hispeed_load
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/timer_rate
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/hispeed_freq
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/io_is_busy
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/target_loads
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/min_sample_time
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/max_freq_hysteresis
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
	chmod 0444 /sys/devices/system/cpu/cpu0/cpufreq/interactive/ignore_hispeed_on_notif

        # online CPU4
        echo 1 > /sys/devices/system/cpu/cpu4/online
	# configure governor settings for big cluster
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/scaling_governor
    chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/use_sched_load
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/use_migration_notif
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/above_hispeed_delay
    chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/boostpulse_duration
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/go_hispeed_load
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/timer_rate
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/hispeed_freq
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/io_is_busy
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/target_loads
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/min_sample_time
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/max_freq_hysteresis
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/scaling_min_freq
	chmod 0644 /sys/devices/system/cpu/cpu4/cpufreq/interactive/ignore_hispeed_on_notif
	echo 1 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/use_sched_load
	echo 1 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/use_migration_notif
	echo "19000 1550000:99000 1900000:299000" > /sys/devices/system/cpu/cpu4/cpufreq/interactive/above_hispeed_delay
    echo 19000 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/boostpulse_duration
	echo 97 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/go_hispeed_load
	echo 20000 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/timer_rate
	echo 1248000 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/hispeed_freq
	echo 1 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/io_is_busy
	echo "88 400000:2 600000:41 800000:82 1000000:69 1200000:75 1400000:77 1550000:83 1800000:98" > /sys/devices/system/cpu/cpu4/cpufreq/interactive/target_loads
	echo 19000 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/min_sample_time
	echo 19000 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/max_freq_hysteresis
	echo 300000 > /sys/devices/system/cpu/cpu4/cpufreq/scaling_min_freq
	echo 0 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/ignore_hispeed_on_notif
    chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/scaling_governor
    chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/use_sched_load
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/use_migration_notif
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/above_hispeed_delay
    chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/boostpulse_duration
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/go_hispeed_load
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/timer_rate
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/hispeed_freq
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/io_is_busy
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/target_loads
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/min_sample_time
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/max_freq_hysteresis
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/scaling_min_freq
	chmod 0444 /sys/devices/system/cpu/cpu4/cpufreq/interactive/ignore_hispeed_on_notif

        # re-enable thermal and BCL hotplug
        chmod 0644 /sys/module/msm_thermal/core_control/enabled
        echo 1 > /sys/module/msm_thermal/core_control/enabled
        chmod 0444 /sys/module/msm_thermal/core_control/enabled

        # Enable input boost configuration
        echo "0:1324800" > /sys/module/cpu_boost/parameters/input_boost_freq
        echo 0 > /sys/module/cpu_boost/parameters/input_boost_ms
        echo "0:0 1:0 2:0 3:0 4:2208000 5:0 6:0 7:0" > /sys/module/cpu_boost/parameters/powerkey_input_boost_freq
        echo 400 > /sys/module/cpu_boost/parameters/powerkey_input_boost_ms

    # from init.rc in xiaomi mi 6 for recovery
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/timer_rate
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/timer_rate
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/timer_slack
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/timer_slack
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/min_sample_time
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/min_sample_time
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/hispeed_freq
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/hispeed_freq
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/target_loads
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/target_loads
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/go_hispeed_load
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/go_hispeed_load
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/above_hispeed_delay
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/above_hispeed_delay
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/boost
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/boost
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/boostpulse
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/input_boost
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/input_boost
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/boostpulse_duration
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/boostpulse_duration
    # chown system system /sys/devices/system/cpu/cpufreq/interactive/io_is_busy
    # chmod 0660 /sys/devices/system/cpu/cpufreq/interactive/io_is_busy

        echo 0 > /dev/cpuset/background/cpus
        echo 0-2 > /dev/cpuset/system-background/cpus
        echo 4-7 > /dev/cpuset/foreground/boost/cpus
        # echo 0-2,4-7 > /dev/cpuset/foreground/cpus
        echo 0-2,4-6 > /dev/cpuset/foreground/cpus
        echo 0 > /proc/sys/kernel/sched_boost
    ;;
esac

