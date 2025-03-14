##main script
import opt_functions
from wellplate_classes_sugg import wellplate96
import numpy as np
import datetime
import os
pass


#Tell the user where to place the liquids in the reservoir!! for correct indexing
#allow user to tweak optim params for algorithms here


def main():

    #these are primarly for later data storage folder/file naming
    optimisation_id = "PSO"
    exp_no = "0"

    current_datetime = datetime.datetime.now().strftime("%a-%d-%b-%Y-at-%I-%M-%S%p")
    exp_id = f"exp_{exp_no}_{optimisation_id}_{current_datetime}" 
    data_storage_folder = "data" 
    exp_data_dir = f"{data_storage_folder}/{exp_id}"
    os.makedirs(exp_data_dir, exist_ok=True)

    wellplate_size = 96 

    wellplate_shape = (8, 12) #as viewed horizontally
    wells_per_iteration = 12
    max_iterations = 8

    if wells_per_iteration * max_iterations > wellplate_size:
        print('Error: too many iterations') 
        return None
    

    liquid_names = ['blue', 'yellow', 'red', "water"] #Tell the user where to place these liquids in the reservoir!!
    measurement_parameter_names = ["measured_red", "measured_green", "measured_blue"]
    manual_measurement = True

    ideal_measurement = [30.0, 30.0, 30.0] # our ideal RGB value
    search_space = [[0.0, 150/3], [0.0, 150/3], [0.0, 150/3]]

    well_locs = [5, 8]
    total_volume = 150.0

    def objective_function(measurements):  
        errors = ((measurements - ideal_measurement)**2).sum(axis = 1)
        return errors

    model = wellplate96(objective_function, exp_data_dir, wellplate_shape, wells_per_iteration, manual_measurement, liquid_names, measurement_parameter_names, well_locs, total_volume)

    #call particle_swarm, random_forest, or gaussian process
    if optimisation_id == "PSO":
        opt_functions.particle_swarm(model, search_space, max_iterations, wells_per_iteration)
    


#if __name__ == "__main__":
main()