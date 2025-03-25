import numpy as np
from skopt import Optimizer
import pyswarms as ps

def particle_swarm(model, search_space, max_iterations, wells_per_iteration):
    '''
    Performs well plate optimisation using particle swarm

    Args:
        model (Class):
            Well plate class, from wellplate_classes
        search_space (list):
            A list of the search space for the algorithms.
            formatted as [[low, high] for i in num_liquids]
        iter_n (int):
            Total number of iterations for the optimisation algorithm.
    '''

    search_space = np.array(search_space)
    max_bound = search_space[:,1]
    min_bound = search_space[:,0]
    bounds = (min_bound, max_bound)


    #initialising swarm
    options = {'c1': 0.3, 'c2': 0.5, 'w':0.1}

    #Call instance of PSO with bounds argument
    optimiser = ps.single.GlobalBestPSO(n_particles=wells_per_iteration, dimensions=3, options=options, bounds=bounds)

    #Perform optimization
    cost, pos = optimiser.optimize(model, iters=max_iterations)

def guassian_process(model, search_space, iter_n):
    '''
    Performs well plate optimisation using guassian optimisation

    Args:
        model (Class):
            Well plate class, from wellplate_classes
        search_space (list):
            A list of the search space for the algorithms.
            formatted as [[low, high] for i in num_liquids]
        iter_n (int):
            Total number of iterations for the optimisation algorithm.
    '''

    iter_s = model.iter_size

    opt = Optimizer(search_space, base_estimator='GP', n_initial_points=iter_s)
    for i in range(iter_n):
        params = []
        for i in range(iter_s):
            params.append(opt.ask())

        result = model(np.array(params))
        for i in range(iter_s):
            opt.tell(params[i], result[i])

def random_forest(model, search_space, iter_n):
    '''
    Performs well plate optimisation using random forest

    Args:
        model (Class):
            Well plate class, from wellplate_classes
        search_space (list):
            A list of the search space for the algorithms.
            formatted as [[low, high] for i in num_liquids]
        iter_n (int):
            Total number of iterations for the optimisation algorithm.
    '''

    iter_s = model.iter_size

    opt = Optimizer(search_space, base_estimator='RF', n_initial_points=iter_s)
    for i in range(iter_n):
        params = []
        for i in range(iter_s):
            params.append(opt.ask())

        result = model(np.array(params))
        for i in range(iter_s):
            opt.tell(params[i], result[i])
