import numpy as np
import pandas as pd
import os
from opentrons_script_generator import generate_script

class wellplate96:
    '''
    A class to use the 96 well plate with optimisation algorithms.

    Args:
        function (function):
            The function that takes the volumes for each liquid in each well plate, and returns a single number for each well.
            The return is the number to be minimized.
        iter_size (int):
            How many wells are used in each iteration.
        liquid_names (list of strings):
            The names of each liquid.
        well_loc (int):
            Position of the well plate in the OT2. Default: 5 (the middle of the robot).
        total_volume (float):
            Total volume to be pipetted in each well. Default: 150uL.
        
    Params:
        iteration_count (int):
            Current iteration count of the algorithm
        num_liquids (int):
            Number of liquids
        output (DataFrame):
            A dataframe containing the volume of each liquid for each well in the well plate.
        input (DataFrame):
            A dataframe containing the return value from 'function' for each well in the well plate.
        function (function):
            The function that takes the volumes for each liquid in each well plate, and returns a single number for each well.
            The return is the number to be minimized.
        iter_size (int):
            How many wells are used in each iteration.
        
    '''
    def __init__(self, function, iter_size, liquid_names, well_loc = 5, total_volume = 150.0):
        self.iteration_count = 0  # Initialize counter
        self.num_liquids = len(liquid_names)
        index = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.output = pd.DataFrame(data = np.zeros([8, 12*self.num_liquids]), index = index)
        self.output.columns = pd.MultiIndex.from_product([np.arange(1, 13), liquid_names])
        self.input = pd.DataFrame(data = np.zeros([8, 12]), index = index, columns = np.arange(1,13))
        self.iter_size = iter_size
        #define which function you want, user input or colour mixing function
        self.function = function
        if function == 'Manual':
            self.manual_input = True
        else: self.manual_input = False
        self.well_loc = well_loc
        self.total_volume = total_volume

    def __call__(self, params):
        #calculates start and end index
        start_index = (self.iteration_count * self.iter_size)
        end_index = start_index + self.iter_size

        #saves output parameter to csv
        self.output.values.reshape(96*self.num_liquids)[start_index*self.num_liquids:end_index*self.num_liquids] = params.reshape(self.iter_size*self.num_liquids)
        self.output.to_csv('./data/output.csv')

        #We will not need to save these if we are uploading the script one at a time
        with open('./data/iter_count.txt', 'w') as file:
            file.write(str(self.iteration_count))
        np.save('./data/values.npy', params)

        #function to pippette goes here
        #os.system('opentrons_simulate opentrons_script.py')
        generate_script(self.iteration_count, params, self.well_loc, self.total_volume)
        print("Upload script, wait for robot and then press any key to continue")
        input()

        if self.manual_input == True:
            values = self.user_input(params, self.input, self.iteration_count)
        else:
            values = self.function(params)
            self.input.values.reshape(96)[start_index:end_index] = values
            self.input.to_csv('./data/input.csv')

        self.iteration_count += 1
        return values
    
    def user_input(self, params, df, iter_c):
        iter_s = params.shape[0]
        #handles input dataframe
        #for colour mixing 
        start_index = iter_c * iter_s
        #saves dataframe to file
        df.to_csv('./data/input.csv')
        print('Input values into input.csv')
        print("Press any key to continue")
        inp = input()
        while inp != 'yes':
            inp = input()
        df2 = pd.read_csv('./data/input.csv', index_col = [0], header = [0], dtype=np.double)
        values = df2.values.reshape(96)[start_index:start_index+iter_s]
        return values
    

