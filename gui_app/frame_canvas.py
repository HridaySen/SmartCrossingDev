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
        
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)
        
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
        if ret:
            # Convert the frame to RGB format from BGR format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to a PIL image
            image = Image.fromarray(frame)

            # Convert the PIL image to a PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Display the PhotoImage on the canvas
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.image = photo

        # Schedule the next frame update
        self.after(15, self.show_feed)
