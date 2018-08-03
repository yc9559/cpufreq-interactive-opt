#coding:utf-8

import random
import multiprocessing
import time

from array import array
from deap import base
from deap import creator
from deap import tools
from deap.benchmarks.tools import diversity, convergence

from modules import *

def generate_param(enable_random):
    if not enable_random:
        return array('i', DEFAULT_PARAM)
    else:
        param_seq = array('i')
        # above_hispeed_delay
        for i in range(ABOVE_LEVELS):
            param_seq.append(random.randint(above_i[0], above_i[1]))
        # boostpulse_duration
        param_seq.append(random.randint(boostpulse_i[0], boostpulse_i[1]))
        # go_hispeed
        param_seq.append(random.randint(go_i[0], go_i[1]))
        # hispeed_freq
        param_seq.append(random.randint(hispeed_i[0], hispeed_i[1]))
        # min_sampling_time
        param_seq.append(random.randint(min_i[0], min_i[1]))
        # target_loads
        for i in range(TARGETLOADS_LEVELS):
            param_seq.append(random.randint(loads_i[0], loads_i[1]))
        return param_seq

def nsga2vm(seed=None):
    random.seed(seed)
    
    # first weight means smaller better, second weight means bigger is better
    creator.create("FitnessMin", base.Fitness, weights=(-1.0, 1.0, -1.0))
    creator.create("Individual", array, typecode='i', fitness=creator.FitnessMin)
    
    toolbox = base.Toolbox()
    # register methods to toolbox
    toolbox.register("attr_int", generate_param, INIT_RANDOM)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr_int)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", interactive_benchmark, ap_env=ap_env)
    toolbox.register("mate", cxSimulatedBinaryBoundedINT, eta=ETA_MATE)
    toolbox.register("mutate", mutPolynomialBoundedINT, eta=ETA_MUTATE, indpb=1.0/NDIM)
    toolbox.register("select", tools.selNSGA2, nd='log')

    # use multithreading
    if CPU_THREAD > 1:
        pool = multiprocessing.Pool(processes = CPU_THREAD)
        toolbox.register("map", pool.map)

    pop = toolbox.population(n=MU)
    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # This is just to assign the crowding distance to the individuals
    # no actual selection is done
    pop = toolbox.select(pop, len(pop))

    # display xxxx/4000 and remaining time
    progress = ProgressDisplay(NGEN)

    # Begin the generational process
    for gen in range(NGEN):
        if gen == EXIT_INCUBATION_NGEN:
            ap_env.is_incubating = False
        if gen % 10 == 0:
            progress.display_progress(gen)
            if WORKLOAD_SIGMA > 0:
                ap_env.workload_shuffle_noise(WORKLOAD_SIGMA)
            if IDLELOAD_SIGMA > 0:
                ap_env.idleload_shuffle_noise(IDLELOAD_SIGMA)

        # Vary the population
        offspring = tools.selTournamentDCD(pop, N_OFFSPRING)
        offspring = [toolbox.clone(ind) for ind in offspring]
        
        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)
            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Select the next generation population
        pop = toolbox.select(pop + offspring, MU)
    
    if CPU_THREAD > 1:
        pool.close()
        pool.join()
        pool.terminate()
    return pop
        
if __name__ == "__main__":
    shmgr = ShellManager()
    for ap_name in todolist:
        print ap_name
        start_time = time.time()

        ap_env = Simulation(ap_name, WORKLOAD_FILE, STANDBY_FILE) 
        # use fixed random seed to produce repeatable results
        pop = nsga2vm(seed=FIXED_SEED)
        top50 = tools.selBest(pop, k=MU)
        test_env = Simulation(ap_name, WORKLOAD_FILE, STANDBY_FILE) 
        test_env.is_incubating = False
        log_NSGA2_result(top50, test_env)
        best3 = find_collection(top50, test_env)
        log_collection(top50, test_env, collection=best3)
        shmgr.write_shell(best3, test_env)
        print ''
        print 'finished in: ' + str(int(time.time()-start_time)) + ' seconds'
        print ''
        # avoid 7500u TDP throttle to 10 walt
        # time.sleep(30)