import numpy as np
import pandas as pd
import os
from opentrons_script_generator import generate_script
from imgprocess.circle_detection import Image_processing
from imgprocess.blurry_well_detection import well_detection
from image_capture.take_photo import take_photo
import string

from imgprocess.planB_interpolation import PlanB_Image_Processing


class wellplate96:
    """
    A class to use the 96 well plate with optimisation algorithms.

    Parameters: 
        - objective_function (function):
            Function to calculate the error based the measured values obtained after using certain liquid-volumes in the experiment. 
        - exp_data_dir (string): 
            directory to store the experimental data.
        - wellplate_shape (tuple): 
            tuple representing the shape (rows, columns) of the wellplate. 
        - wells_per_iteration (int):
            Number of wells used in each (optimization) iteration
        - manual_measurement (bool): 
            boolean indicating whether the measured values should be manually added to the "measurements" csv file, or whether instead 
            the "measure_colors" function should be called. 
        - liquid_names (list of strings): 
            list of the names of the liquids used in the experiment. 
        - measurement_parameter_names (list of strings):
            list of the names of the elements of one measurement (e.g. "red, "green" and "blue" of RBG values)
        - wellplate_locs (list of ints): 
            list containing the location of the wellplate(s) that want to be used. 
        - total_volume: 
            Total liquid volume per well.
    
    """
    def __init__(self, objective_function, exp_data_dir, wellplate_shape, wells_per_iteration, manual_measurement, liquid_names, measurement_parameter_names, wellplate_locs, total_volume):

        self.objective_function = objective_function
        self.exp_data_dir = exp_data_dir
        self.wellplate_shape = wellplate_shape
        self.iteration_count = 0  # Initialize iteration counter
        self.num_liquids = len(liquid_names)
        self.measurement_parameter_names = measurement_parameter_names
        self.num_measurement_parameters= len(measurement_parameter_names)
        self.wells_per_iteration = wells_per_iteration
        self.liquid_names = liquid_names
        self.manual_measurement = manual_measurement 
        self.wellplate_locs = wellplate_locs
        self.nr_wellplates = len(wellplate_locs)
        self.total_volume = total_volume
        self.blank_row_space = 1 #vertical space between wellplate data in CSV files (if more than one is used)

        #Initialize dataframes for storing experimental data
        self.liquid_volume_df, self.measurements_df, self.error_df,self.all_data_df = self.init_dataframes()


    def __call__(self, liquid_volumes):
        """
        Executes one optimization iteration.
        1. Takes the input volumes of each liquid and calculates how much water to use to dilute each set.
        2. generates the opentrons-run script for this iteration, 
        3. Waits for the user to upload this script to the robot, 
        4. Gathers the measurements (e.g. final colors if dyes are mixed) after the liquids have been combined in each well - either manually or by calling a measurement function, 
        5. Computes the errors by calling the objective function that compares these measurements to an ideal, pre-defined measurement. 

        Parameters: 
        - liquid_volumes (ndarray): 
            Array containing the volumes of each liquid that will be put in each of the wells of the current iteration. 
            Its shape is (wells_per_iteration, num_liquids). 
        
        Returns: 
        - errors (array): 
            Computed errors from the objective function. 
        
        """

        #Adds water so that it fills up to the same volume each time
        water_vol = self.total_volume - np.sum(liquid_volumes, axis = 1)
        #water will now be the first liquid to be added
        liquid_volumes = np.hstack([water_vol.reshape(-1,1), liquid_volumes])
   
        #path where the generated script will be stored
        filepath = f"{self.exp_data_dir}/generated_ot2_script.py"
        generate_script(filepath, self.iteration_count, self.wells_per_iteration, liquid_volumes, self.wellplate_locs)
        
        input("Upload script, wait for robot, and then press any key to continue: ")
      
        #obtain measurements either manually or automatically (in the case that color-recording wants to be done)
        if self.manual_measurement == True:
            measurements = self.user_input() 
        else:
            #measurements = self.measure_colors()
            measurements = self.measure_blurry_colours()
        
        errors = self.objective_function(measurements)

        #Data storage
        self.store_data(liquid_volumes, measurements, errors)

        #update the iteration count
        self.iteration_count += 1

        return errors
    
    
    def init_dataframes(self):
        """
        Initializes dataframes for liquid volumes, measurements, errors, and a dataframe where all data appear together.
        """

        wellplate_nr_rows = self.wellplate_shape[0]
        wellplate_nr_columns = self.wellplate_shape[1]

        # constructs the letter-index for the wellplate-shaped csvs, 
        # taking into account the vertical spacing for when the data of multiple wellplates wants to be stored. 
        wellplate_index = []
        for i in range(self.nr_wellplates):

            #e.g., [A, B, C, D, E, F, G, H]
            wellplate_rows = [string.ascii_uppercase[i % 26] for i in range(wellplate_nr_rows)]
            
            if i != self.nr_wellplates - 1:
                wellplate_index.extend(wellplate_rows + [""] * self.blank_row_space)
            else:
                wellplate_index.extend(wellplate_rows)

        # define column indices
        liquid_columns = pd.MultiIndex.from_product([np.arange(1, wellplate_nr_columns+1), self.liquid_names])
        measurement_columns = pd.MultiIndex.from_product([np.arange(1, wellplate_nr_columns+1), self.measurement_parameter_names])
        error_columns = np.arange(1, wellplate_nr_columns+1) 
        all_data_columns = ["iteration_number"] + [f"vol_{liquid_name}" for liquid_name in self.liquid_names] + self.measurement_parameter_names + ["error"]


        total_rows = self.nr_wellplates*wellplate_nr_rows+(self.blank_row_space*(self.nr_wellplates -1))
        
        def create_csv(filename, shape, index = None, columns= None):
            filepath = f"{self.exp_data_dir}/{filename}.csv"

            df = pd.DataFrame(data=np.zeros(shape), index=index, columns=columns)
            df.to_csv(filepath)
            return df
        
        #creates and saved the empty csvs to the experiment folder
        liquid_volume_df = create_csv("liquid_volumes", (total_rows, wellplate_nr_columns * self.num_liquids), wellplate_index, liquid_columns)
        errors_df = create_csv("errors", (total_rows, wellplate_nr_columns), wellplate_index, error_columns)
        measurements_df = create_csv("measurements", (total_rows, wellplate_nr_columns * self.num_measurement_parameters), wellplate_index, measurement_columns)
        all_data_df = create_csv("all_data", (self.nr_wellplates*wellplate_nr_rows*wellplate_nr_columns, len(all_data_columns)), columns = all_data_columns )

        return liquid_volume_df, measurements_df, errors_df, all_data_df
    
    
    def store_data(self, liquid_volumes, measurements, errors):
        """
        Stores the data for the current iteration in csv files (which will also hold the data for the subsequent iterations of the experiment.)
        
        """

        total_wells = self.wellplate_shape[0] *self.wellplate_shape[1]
        raw_start_index = (self.iteration_count * self.wells_per_iteration) 
        current_well_plate = raw_start_index //total_wells

        #The start and end-indexes will be used on the flattened dataframes (in the case of volumes, errors, and measurement data), to correctly select the section 
        #of the dataframe on which to save this iteration data (the original shape of the dataframes is preserved).
        #Done this way, as the wells_per_iteration may not be exactly the size of one row (even though with the default values it is). 
        start_index = raw_start_index + current_well_plate*self.blank_row_space*self.wellplate_shape[1]
        end_index = start_index + self.wells_per_iteration

        #store the liquid-volume data into the dataframe for this iteration
        self.liquid_volume_df.values.reshape(self.liquid_volume_df.size)[start_index*self.num_liquids:end_index*self.num_liquids] = liquid_volumes.flatten()
        self.liquid_volume_df.to_csv(f"{self.exp_data_dir}/liquid_volumes.csv")

        #store the error data for this iteration
        self.error_df.values.reshape(self.error_df.size)[start_index:end_index] = errors
        self.error_df.to_csv(f"{self.exp_data_dir}/errors.csv")

        #only store the measurement data if it hasn't already been manually inputted into a csv. 
        if self.manual_measurement == False: 
            self.measurements_df.values.reshape(self.measurements_df.size)[start_index* self.num_measurement_parameters:end_index * self.num_measurement_parameters] = measurements.flatten()
            self.measurements_df.to_csv(f"{self.exp_data_dir}/measurements.csv")

        #store all the data for one iteration together (each row has the data for one well)
        iteration_idx = np.full((self.wellplate_shape[1], 1), self.iteration_count+1)
        all_data = np.concatenate([iteration_idx, liquid_volumes, measurements, errors[:, np.newaxis] ], axis = 1 )
        start = self.iteration_count*self.wells_per_iteration
        end = start + self.wells_per_iteration
        self.all_data_df.iloc[start:end, :] = all_data
        self.all_data_df.to_csv(f"{self.exp_data_dir}/all_data.csv")


    def user_input(self):       
        """
        Allows the user to manually input their measurement data into a csv. 
        """      

        total_wells = self.wellplate_shape[0] *self.wellplate_shape[1]
        raw_start_index = (self.iteration_count * self.wells_per_iteration) 
        current_well_plate = raw_start_index //total_wells

        #get start- and end-indices to index the correct section of a flattened measurements dataframe (the original shape of which is preserved). 
        #Done this way, as the wells_per_iteration may not be exactly the size of one row (even though with the default values it is). 
        start_index = raw_start_index + current_well_plate*self.blank_row_space*self.wellplate_shape[1]
        end_index = start_index + self.wells_per_iteration

        input("Open 'measurements.csv', input the measurements into the corresponding row, and press any key to continue: ")
        measurements_df = pd.read_csv(f"{self.exp_data_dir}/measurements.csv", skiprows=[0], index_col=0)

        measurements = measurements_df.values.reshape(self.measurements_df.size)[start_index* self.num_measurement_parameters:end_index * self.num_measurement_parameters] 
        measurements = measurements.reshape(self.wells_per_iteration, self.num_measurement_parameters)
        return measurements
    
    def measure_colors(self):
        """
        Assuming the webcam is mounted to the top of the robot and ready to go, this function takes a picture of the wellplate, 
        extracts the rgb-values of each of the wells (even if not all are filled), and returns the colors of only the wells that are part of this iteration.

        """

        #get the start and end-indices to index a flattened color array. When the iteration count exceeds that of only one-wellplate, take the modulus such that the correct index is found. 
        total_wells = self.wellplate_shape[0] *self.wellplate_shape[1]
        start_index = (self.iteration_count * self.wells_per_iteration) % total_wells
        end_index = start_index + self.wells_per_iteration
        
        
        os.makedirs(f"{self.exp_data_dir}/captured_images", exist_ok=True)

        filename = f"{self.exp_data_dir}/captured_images/image_iteration_{self.iteration_count}"
        take_photo(filename)

        processor = Image_processing(filename)
        rgb_values = processor.auto_hough_circle_detection()

        planB_processor = PlanB_Image_Processing(filename)
        rgb_values = planB_processor.run()
        
        # if rgb_values == None:
        #     print("Detection method failed. Using different method:")
            
        # else: 
        #     processor.plot_picture()
        #     answer = input("Happy with the result? If not, a different method will be used: [y/n] ")
        #     if answer.lower() == "n":
        #         rgb_values = planB_processor.run()


        #to check the script works without the robot/actual data, uncomment the line below and comment out the 4 lines above. 
        #rgb_values = np.random.rand(self.wellplate_shape[0], self.wellplate_shape[1], 3)

        iteration_colors = rgb_values.flatten()[start_index*self.num_measurement_parameters:end_index*self.num_measurement_parameters]
        iteration_colors = iteration_colors.reshape(self.wells_per_iteration, self.num_measurement_parameters)

        return iteration_colors

    def measure_blurry_colours(self):
        """
        Assuming the webcam is mounted to the top of the robot and ready to go, this function takes a picture of the wellplate, 
        extracts the rgb-values of each of the wells (even if not all are filled), and returns the colors of only the wells that are part of this iteration.

        """

        #get the start and end-indices to index a flattened color array. When the iteration count exceeds that of only one-wellplate, take the modulus such that the correct index is found. 
        start_index = self.iteration_count * self.wells_per_iteration * self.num_measurement_parameters
        end_index = (start_index + self.wells_per_iteration) * self.num_measurement_parameters
        
        
        os.makedirs(f"{self.exp_data_dir}/captured_images", exist_ok=True)

        filename = f"{self.exp_data_dir}/captured_images/image_iteration_{self.iteration_count}"
        take_photo(filename)
        rgb_values = well_detection(filename)
        #rgb_values = well_detection('imgprocess/test.jpg')

        #to check the script works without the robot/actual data, uncomment the line below and comment out the 4 lines above. 
        #rgb_values = np.random.rand(self.wellplate_shape[0], self.wellplate_shape[1], 3)

        iteration_colours = rgb_values.flatten()[start_index:end_index]
        iteration_colours = iteration_colours.reshape(self.wells_per_iteration, self.num_measurement_parameters)

        return iteration_colours

