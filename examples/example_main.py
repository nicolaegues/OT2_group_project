"""
An example script showing how to use the optobot package. This script uses the
optobot package in the context of a colour mixing experiment, where RGB liquid
pigments are mixed to create a target colour.
"""

# Import required libraries.
import sys

from optobot.automate import OptimisationLoop
from optobot.colorimetric.colours import get_colours


def main():

    network_connection = False
    
    # Define an experiment name.
    experiment_name = "colour_experiment"
    data_storage_folder = "examples/results_data" 
    name = f"{data_storage_folder}/{experiment_name}"

    # Define the experimental parameters.
    # In this experiment, these are RGB colour pigments and water.
    liquid_names = ["water", "blue", "yellow", "red"]

    # Define the measured parameters.
    # In this experiment, these are the RGB values of the experimental products.
    measured_parameter_names = ["measured_red", "measured_green", "measured_blue"]

    # Set a target measurement.
    # In this experiment, this a set of defined RGB values.
    target_measurement = [
        114.8412698,
        96.1111111,
        37.84126984,
    ]  # Taken from a previous experiment.

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
    population_size = 12

    # Define the number of iterations for optimisation.
    # In this experiment, this is defined as 8 -> 8 rows.
    num_iterations = 8

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

        errors = ((measurements - target_measurement) ** 2).sum(axis=1)
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

        return get_colours(
            iteration_count, population_size, num_measured_parameters, data_dir
        )

    # Define the automated optimisation loop.
    model = OptimisationLoop(
        objective_function,
        liquid_names,
        measured_parameter_names,
        population_size,
        name=name,
        measurement_function=measurement_function,
        wellplate_shape=wellplate_shape,
        wellplate_locs=wellplate_locs,
        total_volume=total_volume,
        network_connection = network_connection,
        ot2_labware = None
    )

    # Start the optimisation loop.
    # In this experiment, Particle Swarm Optimisation is used.
    model.optimise(search_space, optimiser="PSO", num_iterations=num_iterations)


if __name__ == "__main__":
    main()
