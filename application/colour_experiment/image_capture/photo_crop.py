import cv2
import numpy as np


def select_crop_region():
    """can manually select a region of interest and retake"""

    global start_x, start_y, end_x, end_y, cropping, crop_selected, frame

    # initial cropping variables
    cropping = False
    crop_selected = False
    start_x, start_y, end_x, end_y = 0, 0, 0, 0

    def mouse_callback(event, x, y, flags, param):
        """click mouseevent --> selects the cropping region"""
        global start_x, start_y, end_x, end_y, cropping, crop_selected

        if event == cv2.EVENT_LBUTTONDOWN and not crop_selected:
            # where we start selecting a region. so left mouse button slected
            # records initial x,y position of mouse click
            start_x, start_y = x, y
            cropping = True

        # moves mouse while holding bitton. cropping== true here.
        # so green rectangle is drawn to show selection
        elif event == cv2.EVENT_MOUSEMOVE and cropping:
            # draws the rectangle while dragging mouse
            temp_frame = frame.copy()
            cv2.rectangle(temp_frame, (start_x, start_y), (x, y), (0, 255, 0), 2)
            cv2.imshow("Select Crop Area", temp_frame)

        # left mouse button is release so finalised crop
        elif event == cv2.EVENT_LBUTTONUP:
            # final cropping
            end_x, end_y = x, y
            cropping = False
            crop_selected = True

    # display webcam for crop select
    # opens webcam so we can manually crop selection
    webcam = cv2.VideoCapture(1)

    while True:

        cv2.namedWindow("Select Crop Area", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Select Crop Area", mouse_callback)

        # frame = cv2.imread("dye_example.jpg")
        ret, frame = webcam.read()
        if not ret:
            print("Error: Could not access webcam.")
            break

        cv2.imshow("Select Crop Area", frame)
        key = cv2.waitKey(1) & 0xFF

        if crop_selected:
            cv2.destroyAllWindows()

            # Display cropped preview
            cropped_frame = frame[start_y:end_y, start_x:end_x]
            cv2.imshow("Cropped Preview", cropped_frame)
            key = cv2.waitKey(1) & 0xFF

            answer = input("Happy with the crop? [y/n] ")

            cv2.destroyAllWindows()

            if answer == "y":
                np.save("crop_coords.npy", np.array([start_x, start_y, end_x, end_y]))
                return (start_x, start_y, end_x, end_y)

            else:
                print("Reselecting crop region...")
                crop_selected = False


def take_photo(cropped_region):
    """Captures a cropped photo using the stored coordinates."""

    # open webcam
    webcam = cv2.VideoCapture(1)
    ret, frame = webcam.read()
    # close after capture
    webcam.release()

    if not ret:
        print("Error: Could not capture image.")
        return
    # frame = cv2.imread("dye_example.jpg")

    # extract cropped co-ordinates and apply to image taken
    start_x, start_y, end_x, end_y = cropped_region
    cropped_frame = frame[start_y:end_y, start_x:end_x]

    # save cropped image ---> idk rename or remove
    filename = f"cropped_image.jpg"
    cv2.imwrite(filename, cropped_frame)
    print(f"Photo saved as {filename}")

    height, width = frame.shape[:2]
    resized_frame = cv2.resize(cropped_frame, (width, height))

    cv2.imwrite("resized_cropped_image.jpg", resized_frame)


########################################################################

if __name__ == "__main__":
    cropped_region = select_crop_region()
    if cropped_region:
        print(f"Cropped Region Selected: {cropped_region}")

        take_photo(cropped_region)
