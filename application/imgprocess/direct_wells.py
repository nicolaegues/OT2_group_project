"""
Contains code for direct calculation of well plate centres using well plate 
dimensions. Also contains code for extracting RGB values at these positions.
"""

# Import required libraries.
import cv2 as cv
import numpy as np

# Create a dict to store the dimensions of a well plate with 96 wells.
# TODO: Move this to a CSV file.
PLATE = {"wells"            : 96,
         "rows"             : 8,
         "columns"          : 12,
         "height"           : 85.36,
         "width"            : 127.56,
         "row_offset"       : 11.18,
         "column_offset"    : 14.28,
         "row_spacing"      : 9.00,
         "column_spacing"   : 9.00,
         "well_diameter"    : 6.85}


def get_well_centres(image: np.ndarray, plate: dict = PLATE, row_distort: float = 0, 
                     column_distort: float = 0) -> np.ndarray:
    """
    Calculates the location of well plate centres in an image of a well plate 
    using well plate dimensions. 

    Parameters
    ----------
    image : np.ndarray
        The image of the well plate.
    
    plate : dict, default = PLATE
        A dictionary containing measurements of the well plate.

    row_distort : float, default = 0
        A coefficient for scaling well plate centres in the vertical direction 
        to account for image distortion. 

    column_distort : float, default = 0
        A coefficient for scaling well plate centres in the horizontal 
        direction to account for image distortion.        
    
    Returns
    -------
    centres : np.ndarray, shape(n_rows, n_columns, 2)
        An array containing the pixel positions of the well plate centres.
    """

    # Get the height and width of the image.
    image_height = image.shape[0]
    image_width = image.shape[1]

    # Calculate the scaling factors of the well plate dimensions.
    scale_height = image_height / plate["height"] 
    scale_width = image_width / plate["width"]

    # Calculate the pixel positions of the well plate centres.
    row_centres = plate["row_offset"] + (plate["row_spacing"] * np.arange(plate["rows"]))
    column_centres = plate["column_offset"] + (plate["column_spacing"] * np.arange(plate["columns"]))

    row_centres *= scale_height
    column_centres *= scale_width

    # If a vertical scaling coefficient was passed to account for distortion. 
    if row_distort:
        # Calculate the distance of the row-centres from the vertical-centre.
        image_height_centre = image_height // 2
        row_distances = row_centres - image_height_centre

        # Scale the rows.
        row_centres += row_distort * row_distances

    # If a horizontal scaling coefficient was passed to account for distortion.
    if column_distort:
        # Calculate the distance of the column-centres from the horizontal-centre.
        image_width_centre = image_width // 2
        column_distances = column_centres - image_width_centre

        # Scale the columns.
        column_centres += column_distort * column_distances
    
    # Round the pixel positions.
    row_centres = np.round(row_centres).astype(int)
    column_centres = np.round(column_centres).astype(int)

    # Create a single array of pixel positions.
    centres = np.stack(np.meshgrid(row_centres, column_centres)).T

    return centres


def get_colours(image: np.ndarray, positions: np.ndarray, radius: int = 0) -> np.ndarray:
    """
    Gets the RGB values of an image at given pixel positions. A radius of 
    pixels to average the RGB values over can also be passed.

    Parameters
    ----------
    image : np.ndarray
        The image to get the RGB values of.
    
    positions : np.ndarray, shape(n_rows, n_columns, 2)
        The pixel positions to get the RGB values at.

    radius : int, default = 0
        The radius of pixels to average the RGB values over.
    
    Returns
    -------
    colours : np.ndarray, shape(n_rows, n_columns, 3)
        An array containing the RGB values of the image at the given pixels.
    """
    
    # Get the RGB values at the pixel positions.
    colours = image[positions[:, :, 0], positions[:, :, 1]]

    # If a radius of more than 0 is entered. 
    if radius > 0:
        # TODO: Vectorise this loop.
        # Sum the RGB values of pixels for each radius.
        for i in range(1, radius + 1):
            # Sum the RGB values of horizontally displaced pixels.
            colours += image[positions[:, :, 0], positions[:, :, 1] + i]
            colours += image[positions[:, :, 0], positions[:, :, 1] - i]

            # Sum the RGB values of vertically displaced pixels.
            colours += image[positions[:, :, 0] + i, positions[:, :, 1]]
            colours += image[positions[:, :, 0] - i, positions[:, :, 1]]

            # Sum the RGB values of diagonally displaced pixels.
            colours += image[positions[:, :, 0] + i, positions[:, :, 1] + i]
            colours += image[positions[:, :, 0] - i, positions[:, :, 1] - i]

            colours += image[positions[:, :, 0] + i, positions[:, :, 1] - i]
            colours += image[positions[:, :, 0] - i, positions[:, :, 1] + i]

        # Calculate the average of the RGB values.
        colours /= ((2 * radius) + 1) ** 2
        colours = np.round(colours).astype(int)
        
    return colours


def draw_grid(image: np.ndarray, positions: np.ndarray, filename: str, 
              colour: tuple[int] = (0, 0, 0)) -> None:
    """
    Draws a grid that intersects at the given pixel positions on an image.

    Parameters
    ----------
    image : np.ndarray
        The image to draw the grid on.
    
    positions : np.ndarray, shape(n_rows, n_columns, 2)
        The pixel positions that the grid should intersect at.

    filename : str
        The name of the file to save the image with the grid to.
    
    colour : tuple[int], default = (0, 0, 0)
        The colour of the grid lines in RGB.
    """

    # Get the height and width of the image.
    image_height = image.shape[0]
    image_width = image.shape[1]

    # Create a copy of the image.
    img = image.copy()

    # Draw the horizontal grid lines.
    for row in positions[:, 0, 0]:
        cv.line(img, (0, row), (image_width, row), color=colour)
    
    # Draw the vertical grid lines.
    for column in positions[0, :, 1]:
        cv.line(img, (column, 0), (column, image_height), color=colour)

    # Save the image.
    cv.imwrite(filename, cv.cvtColor(img, cv.COLOR_RGB2BGR))

    return None