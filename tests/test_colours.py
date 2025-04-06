import os

from optobot.colorimetric.image_processing.contours_adapted import well_detection
from optobot.colorimetric.image_processing.extrapolated_grid import ExtrapolatedGrid


def test_get_colours(
    iteration_count, population_size, num_measured_parameters, data_dir
):
    """
    Assuming the webcam is mounted to the top of the robot and ready to go, this function takes a picture of the wellplate,
    extracts the rgb-values of each of the wells (even if not all are filled), and returns the colors of only the wells that are part of this iteration.

    """

    # get the start and end-indices to index a flattened color array. When the iteration count exceeds that of only one-wellplate, take the modulus such that the correct index is found.
    start_index = (iteration_count * population_size) * num_measured_parameters
    end_index = start_index + population_size * num_measured_parameters

    # os.makedirs(f"{data_dir}/captured_images", exist_ok=True)
    # captured_im_path = f"{data_dir}/captured_images/image_iteration_{iteration_count}"
    captured_im_path = "tests/test_data/test_image.jpg"

    os.makedirs(f"{data_dir}/detected_well_figs", exist_ok=True)
    detected_wells_figs_path = f"{data_dir}/detected_well_figs/fig_iteration_{iteration_count}"

    # take_photo(filename)

    # while loop for confirmation
    inp = ""
    while inp != "y":

        # Repeats until desired result
        print("Type threshold (Default is 30):")
        threshold = int(input())
        rgb_values = well_detection(captured_im_path, detected_wells_figs_path, threshold)

        print("\nHappy with detection?")
        print(
            'type "y" if you are, "n" to try again, and "b" to use the manual clicking detection'
        )
        user = input()
        if user == "y":
            inp = user
        elif user == "b":
            planB_processor = ExtrapolatedGrid(captured_im_path, detected_wells_figs_path)
            rgb_values = planB_processor.run()
            # accounts for overlap for multiple well plates
            start_index = start_index % (96 * num_measured_parameters)
            end_index = end_index % (96 * num_measured_parameters)
            inp = "y"
        else:
            inp = ""

        # to check the script works without the robot/actual data, uncomment the line below and comment out the 4 lines above.
        # rgb_values = np.random.rand(self.wellplate_shape[0], self.wellplate_shape[1], 3)

        iteration_colours = rgb_values.flatten()[start_index:end_index]
        iteration_colours = iteration_colours.reshape(
            population_size, num_measured_parameters
        )

    return iteration_colours
