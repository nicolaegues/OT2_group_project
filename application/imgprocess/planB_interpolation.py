import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
import numpy as np
from math import dist

class PlanB_Image_Processing:
    def __init__(self, image_path):
        self.image = plt.imread(image_path)
        self.clicked_points = []
        self.rgb_values = None
        self.fig, self.ax = plt.subplots()

    def get_rgb_at_center(self, x, y):
        """Returns the RGB values at a given (x, y) coordinate"""
        x, y = int(x), int(y)
        return self.image[y, x]  

    def calculate_well_centers(self, first_click, second_click, rows=8, cols=12):
        """Calculates the well centers based on two selected points"""
        dx = dist(first_click, second_click)
        dy = dx  

        well_centers = []
        for i in range(rows):
            for j in range(cols):
                x = first_click[0] + j * dx  
                y = first_click[1] + i * dy  
                well_centers.append((x, y))

        return well_centers

    def plot_well_centers(self, well_centers):
        """Plots the calculated well centers on the image"""
        self.ax.imshow(self.image)
        for center in well_centers:
            self.ax.plot(center[0], center[1], 'ro')
        plt.draw()

    def on_click(self, event: MouseEvent):
        """Handles mouse clicks to determine well grid"""
        if event.inaxes:
            self.clicked_points.append((event.xdata, event.ydata))

            if len(self.clicked_points) == 2:
                first_click, second_click = self.clicked_points
                well_centers = self.calculate_well_centers(first_click, second_click)
                self.plot_well_centers(well_centers)

                # Extract RGB values for each well center
                self.rgb_values = np.zeros((8, 12, 3), dtype=np.uint8)
                for i in range(8):
                    for j in range(12):
                        x, y = well_centers[i * 12 + j]
                        self.rgb_values[i, j] = self.get_rgb_at_center(x, y)

                self.clicked_points = []  #reset points after processing

    def run(self):
        """Displays the image and allows user interaction to define the grid"""
        while True:
            self.fig, self.ax = plt.subplots()
            self.ax.imshow(self.image)
            self.fig.canvas.mpl_connect('button_press_event', self.on_click)
            plt.show()

            answer = input("Happy with the grid? [y/n] ")
            if answer.lower() == "y":
                return self.rgb_values  #return RGB values when done


#Example usage inside the script
if __name__ == "__main__":
    image_path = "C:/Users/nicol/OneDrive - University of Bristol/OT2_group_project/application/image_capture/Screenshot 2025-03-20 104037.png"
    analyzer = PlanB_Image_Processing(image_path)
    final_rgb_values = analyzer.run()
    pass