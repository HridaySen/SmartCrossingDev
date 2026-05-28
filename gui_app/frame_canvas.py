import tkinter as tk
import sys
import os
import cv2

# Look for imports starting from the project root.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.zone import Zone
from PIL import Image, ImageTk

# Make a Canvas frame, under the tk.Frame class
# tk.Frame is a layout widget that can contain other widgets, and can be used to organize the layout of the GUI. 
# By inheriting from tk.Frame, we can create a custom frame that contains a canvas for drawing and displaying the camera feed.
class FrameCanvas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Set the width and height of the canvas
        self.canvas_width = 1500
        self.canvas_height = 900
        
        # Create a canvas widget and pack it into the frame
        self.canvas = tk.Canvas(self, bg="red", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.drawing = False
        self.drawn_points = []

        self.camera_source = 0
        self.capture = cv2.VideoCapture(self.camera_source)

        self.show_feed()


    def start_drawing(self, event):
        self.drawing = True
    
    def end_drawing(self, event):
        self.drawing = False
        if self.drawn_points:
            zone = Zone(self.drawn_points)
            zone.save_zone()
            self.drawn_points = []

    def show_feed(self):
        # Get the opencv feed
        ret, frame = self.capture.read()
        # print(f"Frame dimensions: {frame.shape}")
        if ret:
            # Resize the frame to fit the canvas
            frame = self.__resize_frame(frame)

            # Convert the frame to RGB format from BGR format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to a PIL image
            image = Image.fromarray(frame)

            # Convert the PIL image to a PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Get the center of canvas
            center_x, center_y = self.__return_center()

            # Display the PhotoImage on the canvas
            self.canvas.create_image(center_x, center_y, image=photo, anchor=tk.CENTER)
            self.canvas.image = photo

        # Schedule the next frame update
        self.after(15, self.show_feed)

    def __resize_frame(self, frame):
        frame_height, frame_width = frame.shape[:2]
        scaling_factor = min(self.canvas_width / frame_width, self.canvas_height / frame_height)
        new_width = int(frame_width * scaling_factor)
        new_height = int(frame_height * scaling_factor)
        
        # Resize the frame to fit the canvas
        return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    def __return_center(self):
        return self.canvas_width // 2, self.canvas_height // 2