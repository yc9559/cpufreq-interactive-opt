import random
from interactive import *

def cxSimulatedBinaryBoundedINT(ind1, ind2, eta):
    """Executes a simulated binary crossover that modify in-place the input
    individuals. The simulated binary crossover expects :term:`sequence`
    individuals of floating point numbers.
    
    :param ind1: The first individual participating in the crossover.
    :param ind2: The second individual participating in the crossover.
    :param eta: Crowding degree of the crossover. A high eta will produce
                children resembling to their parents, while a small eta will
                produce solutions much more different.
    :param low: A value or an :term:`python:sequence` of values that is the lower
                bound of the search space.
    :param up: A value or an :term:`python:sequence` of values that is the upper
               bound of the search space.
    :returns: A tuple of two individuals.

    This function uses the :func:`~random.random` function from the python base
    :mod:`random` module.

    .. note::
       This implementation is similar to the one implemented in the 
       original NSGA-II C code presented by Deb.
    """
    low = zip(  above_i, above_i, above_i, above_i, above_i, 
                above_i, above_i, above_i, above_i, above_i, 
                boostpulse_i, go_i, hispeed_i, min_i, 
                loads_i, loads_i, loads_i, loads_i, loads_i, 
                loads_i, loads_i, loads_i, loads_i, loads_i
                )[0]
    up = zip(   above_i, above_i, above_i, above_i, above_i, 
                above_i, above_i, above_i, above_i, above_i, 
                boostpulse_i, go_i, hispeed_i, min_i, 
                loads_i, loads_i, loads_i, loads_i, loads_i, 
                loads_i, loads_i, loads_i, loads_i, loads_i
                )[1]

    size = min(len(ind1), len(ind2))
    # if not isinstance(low, Sequence):
    #     low = repeat(low, size)
    # elif len(low) < size:
    #     raise IndexError("low must be at least the size of the shorter individual: %d < %d" % (len(low), size))
    # if not isinstance(up, Sequence):
    #     up = repeat(up, size)
    # elif len(up) < size:
    #     raise IndexError("up must be at least the size of the shorter individual: %d < %d" % (len(up), size))
    
    for i, xl, xu in zip(xrange(size), low, up):
        if random.random() <= 0.5:
            # This epsilon should probably be changed for 0 since 
            # floating point arithmetic in Python is safer
            # if abs(ind1[i] - ind2[i]) > 1e-14:
            if abs(ind1[i] - ind2[i]) > 0:
                x1_i =  min(ind1[i], ind2[i])
                x2_i = max(ind1[i], ind2[i])
                x1 = float(x1_i)
                x2 = float(x2_i)
                rand = random.random()
                
                beta = 1.0 + (2.0 * (x1 - xl) / (x2 - x1))
                alpha = 2.0 - beta**-(eta + 1)
                if rand <= 1.0 / alpha:
                    beta_q = (rand * alpha)**(1.0 / (eta + 1))
                else:
                    beta_q = (1.0 / (2.0 - rand * alpha))**(1.0 / (eta + 1))
                
                c1 = 0.5 * (x1 + x2 - beta_q * (x2 - x1))
                
                beta = 1.0 + (2.0 * (xu - x2) / (x2 - x1))
                alpha = 2.0 - beta**-(eta + 1)
                if rand <= 1.0 / alpha:
                    beta_q = (rand * alpha)**(1.0 / (eta + 1))
                else:
                    beta_q = (1.0 / (2.0 - rand * alpha))**(1.0 / (eta + 1))
                c2 = 0.5 * (x1 + x2 + beta_q * (x2 - x1))
                
                c1 = min(max(c1, xl), xu)
                c2 = min(max(c2, xl), xu)
                c1_i = int(c1)
                c2_i = int(c2)
                
                if random.random() <= 0.5:
                    ind1[i] = c2_i
                    ind2[i] = c1_i
                else:
                    ind1[i] = c1_i
                    ind2[i] = c2_i
    
    return ind1, ind2   

def mutPolynomialBoundedINT(individual, eta, indpb):
    """Polynomial mutation as implemented in original NSGA-II algorithm in
    C by Deb.
    
    :param individual: :term:`Sequence <sequence>` individual to be mutated.
    :param eta: Crowding degree of the mutation. A high eta will produce
                a mutant resembling its parent, while a small eta will
                produce a solution much more different.
    :param low: A value or a :term:`python:sequence` of values that
                is the lower bound of the search space.
    :param up: A value or a :term:`python:sequence` of values that
               is the upper bound of the search space.
    :returns: A tuple of one individual.
    """
    size = len(individual)
    # if not isinstance(low, Sequence):
    #     low = repeat(low, size)
    # elif len(low) < size:
    #     raise IndexError("low must be at least the size of individual: %d < %d" % (len(low), size))
    # if not isinstance(up, Sequence):
    #     up = repeat(up, size)
    # elif len(up) < size:
    #     raise IndexError("up must be at least the size of individual: %d < %d" % (len(up), size))
    low = zip(  above_i, above_i, above_i, above_i, above_i, 
                above_i, above_i, above_i, above_i, above_i, 
                boostpulse_i, go_i, hispeed_i, min_i, 
                loads_i, loads_i, loads_i, loads_i, loads_i, 
                loads_i, loads_i, loads_i, loads_i, loads_i
                )[0]
    up = zip(   above_i, above_i, above_i, above_i, above_i, 
                above_i, above_i, above_i, above_i, above_i, 
                boostpulse_i, go_i, hispeed_i, min_i, 
                loads_i, loads_i, loads_i, loads_i, loads_i, 
                loads_i, loads_i, loads_i, loads_i, loads_i
                )[1]
    
    for i, xl, xu in zip(range(size), low, up):
        if random.random() <= indpb:
            x_i = individual[i]
            x = float(x_i)
            delta_1 = (x - xl) / (xu - xl)
            delta_2 = (xu - x) / (xu - xl)
            rand = random.random()
            mut_pow = 1.0 / (eta + 1.)

            if rand < 0.5:
                xy = 1.0 - delta_1
                val = 2.0 * rand + (1.0 - 2.0 * rand) * xy**(eta + 1)
                delta_q = val**mut_pow - 1.0
            else:
                xy = 1.0 - delta_2
                val = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * xy**(eta + 1)
                delta_q = 1.0 - val**mut_pow

            x = x + delta_q * (xu - xl)
            x = min(max(x, xl), xu)
            x_i = int(x)
            individual[i] = x_i
    return individual,
