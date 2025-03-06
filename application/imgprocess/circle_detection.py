import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

class Image_processing:
    def __init__(self, image_path, expected_grid=(8,12)):
        self.image_path = image_path
        self.expected_grid = expected_grid
        self.image = cv.imread(image_path)
        self.best_circles = None
        self.labelled_rgb_values = None  # Store labelled RGB values here

    def enforce_grid_pattern(self, circles):
        """
        Forces a grid structure on detected circles by sorting and filtering.
        
        Args:
            circles (np.ndarray): Detected circles from HoughCircles.
        
        Returns:
            np.ndarray: Filtered circles arranged in a grid-like pattern.
        """
        if circles is None or len(circles[0]) < 2:
            return None
        
        # Extract (x, y) positions only.
        circle_positions = circles[0, :, :2]
        
        # Sort circles by their y-coordinate (rows) and then by x-coordinate (columns)
        sorted_indices = np.lexsort((circle_positions[:, 0], circle_positions[:, 1]))
        sorted_circles = circles[0, sorted_indices]
        
        # Calculate the expected number of circles
        expected_num_circles = self.expected_grid[0] * self.expected_grid[1]
        
        # If more circles are detected than expected, keep only the first `expected_num_circles`
        if len(sorted_circles) > expected_num_circles:
            sorted_circles = sorted_circles[:expected_num_circles]
        
        return np.array([sorted_circles], dtype=np.uint16)

    def extract_rgb_values(self, circles, radius=1):
        """
        Extracts the average RGB values at the centers of detected circles.
        
        Args:
            circles (np.ndarray): Detected circles.
            radius (int): Radius for averaging RGB values.
        
        Returns:
            np.ndarray: Array of mean RGB values for each circle.
        """
        # Convert the image from OpenCV's default BGR format to RGB 
        image_rgb = cv.cvtColor(self.image, cv.COLOR_BGR2RGB)
        
        # List to store the mean RGB values for each detected circle
        rgb_values = []
        
        # Iterate through all detected circles to extract RGB values
        for circle in circles[0, :]:
            x, y = circle[0], circle[1]
            rgb = np.zeros(3, dtype=np.float32)
            count = 0
            
            # Iterate over the surrounding pixels within the specified radius to compute mean RGB
            for i in range(-radius, radius + 1):
                for j in range(-radius, radius + 1):
                    # Ensure pixel coordinates are within valid bounds of the image
                    if 0 <= y + i < image_rgb.shape[0] and 0 <= x + j < image_rgb.shape[1]:
                        rgb += image_rgb[y + i, x + j]
                        count += 1
            
            # Compute mean RGB value
            rgb /= count  
            rgb_values.append(rgb.astype(int))
        
        return np.array(rgb_values)

    def auto_hough_circle_detection(self):
        """
        Detects circles in an image, extracts RGB values, and prints labelled results.
        
        Returns:
            dict: Labelled RGB values for each detected well, or None if detection fails.
        """
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        gray = cv.equalizeHist(gray)
        blurred = cv.medianBlur(gray, 5)
        
        # Controls threshold for detecting circles and is adjusted to optimise detection.
        param2 = 50
        best_circles = None
        
        # Loop progressively lowers param2 to increase sensitivity
        while param2 >= 10:
            # Circle detection using hough circles
            circles = cv.HoughCircles(
                blurred, 
                cv.HOUGH_GRADIENT, 
                dp=1.2, 
                minDist=15,  
                param1=50, 
                param2=param2,  
                minRadius=20, 
                maxRadius=25
            )

            # Compare circles with well plate
            if circles is not None and circles.shape[1] >= self.expected_grid[0] * self.expected_grid[1]:
                best_circles = circles
                break  
            param2 -= 5  
        
        # If it works, use enforce grid to remove outliers --> align to 96 well plate
        if best_circles is not None:
            best_circles = self.enforce_grid_pattern(best_circles)
            if best_circles is not None:
                rgb_values = self.extract_rgb_values(best_circles)
                circle_positions = best_circles[0, :, :2]
                
                # Sort wells by their positions (top-left to bottom-right order)
                sorted_indices = np.lexsort((circle_positions[:, 0], circle_positions[:, 1]))
                sorted_circles = best_circles[0, sorted_indices]
                
                # Assign well labels
                well_labels = [f"W{i + 1}" for i in range(self.expected_grid[0] * self.expected_grid[1])]
                self.labelled_rgb_values = dict(zip(well_labels, rgb_values[sorted_indices]))
                self.best_circles = sorted_circles
                
                # Print labelled RGB values
                print("Labelled RGB Values:")
                for well, rgb in self.labelled_rgb_values.items():
                
                    return self.labelled_rgb_values
    
        print("Circle detection failed.")
        return None

    def plot_picture(self):
        """
        Plots the image with detected circles and labels.

        Returns:
            None: Displays the image using matplotlib.
        """
        if self.best_circles is not None:
            image = self.image.copy()
            for idx, circle in enumerate(self.best_circles):
                center = (circle[0], circle[1])
                radius = circle[2]
                cv.circle(image, center, radius, (0, 255, 0), 2)
                cv.circle(image, center, 5, (0, 0, 255), -1)  # Red bullseye
                cv.putText(image, f"W{idx + 1}", (center[0] - 10, center[1] + 5), 
                            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Display result
            plt.figure(figsize=(10, 10))
            plt.imshow(cv.cvtColor(image, cv.COLOR_BGR2RGB))
            plt.axis('off')
            plt.show()
                


    

    


