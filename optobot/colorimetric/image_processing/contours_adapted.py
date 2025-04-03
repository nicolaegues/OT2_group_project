import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np


def well_detection(filename, thresh=30):
    """
    Takes an image of a well plate with coloured dyes in the well, and returns a sorted
    array of the rgb values in each well

    args:
        image (array): cv2 image of the well plate
    returns:
        rgb_list (array): a number of detected wells x 3 array of rgb values
    """

    # modifiable parameters
    # radius is number of pixels from detected circles to find average RGB
    radius = 4

    # threshold is how grey pixel needs to be to be turned to white, higher threshold - less grey

    # Sets all pixels to white if they are grey
    # Done by finding the median and checking if pixels are within a certain threshold of that median
    image = cv.imread(filename)

    for i in range(np.shape(image)[0]):
        for j in range(np.shape(image)[1]):
            pixel = image[i, j]
            median = np.median(pixel)
            if np.all(median - thresh < pixel) and np.all(median + thresh > pixel):
                # currently changes all pixels to white, black may be better
                image[i, j] = [255, 255, 255]

    # Convert the image to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to enhance contrast
    clahe = cv.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Apply median blur to reduce noise
    blurred = cv.medianBlur(gray, 5)

    # Detect edges using the Canny edge detector
    edges = cv.Canny(blurred, 50, 200)

    # Find contours in the edge-detected image
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    valid_circle = []

    coords = []
    for cont in contours:
        # Calculate the perimeter of the contour
        perimeter = cv.arcLength(cont, True)

        # Calculate the area of the contour
        area = cv.contourArea(cont)
        # Avoid division by zero
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * (area / (perimeter**2))
        if 0.7 < circularity < 1.3:
            xy, r = cv.minEnclosingCircle(cont)
            coords.append(xy)
            valid_circle.append(r)

    coords = np.array(coords)
    num_rows = ((len(coords) - 1) // 12) + 1

    # sorting coordinates: sort by y first, split it by 12 to get rows
    # then sort by x to get it in order
    sort_coords = [None for i in range(num_rows)]
    for i in range(num_rows):
        sort_row = coords[coords[:, 1].argsort()]
        if i * 12 <= len(coords):
            row_split = sort_row[i * 12 : i * 12 + 12]
        else:
            row_split = sort_row[i * 12 :]
        sort_col = row_split[row_split[:, 0].argsort()]
        sort_coords[i] = sort_col
    sort_coords = np.vstack(sort_coords)

    image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    rgb_list = []
    for x, y in sort_coords:
        x = int(x)
        y = int(y)
        count = 0
        rgb = np.zeros(3)
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius - 1):
                rgb += image_rgb[y + i, x + j]
                count += 1
        rgb /= count
        rgb_list.append(rgb)

    cv.drawContours(image, contours, -1, (0, 255, 0), 2)
    image_display = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    plt.imshow(image_display)
    plt.show()

    rgb_list = np.array(rgb_list)

    return rgb_list
