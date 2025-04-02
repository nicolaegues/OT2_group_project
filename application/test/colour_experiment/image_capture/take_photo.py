import cv2
import numpy as np

def take_photo(file = 'image.jpg', camera = 1, crop_coords_file = None):
    '''
    Function to take photo from computer webcam.
    Saves image to the same directory as the instance of python.

    Args:
        camera (int): port number of webcam. default is 0
        file (string): filename of saved image
    '''
    webcam = cv2.VideoCapture(camera)
    check, frame = webcam.read()
    webcam.release()

    if not check:
        print("Error: Could not capture image.")
        return

    if crop_coords_file is not None:
        #extract cropped co-ordinates and apply to image taken
        cropped_region = np.load(crop_coords_file)
        start_x, start_y, end_x, end_y = cropped_region
        cropped_frame = frame[start_y:end_y, start_x:end_x]
        frame = cropped_frame

    cv2.imwrite(filename=file, img=frame)
