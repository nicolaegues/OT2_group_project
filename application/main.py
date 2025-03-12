##main script
import opt_functions
from wellplate_classes import wellplate96
import numpy as np

def main():

    liquid_names = ['blue', 'green', 'red']
    search_space = [[0.0, 150/3], [0.0, 150/3], [0.0, 150/3]]
    iteration_size = 12
    iteration_number = 8
    if iteration_size * iteration_number > 96:
        print('Error: too many iterations')
        return None

    #example function to be minimized for colours, sums it then squares it
    #we need to import and add the camera recognition function here, can be created as a class with
    #__call__ to allow it to use parameters but still only input params and return values.
    #instead we could have more variables passed into it, and just write in the docs which ones
    #it would be easier to pass start_index and iter_size or iter_n and iter_size to locate the correct section of wells
    def auto_input(params):
        ideal = np.array([30.0, 20.0, 12.0])
        values = ((params - ideal)**2).sum(axis = 1)
        return values

    #type 'Manual' in the function box to allow manual input
    model = wellplate96(auto_input, iteration_size, liquid_names)

    #allow user to tweak params for algorithms here

    #call particle_swarm, random_forest, or gaussian process
    opt_functions.particle_swarm(model, search_space, iteration_number)



if __name__ == "__main__":
    main()