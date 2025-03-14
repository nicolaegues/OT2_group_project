import numpy as np
import pandas as pd
import os
from opentrons_script_generator import generate_script
from imgprocess.circle_detection import Image_processing
from image_capture.take_photo import take_photo
import string


class wellplate96:
    '''
    A class to use the 96 well plate with optimisation algorithms.

    Args:
        objective_function (objective_function):
            The objective function that takes the volumes for each liquid in each well plate, and returns a single number (error) for each well.
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
    def __init__(self, objective_function, exp_data_dir, wellplate_shape, wells_per_iteration, manual_measurement, liquid_names, measurement_parameter_names, well_locs, total_volume):

        self.objective_function = objective_function
        self.exp_data_dir = exp_data_dir
        self.wellplate_shape = wellplate_shape
        self.iteration_count = 0  # Initialize counter
        self.num_liquids = len(liquid_names)
        self.measurement_parameter_names = measurement_parameter_names
        self.num_measurement_parameters= len(measurement_parameter_names)
        self.wells_per_iteration = wells_per_iteration
        self.liquid_names = liquid_names
        self.manual_measurement = manual_measurement #boolean
        self.well_locs = well_locs
        self.nr_wellplates = len(well_locs)
        self.total_volume = total_volume
        self.blank_row_space = 5

        self.liquid_volume_df, self.measurements_df, self.error_df,self.all_data_df = self.init_dataframes()


    def __call__(self, liquid_volumes):

        #Adds water so that it fills up to the same volume each time
        water_vol = self.total_volume - np.sum(liquid_volumes, axis = 1)
        #water will now be the first liquid to be added
        liquid_volumes = np.hstack([water_vol.reshape(-1,1), liquid_volumes])
   
        filepath = f"{self.exp_data_dir}/generated_script.py"
        generate_script(filepath, self.iteration_count, self.wells_per_iteration, liquid_volumes, self.well_locs)
        input("Upload script, wait for robot, and then press any key to continue: ")
      
        if self.manual_measurement == True:
            measurements= self.user_input() #the mixed color RGB values
            #measurements = liquid_volumes[:, :-1]
        else:
            measurements = self.measure_colors()
        
        errors = self.objective_function(measurements)

        self.store_data(liquid_volumes, measurements, errors)

        self.iteration_count += 1

        return errors
    
    
    def init_dataframes(self):

        wellplate_nr_rows = self.wellplate_shape[0]
        wellplate_nr_columns = self.wellplate_shape[1]

        wellplate_index = [string.ascii_uppercase[i % 26] for i in range(self.wellplate_shape[0])] #['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        wellplate_index = []

        for i in range(self.nr_wellplates):
            wellplate_rows = [string.ascii_uppercase[i % 26] for i in range(wellplate_nr_rows)]
            
            if i != self.nr_wellplates - 1:
                wellplate_index.extend(wellplate_rows + [""] * self.blank_row_space)
            else:
                wellplate_index.extend(wellplate_rows)

        liquid_columns = pd.MultiIndex.from_product([np.arange(1, wellplate_nr_columns+1), self.liquid_names])
        measurement_columns = pd.MultiIndex.from_product([np.arange(1, wellplate_nr_columns+1), self.measurement_parameter_names])
        all_data_columns = ["iteration_number"] + [f"vol_{liquid_name}" for liquid_name in self.liquid_names] + self.measurement_parameter_names + ["error"]
        error_columns = np.arange(1, wellplate_nr_columns+1)

        total_rows = self.nr_wellplates*wellplate_nr_rows+(self.blank_row_space*(self.nr_wellplates -1))
        
        def create_csv(filename, shape, index = None, columns= None):
            filepath = f"{self.exp_data_dir}/{filename}.csv"

            df = pd.DataFrame(data=np.zeros(shape), index=index, columns=columns)
            df.to_csv(filepath)
            return df
        
        
        liquid_volume_df = create_csv("liquid_volumes", (total_rows, wellplate_nr_columns * self.num_liquids), wellplate_index, liquid_columns)
        errors_df = create_csv("errors", (total_rows, wellplate_nr_columns), wellplate_index, error_columns)
        measurements_df = create_csv("measurements", (total_rows, wellplate_nr_columns * self.num_measurement_parameters), wellplate_index, measurement_columns)
        all_data_df = create_csv("all_data", (self.nr_wellplates*wellplate_nr_rows*wellplate_nr_columns, len(all_data_columns)), columns = all_data_columns )

        return liquid_volume_df, measurements_df, errors_df, all_data_df
    
    
    def store_data(self, liquid_volumes, measurements, errors):


        #handling cases where the wells_per_iterations do not exactly equal one row. 
        total_wells = self.wellplate_shape[0] *self.wellplate_shape[1]
        og_start_index = (self.iteration_count * self.wells_per_iteration) 

        current_well_plate = og_start_index //(self.wellplate_shape[0]*self.wellplate_shape[1])
        start_index = og_start_index + current_well_plate*self.blank_row_space*self.wellplate_shape[1]
        end_index = start_index + self.wells_per_iteration

        self.liquid_volume_df.values.reshape(self.liquid_volume_df.size)[start_index*self.num_liquids:end_index*self.num_liquids] = liquid_volumes.flatten()
        self.liquid_volume_df.to_csv(f"{self.exp_data_dir}/liquid_volumes.csv")

        
        self.error_df.values.reshape(self.error_df.size)[start_index:end_index] = errors
        self.error_df.to_csv(f"{self.exp_data_dir}/errors.csv")


        if self.manual_measurement == False: 
            self.measurements_df.values.reshape(self.nr_wellplates* total_wells*self.num_liquids + self.blank_row_space)[(start_index )* self.num_liquids:end_index * self.num_liquids] = measurements.flatten()
            self.measurements_df.to_csv(f"{self.exp_data_dir}/measurements.csv")


        iteration_idx = np.full((self.wellplate_shape[1], 1), self.iteration_count+1)
        all_data = np.concatenate([iteration_idx, liquid_volumes, measurements, errors[:, np.newaxis] ], axis = 1 )
        self.all_data_df.iloc[self.iteration_count:self.iteration_count+self.wells_per_iteration, :] = all_data
        self.all_data_df.to_csv(f"{self.exp_data_dir}/all_data.csv")


    def user_input(self):             

        input("Open 'measurements.csv', input the measurements into the corresponding row, and press any key to continue: ")

        measurements_df = pd.read_csv(f"{self.exp_data_dir}/measurements.csv")
        measurements = measurements_df.values[self.iteration_count, :]

        return measurements
    
    def measure_colors(self):

        total_wells = self.wellplate_shape[0] *self.wellplate_shape[1]
        start_index = (self.iteration_count * self.wells_per_iteration) % total_wells
        end_index = start_index + self.wells_per_iteration
        
        
        # well_id = self.iteration_count % total_wells

        os.makedirs(f"{self.exp_data_dir}/captured_images", exist_ok=True)
        filename = f"{self.exp_data_dir}/captured_images/image_iteration_{self.iteration_count}"
        take_photo(filename)

        processor = Image_processing(filename)
        rgb_values = processor.auto_hough_circle_detection()

        #assuming rgb values are of shape (rows, cols, 3)
        letter_colors = rgb_values.flatten()[start_index*self.num_liquids:end_index*self.num_liquids]


        return letter_colors


