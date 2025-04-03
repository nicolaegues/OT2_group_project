##main script
from ..optobot.automate import OptimisationLoop
from ..optobot.colorimetric import get_colours

pass


# to-do: allow user to tweak optim params for algorithms
# complete if loop for other optim methods


def main():

    # experiment name
    name = "colour_experiment"

    # Change this based on what you want your ideal measurement to be
    ideal_measurement = [
        114.8412698,
        96.1111111,
        37.84126984,
    ]  # our ideal RGB value, taken from well A4 of test2.jpg

    # search space for the volumes of the liquids
    search_space = [[0.0, 30.0], [0.0, 30.0], [0.0, 30.0]]
    # total volume in each well
    total_volume = 90.0

    # wellplate info
    wellplate_size = 96
    wellplate_shape = (8, 12)  # as viewed horizontally

    # location(s) of the wellplate(s). First one will be filled, then the remaining iterations will done on the other wellplate(s).
    wellplate_locs = [8, 5]

    num_iterations = 16
    population_size = 12

    def objective_function(measurements):
        errors = ((measurements - ideal_measurement) ** 2).sum(axis=1)
        return errors

    def measurement_function(
        liquid_volumes,
        iteration_count,
        population_size,
        num_measured_parameters,
        data_dir,
    ):
        """
        Measurement function to go into wellplate_class
        For this colour experiment we have a function to measure colours
        The return goes straight into the objective function
        by default this function is manual

        Returns:
            A population_size x num_measured_parameters size array containing the measured paramater numbers
        """
        return get_colours(
            iteration_count, population_size, num_measured_parameters, data_dir
        )

    if population_size * num_iterations > wellplate_size * len(wellplate_locs):
        print("Error: too many iterations, or too many wells per iteration")
        return None

    liquid_names = ["water", "blue", "yellow", "red"]  # in A1-A4
    measured_parameter_names = ["measured_red", "measured_green", "measured_blue"]

    # whether to manually input measured values (that will obtained after the liquids are mixed with certain volumes),
    # or whether to do this automatically (in which case a "record_colors" function will be called within the class)

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
    )

    # call particle_swarm, random_forest, or gaussian process
    model.optimise(search_space, optimiser="PSO", num_iterations=num_iterations)


if __name__ == "__main__":
    main()
