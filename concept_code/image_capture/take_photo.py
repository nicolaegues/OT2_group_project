import cv2
def take_photo(file = 'image.jpg', camera = 0):
    '''
    Function to take photo from computer webcam.
    Saves image to the same directory as the instance of python.

    Args:
        camera (int): port number of webcam. default is 0
        file (string): filename of saved image
    '''
    webcam = cv2.VideoCapture(camera)
    check, frame = webcam.read()
    cv2.imwrite(filename=file, img=frame)
    webcam.release()