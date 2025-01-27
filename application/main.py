"""
Contains the main code for this package.
"""

# Import required libraries.
import cv2 as cv

# Import local modules.
from imgprocess import direct_wells


def main():
    # TODO: Add functional code.
    
    ## Example/Placeholder code.
    # Read in the test image.
    image = cv.cvtColor(cv.imread("../tests/images/wells_96_0001.webp"), cv.COLOR_BGR2RGB)

    # Get the RGB values at the well plate centres.
    centres = direct_wells.get_well_centres(image)
    colours = direct_wells.get_colours(image, centres)

    return None


if __name__ == "__main__":
    main()
