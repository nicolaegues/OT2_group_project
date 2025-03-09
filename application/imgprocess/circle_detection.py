
import cv2 as cv  
import numpy as np  
import matplotlib.pyplot as plt  

class Image_processing:
    def __init__(self, image_path, expected_grid=(8, 12)):
        """
        Initialises the Image_processing class with the image path and expected grid dimensions.
        
        Args:
            image_path (str): Path to the image file.
            expected_grid (tuple): Expected grid dimensions (rows, columns) for the well plate.
        """
        self.image_path = image_path  
        self.expected_grid = expected_grid  
        self.image = cv.imread(image_path)  
        # Placeholder for detected circles
        self.best_circles = None  

    def filter_circular_contours(self, contours):
        """
        Filters contours to keep only those that are  circular.
        
        Args:
            contours (list): List of contours detected in the image.
        
        Returns:
            list: List of radii of contours that are  circular.
        """
        # List to store radii of valid circular contours
        valid_circle = []  
        for cont in contours:
            # Calculate the perimeter of the contour
            perimeter = cv.arcLength(cont, True)  

            # Calculate the area of the contour
            area = cv.contourArea(cont)  
            # Avoid division by zero
            if perimeter == 0:
                continue  
            circularity = 4 * np.pi * (area / (perimeter ** 2))  
            if 0.8 < circularity < 1.2:  
                _, radius = cv.minEnclosingCircle(cont)  
                valid_circle.append(radius)  
        return valid_circle
    
    def enforce_grid_pattern(self, circles):
        """
        Enforces a grid pattern on the detected circles to align them with the expected well plate layout.
        
        Args:
            circles (np.ndarray): Detected circles, represented as (x, y and radius).
        
        Returns:
            np.ndarray: Array of circles aligned in a grid pattern.
        """
        # Check circles are valid
        if circles is None or len(circles[0]) < 2:
            return None  
        
        # Extract (x, y, radius) positions of the circles. Selects all circles and their first 3 values (x, y, radius)
        circle_positions = circles[0, :, :3]  
        
        # Sort circles by Y-coordinate (row-wise sorting).
        #Circles are processed from top to bottom
        sorted_by_y = sorted(circle_positions, key=lambda p: p[1])
        
        # Group circles into rows based on distance to Y-coordinates.
        rows = []
        # Differences in y-coordinates. 
        y_differences = np.diff([p[1] for p in sorted_by_y])
        # Median difference between circles in Y-direction
        median_diff = np.median(y_differences)
        #Threshold to organise circles into rows
        row_threshold = median_diff + np.std(y_differences)
        # Initialise first row ith first circle.
        current_row = [sorted_by_y[0]]

        # Iterate through the remaining circles to organise them into rows
        for i in range(1, len(sorted_by_y)):
            # Check if the current circle is close enough in Y-coordinate to be part of the current row
            if abs(sorted_by_y[i][1] - current_row[-1][1]) < row_threshold:
                current_row.append(sorted_by_y[i]) 

            # If not, finish  current row by sorting it by X-coordinate.
            else:
                rows.append(sorted(current_row, key=lambda p: p[0])) 
                current_row = [sorted_by_y[i]]  

        # Add the last row to the list of rows
        rows.append(sorted(current_row, key=lambda p: p[0]))  # Add the last row

        # Confirm numbers of circles
        corrected_rows = []
        for row in rows:
            if len(row) == 12:
                corrected_rows.append(row)
            # If the row has too many circles. Sort row by X-coord and keep the first correct
            #12 circles 
            elif len(row) > 12:
                sorted_row = sorted(row, key=lambda p: p[0])
                corrected_rows.append(sorted_row[:12])
            else:
                continue

        # Flatten corrected rows back into a single array
        sorted_circles = np.array([circle for row in corrected_rows for circle in row])

        # Limit to expected number of wells (8x12 = 96)
        if len(sorted_circles) > self.expected_grid[0] * self.expected_grid[1]:
            sorted_circles = sorted_circles[:self.expected_grid[0] * self.expected_grid[1]]

        return np.array([sorted_circles], dtype=np.float32)

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
            x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
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
        Detects circles in an image and extracts RGB values.
        
        Returns:
            np.ndarray: Array of RGB values for each detected circle, or None if detection fails.
        """
        # Convert the image to grayscale
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        
        # Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to enhance contrast
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Apply median blur to reduce noise
        blurred = cv.medianBlur(gray, 5)
        
        # Detect edges using the Canny edge detector
        edges = cv.Canny(blurred, 50, 150)

        # Find contours in the edge-detected image
        contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if not contours:
            print("No contours found. Check image quality.")
            return None

        # Filter circular contours only
        valid_circle = self.filter_circular_contours(contours)

        if len(valid_circle) < 5:
            print("Not enough valid circles detected from contours.")
            return None

        # Controls threshold for detecting circles and is adjusted to optimise detection.
        param2 = 50
        best_circles = None
        
        # Loop progressively lowers param2 to increase sensitivity
        while param2 >= 10:
            # Circle detection using Hough Circles
            circles = cv.HoughCircles(
                blurred, 
                cv.HOUGH_GRADIENT, 
                dp=1, 
                minDist=15,  
                param1=50, 
                param2=param2,  
                minRadius=15, 
                maxRadius=25
            )

            # Compare circles with well plate
            if circles is not None and circles.shape[1] >= self.expected_grid[0] * self.expected_grid[1]:
                best_circles = circles
                break  
            param2 -= 5  
        
        # If circles are detected, enforce grid pattern to remove outliers
        if best_circles is not None:
            best_circles = self.enforce_grid_pattern(best_circles)
            if best_circles is not None:
                rgb_values = self.extract_rgb_values(best_circles)
                self.best_circles = best_circles
                
                # Return the array of RGB values
                return rgb_values
    
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
            for idx, circle in enumerate(self.best_circles[0, :]):
                # Ensure centre and radius are integers
                x, y, r = int(circle[0]), int(circle[1]), int(circle[2])  # Convert to integers
                center = (x, y)  
                radius = r  
                # Draw green circle
                cv.circle(image, center, radius, (0, 255, 0), 2)  
                # Draw red bullseye
                cv.circle(image, center, 5, (0, 0, 255), -1)  
                cv.putText(image, f"W{idx + 1}", (center[0] - 10, center[1] + 5), 
                            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)  # Label the circle
            
            # Display result
            plt.figure(figsize=(10, 10))
            plt.imshow(cv.cvtColor(image, cv.COLOR_BGR2RGB))
            plt.axis('off')
            plt.show()