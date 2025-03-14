##main script
import opt_functions
from wellplate_classes import wellplate96
import numpy as np
import datetime
import os
pass


#to-do: allow user to tweak optim params for algorithms 
#complete if loop for other optim methods


def main():

    #these are primarly for later data storage folder/file naming
    optimisation_id = "PSO"
    exp_no = "Example_2_wellplates_random"

    #Create experiment directory. All the data will be saved here. 
    current_datetime = datetime.datetime.now().strftime("%a-%d-%b-%Y-at-%I-%M-%S%p")
    exp_id = f"exp_{exp_no}_{optimisation_id}_{current_datetime}" 
    data_storage_folder = "data" 
    exp_data_dir = f"{data_storage_folder}/{exp_id}"
    os.makedirs(exp_data_dir, exist_ok=True)

    # Change this based on what you want your ideal measurement to be
    ideal_measurement = [30.0, 30.0, 30.0] # our ideal RGB value

    #search space for the volumes of the liquids
    search_space = [[0.0, 30.0], [0.0, 30.0], [0.0, 30.0]]
    #total volume in each well
    total_volume = 90.0

    def objective_function(measurements): 
        errors = ((measurements - ideal_measurement)**2).sum(axis = 1)
        return errors

    #wellplate info
    wellplate_size = 96 
    wellplate_shape = (8, 12) #as viewed horizontally

    #location(s) of the wellplate(s). First one will be filled, then the remaining iterations will done on the other wellplate(s).
    wellplate_locs = [5, 8]

    max_iterations = 16  
    wells_per_iteration = 12
 

    if wells_per_iteration * max_iterations > wellplate_size*len(wellplate_locs):
        print('Error: too many iterations, or too many wells per iteration') 
        return None
    

    liquid_names = ["water", 'blue', 'yellow', 'red'] #in A1-A4
    measurement_parameter_names = ["measured_red", "measured_green", "measured_blue"]
    
    #whether to manually input measured values (that will obtained after the liquids are mixed with certain volumes), 
    # or whether to do this automatically (in which case a "record_colors" function will be called within the class)
    manual_measurement = False 

    model = wellplate96(objective_function, exp_data_dir, wellplate_shape, wells_per_iteration, manual_measurement, liquid_names, measurement_parameter_names, wellplate_locs, total_volume)

    #call particle_swarm, random_forest, or gaussian process
    if optimisation_id == "PSO":
        opt_functions.particle_swarm(model, search_space, max_iterations, wells_per_iteration)
    


if __name__ == "__main__":
    main()