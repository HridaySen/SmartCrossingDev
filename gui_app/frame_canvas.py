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
        self.max_width = 1500
        self.max_height = 900
        
        # Create a canvas widget and pack it into the frame
        self.canvas = tk.Canvas(self, bg="red", width=self.max_width, height=self.max_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize variables for drawing zones
        self.drawing = False
        self.drawn_points = []

        # Initialize the camera feed
        self.camera_source = 0
        self.capture = cv2.VideoCapture(self.camera_source, cv2.CAP_DSHOW)

        # Opencv uses 640x480 by default, so we need to set it to 1920x1080 for our laptop camera feed
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # Now prevent memory leaks by keeping track of the canvas image
        self.canvas_image_id = None

        self.show_feed()

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

            # Update the existing image, or create a new one if it doesn't exist
            if self.canvas_image_id is None:
                self.canvas_image_id = self.canvas.create_image(center_x, center_y, image=photo, anchor=tk.CENTER)
            else:
                self.canvas.itemconfig(self.canvas_image_id, image=photo)
                self.canvas.coords(self.canvas_image_id, center_x, center_y)

            self.canvas.image = photo

        # Schedule the next frame update
        self.after(15, self.show_feed)

    def save_frame(self):
        # Get the current frame from the camera feed
        ret, frame = self.capture.read()
        if ret:
            # Save the frame to a file
            cv2.imwrite("frame_chosen.jpg", frame)

    def __resize_frame(self, frame):
        # current canvas dimensions
        current_canvas_w = max(self.canvas.winfo_width(), self.max_width)
        current_canvas_h = max(self.canvas.winfo_height(), self.max_height)

        # Get the dimensions of the frame and calculate the scaling factor to fit it within the canvas while maintaining the aspect ratio
        frame_height, frame_width = frame.shape[:2]
        scaling_factor = min(current_canvas_w / frame_width, current_canvas_h / frame_height)
        new_width = int(frame_width * scaling_factor)
        new_height = int(frame_height * scaling_factor)
        
        # Resize the frame to fit the canvas
        return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    def __return_center(self):
        # winfo gets you the live dimensions of the canvas, which is important for resizing the window and keeping the feed centered. 
        # If the dimensions are 1, it means the window hasn't been rendered yet, so we use the max dimensions instead.
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        centre_x = w // 2 if w > 1 else self.max_width // 2
        centre_y = h // 2 if h > 1 else self.max_height // 2

        return centre_x, centre_y