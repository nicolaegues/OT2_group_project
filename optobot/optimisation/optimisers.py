import numpy as np
import pyswarms as ps
from skopt import Optimizer


def particle_swarm(model, search_space, num_iterations):
    """
    Performs well plate optimisation using particle swarm

    Args:
        model (Class):
            Well plate class, from wellplate_classes
        search_space (list):
            A list of the search space for the algorithms.
            formatted as [[low, high] for i in num_liquids]
        num_iterations (int):
            Total number of iterations for the optimisation algorithm.
    """

    search_space = np.array(search_space)
    max_bound = search_space[:, 1]
    min_bound = search_space[:, 0]
    bounds = (min_bound, max_bound)

    population_size = model.population_size

    # initialising swarm
    options = {"c1": 0.3, "c2": 0.5, "w": 0.1}

    # Call instance of PSO with bounds argument
    optimiser = ps.single.GlobalBestPSO(
        n_particles=population_size, dimensions=3, options=options, bounds=bounds
    )

    # Perform optimization
    cost, pos = optimiser.optimize(model, iters=num_iterations)


def guassian_process(model, search_space, num_iterations):
    """
    Performs well plate optimisation using guassian optimisation

    Args:
        model (Class):
            Well plate class, from wellplate_classes
        search_space (list):
            A list of the search space for the algorithms.
            formatted as [[low, high] for i in num_liquids]
        num_iterations (int):
            Total number of iterations for the optimisation algorithm.
    """

    population_size = model.population_size

    opt = Optimizer(search_space, base_estimator="GP", n_initial_points=population_size)

    for i in range(num_iterations):
        params = opt.ask(population_size)
        result = model(np.array(params))
        for i in range(population_size):
            opt.tell(params[i], result[i])


def random_forest(model, search_space, num_iterations):
    """
    Performs well plate optimisation using random forest

    Args:
        model (Class):
            Well plate class, from wellplate_classes
        search_space (list):
            A list of the search space for the algorithms.
            formatted as [[low, high] for i in num_liquids]
        num_iterations (int):
            Total number of iterations for the optimisation algorithm.
    """

    population_size = model.population_size

    opt = Optimizer(search_space, base_estimator="RF", n_initial_points=population_size)

    for i in range(num_iterations):
        params = opt.ask(population_size)
        result = model(np.array(params))
        for i in range(population_size):
            opt.tell(params[i], result[i])


"""
    for i in range(num_iterations):
        params = []
        for i in range(population_size):
            params.append(opt.ask())
        result = model(np.array(params))
        #print(params, result)
        for i in range(population_size):
            opt.tell(params[i], result[i])
"""
