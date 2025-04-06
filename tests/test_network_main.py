"""
The proposed main script for the version where the robot is connected to the robot. 
It is also simultanously the opentrons run script. The user must upload this to the OT2 app at the 
beginning of the experiment, after which all optimsation steps will be executed in one go by the 
robot. 
This also means, however, that there can't be any well detection pop-ups prompting the user to 
decide whether they are happy with the well detection. Only a fully automatic method can be used 
(and must therefore work flawlessly!).

Simulate the OT2 robot outputs from command line via: 

export PYTHONPATH=$(pwd)
opentrons_simulate tests/test_network_main.py

"""

from opentrons import protocol_api
import numpy as np

import sys
from optobot.automate import OptimisationLoop
from tests.test_colours_network import test_get_colours

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

# Set whether the robot is connected to the network (True) or not (False)
network_connection = True

# Define an experiment name.
experiment_name = "colour_experiment"
data_storage_folder = "tests/test_results_data" 
name = f"{data_storage_folder}/{experiment_name}"

# Define the experimental parameters.
# In this experiment, these are RGB colour pigments and water.
liquid_names = ["water", "blue", "yellow", "red"]

# Define the measured parameters.
# In this experiment, these are the RGB values of the experimental products.
measured_parameter_names = ["measured_red", "measured_green", "measured_blue"]

# Set a target measurement.
# In the real experiment, this a set of defined RGB values. 
#For testing purposes, this is the volumes of the input liquids directly (instead of the measurements)
test_target_measurement = [
    14, 
    20, 
    15]

# Define the search space of the experimental parameters.
# In this experiment, this is the range of volumes for RGB colour pigments.
search_space = [[0.0, 30.0], [0.0, 30.0], [0.0, 30.0]]

# Define the well plate dimensions.
wellplate_size = 96
wellplate_shape = (8, 12)  # As (rows, columns).

# Define the total volume in a well.
total_volume = 90.0

# Define the location of the wellplate in the Opentrons OT-2.
# In this experiment, this is slot 5.
# NOTE: More than one well plate can be used.
# NOTE: For example, slots 5 & 8 -> [5, 8]
wellplate_locs = [5]

# Define the population size for optimisation.
# In this experiment, this is defined as 12 -> 12 wells/columns.
population_size = 5

# Define the number of iterations for optimisation.
# In this experiment, this is defined as 8 -> 8 rows.
num_iterations = 2

# Check that the number of iterations and population size are valid.
if population_size * num_iterations > wellplate_size * len(wellplate_locs):
    print("error: not enough wells for defined population and iteration size")
    sys.exit(1)

# Define an objective function for optimisation.
def objective_function(measurements):
    """
    The objective function to be optimised.

    In this experiment, this calculates the squared Euclidean distance
    between the target RGB value and the measured RGB values.

    Parameters
    ----------
    measurements : np.ndarray
        The measured parameter values of the experimental products.

    Returns
    -------
    errors : np.ndarray
        The errors between the target value and the measured values.
    """

    errors = ((measurements - test_target_measurement) ** 2).sum(axis=1)
    return errors


# Define a measurement function for measuring experimental products.
# NOTE: A measurement function does not have to be defined if measurement input is manual.
def measurement_function(
    liquid_volumes,
    iteration_count,
    population_size,
    num_measured_parameters,
    data_dir,
):
    """
    The measurement function for measuring experimental products.

    In this experiment, this uses the "get_colours" function from the
    "optobot.colorimetric.colours" sub-module. The "get_colours" function
    uses a webcam pointing at the OT-2 deck to take a picture and retrieve
    the RGB values of the experimental products.

    Parameters
    ----------
    liquid_volumes : np.ndarray
        The liquid volumes of the experimental products.

    iteration_count : int
        The current iteration.

    population_size : int
        The population size.

    num_measured_parameters : int
        The number of measured parameters.

    data_dir : string
        The directory for storing the experimental data.

    Returns
    -------
    np.ndarray, float[population_size, num_measured_parameters]
        The measured parameter values of the experimental products.
    """

    return test_get_colours(
        iteration_count, population_size, num_measured_parameters, data_dir
    )

def test_measurement_function(
    liquid_volumes,
    iteration_count,
    population_size,
    num_measured_parameters,
    data_dir,
):
    """
    Function that skips the measurement step for testing purposes to check the optimisation works, 
    by using the input liquid volumes directly as the "measurements".
    
    """
    return liquid_volumes[:, 1:]

def run(protocol: protocol_api.ProtocolContext):
    #loading the tips, reservoir and well plate into the program
    tips = protocol.load_labware("opentrons_96_tiprack_1000ul", 1)
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", 2)
    
    plates = {}
    for idx, loc in enumerate(wellplate_locs):
        plates[f"plate_{idx+1}"] = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", loc)
    
    left_pipette = protocol.load_instrument("p1000_single_gen2", "right", tip_racks=[tips])

    ot2_labware = {"reservoir": reservoir, "plates": plates, "left_pipette": left_pipette}

    model = OptimisationLoop(
        objective_function,
        liquid_names,
        measured_parameter_names,
        population_size,
        name=name,
        measurement_function=test_measurement_function,
        wellplate_shape=wellplate_shape,
        wellplate_locs=wellplate_locs,
        total_volume=total_volume,
        network_connection = network_connection,
        ot2_labware = ot2_labware
    )
    # call particle_swarm, random_forest, or gaussian process
    model.optimise(search_space, optimiser="PSO", num_iterations=num_iterations)


