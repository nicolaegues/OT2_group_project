import numpy as np
import pandas as pd
from opentrons import protocol_api
import subprocess
import pyswarms as ps

def auto_input(params, df, iter_c):
    iter_s = params.shape[0]
    start_index = iter_c * iter_s
    ideal = np.array([40.0, 60.0, 20.0])
    values = ((params - ideal)**2).sum(axis = 1)
    df.values.reshape(96)[start_index:start_index+iter_s] = values
    df.to_csv('input.csv')
    return values


class wellplate96:
    def __init__(self, function, iter_size, liquid_names):
        self.iteration_count = 0  # Initialize counter
        self.num_liquids = len(liquid_names)
        self.output = pd.DataFrame(data = np.zeros([8, 12*self.num_liquids]), index = np.arange(1, 9))
        self.output.columns = pd.MultiIndex.from_product([np.arange(1, 13), liquid_names])
        self.input = pd.DataFrame(data = np.zeros([8, 12]), index = np.arange(1, 9), columns = np.arange(1,13))
        self.iter_size = iter_size
        self.liquid_names = liquid_names
        #define which function you want, user input or colour mixing function
        self.function = function

    def __call__(self, params):
        #calculates start and end index
        start_index = (self.iteration_count * self.iter_size) * self.num_liquids
        end_index = start_index + self.iter_size*self.num_liquids

        #saves output parameter to csv
        self.output.values.reshape(96*self.num_liquids)[start_index:end_index] = params.reshape(12*self.num_liquids)
        self.output.to_csv('output.csv')

        with open('iter_count.txt', 'w') as file:
            file.write(str(self.iteration_count))

        np.save('values.npy', params)

        #function to pippette goes here
        #subprocess.run("opentrons_simulate", "opentrons_script.py")

        #camera processing and colour extraction function goes here
        values = self.function(params, self.input, self.iteration_count)
        self.iteration_count += 1
        return values
    

model = wellplate96(auto_input, 12, ['blue', 'green', 'red'])

max_bound = 100 * np.ones(3)
min_bound = np.zeros(3)
bounds = (min_bound, max_bound)

#initialising swarm
options = {'c1': 0.3, 'c2': 0.5, 'w':0.1}

#Call instance of PSO with bounds argument
optimiser = ps.single.GlobalBestPSO(n_particles=12, dimensions=3, options=options, bounds=bounds)

#Perform optimization
cost, pos = optimiser.optimize(model, iters=8)
