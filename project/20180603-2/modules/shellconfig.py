#coding:utf-8

import time, re, os, shutil
from conf import *
from logger import *
from interactive import InteractiveParamSeq, freq_to_table

class ParamToReplace(object):
    def __init__(self, ap_env, collection):
        ap_env_name = ap_env.model_name.split('_')
        ap_type = ap_env_name[-1]
        ap_name = SHELL_MODEL_DICT[ap_env_name[0]]['sku_name']
        self.todo = list()
        self.todo.extend(SHARED_SHELL_PARAM)
        self.todo.append(['platform_name', ap_name])
        self.todo.append(['generated_time', time.asctime()])
        self.todo.append([ap_type+'_min_freq', freq_to_hz(ap_env.min_freq)])

        class_list = ['performance', 'balance', 'powersave']
        cat_seq = zip(class_list, collection)
        for class_name, choice in cat_seq:
            ref_score = choice[0]
            param_seq = choice[2]
            p = InteractiveParamSeq(param_seq, ap_env.freq_table)
            prefix = class_name+'_'+ap_type+'_'
            self.todo.append([prefix+'above_hispeed_delay', above_to_str(p, ap_env, ref_score)])
            self.todo.append([prefix+'hispeed_freq',        freq_to_hz(p.hispeed_freq)])
            self.todo.append([prefix+'go_hispeed_load',     p.go_hispeed])
            self.todo.append([prefix+'target_loads',        tgload_to_str(p, ap_env)])
            self.todo.append([prefix+'min_sample_time',     period_to_ns(p.min_sampling_time)])
            # self.todo.append([prefix+'boostpulse_duration', period_to_ns(p.boostpulse_duration)])
            # if ap_type == 'b':  self.todo.append([prefix+'input_boost_freq', 0])
            # else:               self.todo.append([prefix+'input_boost_freq', freq_to_hz(ap_env.enough_capacity/100)])
            # self.todo.append([prefix+'input_boost_freq', freq_to_hz(p.hispeed_freq)])
            # change min-freq 0.3g->0.4g for a long time
            self.todo.append([prefix+'input_boost_freq', freq_to_hz(ap_env.freq_table[ap_env.min_freq])])    
        
        # low latency mode
        lower_max_freq  = ceiling_match_freq(ap_env.max_freq-1, ap_env.freq_table)
        lower_enough_freq = ceiling_match_freq(ap_env.enough_capacity/100-2, ap_env.freq_table)
        fast_tgload_str = "80 %i:90" %(freq_to_hz(ap_env.max_freq))
        fast_above_str  = "18000 %i:198000" %(freq_to_hz(lower_max_freq))
        self.todo.append(['fast_'+ap_type+'_above_hispeed_delay', fast_above_str])
        self.todo.append(['fast_'+ap_type+'_hispeed_freq', freq_to_hz(lower_enough_freq)])
        self.todo.append(['fast_'+ap_type+'_target_loads', fast_tgload_str])


class ShellManager(object):
    def __init__(self,):
        self.start_time = time.strftime('%Y-%m-%d %H%M%S', time.localtime())
        self.output_base = SHELL_BASE_DIR + 'output/' + self.start_time + '/'
        self.done_record = dict()
        os.mkdir(self.output_base)

    def file_re_replace(self, path, param_to_replace):
        to_replace = param_to_replace.todo
        replaced_string = ''
        with open(path, 'r') as templatefile:
            lines = list()
            for line in templatefile:
                lines.append(line)
            replaced_string = ''.join(lines)
        patterns = [re.escape('['+ x[0] +']') for x in to_replace]
        repls = [str(x[1]) for x in to_replace]
        for i in range(len(patterns)):
            replaced_string = re.sub(patterns[i], repls[i], replaced_string)
        with open(path, 'w') as shellfile:
            shellfile.write(replaced_string)
        return 0
        
    def write_shell(self, best3, ap_env):
        model = ap_env.model_name.split('_')[0]
        out_dir = self.output_base + SHELL_MODEL_DICT[model]['sku_name']
        outpath = out_dir + '/powercfg.apk'
        if model not in self.done_record:
            template_path = SHELL_BASE_DIR + 'template/' + SHELL_MODEL_DICT[model]['template']
            os.mkdir(out_dir)
            shutil.copy(template_path, outpath)
            self.done_record[model] = True
        to_repl = ParamToReplace(ap_env, best3)
        self.file_re_replace(outpath, to_repl)
        print ap_env.model_name + ' shell generated'
        return 0


SHELL_MODEL_DICT = {
    's835': {
        'sku_name': 'sd_835',
        'template': 'qualcomm_hmp_4+4.sh',
    },
    's821': {
        'sku_name': 'sd_820_821',
        'template': 'qualcomm_hmp_2+2.sh',
    },
    's810': {
        'sku_name': 'sd_810_808',
        'template': 'qualcomm_hmp_4+4_810.sh',
    },
    's801': {
        'sku_name': 'sd_801_800_805',
        'template': 'qualcomm_asmp.sh',
    },
    's660': {
        'sku_name': 'sd_660',
        'template': 'qualcomm_hmp_4+4.sh',
    },
    's650': {
        'sku_name': 'sd_652_650',
        'template': 'qualcomm_hmp_4+4.sh',
    },
    's636': {
        'sku_name': 'sd_636',
        'template': 'qualcomm_hmp_4+4.sh',
    },
    's625': {
        'sku_name': 'sd_625_626',
        'template': 'qualcomm_hmp_8.sh',
    },
    'e8895': {
        'sku_name': 'exynos_8895',
        'template': 'universial_hmp_4+4.sh',
    },
    'e8890': {
        'sku_name': 'exynos_8890',
        'template': 'universial_hmp_4+4.sh',
    },
    'e7420': {
        'sku_name': 'exynos_7420',
        'template': 'universial_hmp_4+4.sh',
    },
    'k950': {
        'sku_name': 'kirin_950_955',
        'template': 'universial_hmp_4+4.sh',
    },
    'k960': {
        'sku_name': 'kirin_960',
        'template': 'universial_hmp_4+4.sh',
    },
    'k970': {
        'sku_name': 'kirin_970',
        'template': 'universial_hmp_4+4.sh',
    },
    'z3560': {
        'sku_name': 'atom_z3560_z3580',
        'template': 'universial_smp.sh',
    },
    'mt6797': {
        'sku_name': 'helio_x20_x25',
        'template': 'mtk_hmp_3cluster.sh',
    },
    'mt6795': {
        'sku_name': 'helio_x10',
        'template': 'mtk_hmp_2cluster.sh',
    },
}


SHARED_SHELL_PARAM = [
    ['project_name', 'Project WIPE'],
    ['github_url', 'https://github.com/yc9559/cpufreq-interactive-opt'],
    ['yourname', 'yc9559'],
    ['sched_boost', 0],
    ['sched_prefer_sync_wakee_to_waker', 1],
    ['sched_init_task_load', 40],
    ['sched_spill_load', 90],
    ['sched_freq_inc_notify', 3000000],
    ['input_boost_ms', 2500],     # keep min-freq adjustment for 2500ms, touch latency is about 50-80ms, from kernel to draw
    ['timer_rate', 20000],
    ['timer_slack', 180000],
    ['boostpulse_duration', 0],
    ['io_is_busy', 0],
    ['use_sched_load', 1],
    ['ignore_hispeed_on_notif', 0],
    ['enable_prediction', 0]
]
