import numpy as np
from skopt import Optimizer
import pyswarms as ps

def particle_swarm(model, search_space, iter_s, iter_n):

    search_space = np.array(search_space)
    max_bound = search_space[:,1]
    min_bound = search_space[:,0]
    bounds = (min_bound, max_bound)

    #initialising swarm
    options = {'c1': 0.3, 'c2': 0.5, 'w':0.1}

    #Call instance of PSO with bounds argument
    optimiser = ps.single.GlobalBestPSO(n_particles=iter_s, dimensions=3, options=options, bounds=bounds)

    #Perform optimization
    cost, pos = optimiser.optimize(model, iters=iter_n)

def guassian_process(model, search_space, iter_s, iter_n):

    opt = Optimizer(search_space, base_estimator='GP')
    for i in range(iter_n):
        params = []
        for i in range(iter_s):
            params.append(opt.ask())

        result = model(np.array(params))
        for i in range(iter_s):
            opt.tell(params[i], result[i])

def random_forest(model, search_space, iter_s, iter_n):

    opt = Optimizer(search_space, base_estimator='RF')
    for i in range(iter_n):
        params = []
        for i in range(iter_s):
            params.append(opt.ask())

        result = model(np.array(params))
        for i in range(iter_s):
            opt.tell(params[i], result[i])