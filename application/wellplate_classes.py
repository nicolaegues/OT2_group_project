import numpy as np
import pandas as pd
import os

class wellplate96:
    def __init__(self, function, iter_size, liquid_names):
        self.iteration_count = 0  # Initialize counter
        self.num_liquids = len(liquid_names)
        self.output = pd.DataFrame(data = np.zeros([8, 12*self.num_liquids]), index = np.arange(1, 9))
        self.output.columns = pd.MultiIndex.from_product([np.arange(1, 13), liquid_names])
        self.input = pd.DataFrame(data = np.zeros([8, 12]), index = np.arange(1, 9), columns = np.arange(1,13))
        self.iter_size = iter_size
        #define which function you want, user input or colour mixing function
        self.function = function
        if function == 'Manual':
            self.manual_input = True
        else: self.manual_input = False

    def __call__(self, params):
        #calculates start and end index
        start_index = (self.iteration_count * self.iter_size)
        end_index = start_index + self.iter_size

        #saves output parameter to csv
        self.output.values.reshape(96*self.num_liquids)[start_index*self.num_liquids:end_index*self.num_liquids] = params.reshape(self.iter_size*self.num_liquids)
        self.output.to_csv('./data/output.csv')

        with open('./data/iter_count.txt', 'w') as file:
            file.write(str(self.iteration_count))

        np.save('./data/values.npy', params)

        #function to pippette goes here
        os.system('opentrons_simulate opentrons_script.py')


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
        print("type 'yes' when done")
        inp = input()
        while inp != 'yes':
            inp = input()
        df2 = pd.read_csv('./data/input.csv', index_col = [0], header = [0], dtype=np.double)
        values = df2.values.reshape(96)[start_index:start_index+iter_s]
        return values
    

