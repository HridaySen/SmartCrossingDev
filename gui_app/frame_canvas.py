import tkinter as tk
import sys
import os
import cv2

# Look for imports starting from the project root.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.zone import Zone
from PIL import Image, ImageTk

# Make a Canvas frame, under the tk.Frame class
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
        self.drawn_points_current_resolution = []
        self.clicked_points = [] # Store the event.x and event.y

        # Track the current displayed image dimensions for accurate click position calculations
        self.current_img_w = 0
        self.current_img_h = 0

        # track the current scale of the displayed image for accurate click position calculations
        self.current_img_scale = 1.0

        # Bind the left mouse button click event to the canvas for drawing zones
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Initialize the camera feed
        self.camera_source = 0
        self.capture = cv2.VideoCapture(self.camera_source, cv2.CAP_DSHOW)

        # Opencv uses 640x480 by default, so we need to set it to 1920x1080 for our laptop camera feed
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # Now prevent memory leaks by keeping track of the canvas image
        self.canvas_image_id = None

        # Track loop_id for after method, so we can cancel it when the window is closed to prevent memory leaks
        self.loop_id = None

        self.show_feed()

    # new method to handle canvas clicks for drawing zones
    def on_canvas_click(self, event):
        # Only allow drawing if the drawing mode is active
        if not self.drawing:
            print("Not in drawing mode, click ignored.")
            return

        # no image loaded/displayed yet, so we can't calculate the click position relative to the image, ignore the click
        if self.current_img_w == 0 or self.current_img_h == 0:
            print("Image not loaded yet, click ignored.")
            return

        # save clicks to event clicks list
        self.clicked_points.append((event.x, event.y))

        # Find the current live center of the canvas
        center_x, center_y = self.__return_center()

        # Calculate the boundaries of the image relative to the canvas origin (0,0)
        img_start_x = center_x - (self.current_img_w // 2)
        img_start_y = center_y - (self.current_img_h // 2)

        # Subtract boundaries to find the click location on the frame surface
        frame_click_x = event.x - img_start_x
        frame_click_y = event.y - img_start_y
        self.drawn_points_current_resolution.append((frame_click_x, frame_click_y))

        # These are real coordinates on the 1080p frame, which we can use for zoning and saving to our JSON file
        real_1080p_x = frame_click_x / self.current_img_scale
        real_1080p_y = frame_click_y / self.current_img_scale

        # Check if the user clicked inside the actual image frame boundaries
        if 0 <= frame_click_x <= self.current_img_w and 0 <= frame_click_y <= self.current_img_h:
            print(f"Clicked INSIDE the frame lololol: X={frame_click_x}, Y={frame_click_y}, Scaled: X={real_1080p_x}, Y={real_1080p_y}")           
            
            # Add to the list of drawn points for zoning
            self.drawn_points.append((real_1080p_x, real_1080p_y))

            # Make a drawing
            radius = 4
            point_id = self.canvas.create_oval(
                event.x - radius, event.y - radius,
                event.x + radius, event.y + radius,
                fill="green", outline="black", width=1.5
            )
        else:
            print("Clicked OUTSIDE the camera frame (on the red canvas space). Ignored.")
    

    def show_feed(self):
        # Get the opencv feed
        ret, frame = self.capture.read()
        if ret:
            # Prepare the frame for display on the canvas
            photo = self.__prepare_frame(frame)

            # Update the existing image, or create a new one if it doesn't exist
            self.__update_canvas(photo)

        # Schedule the next frame update
        self.loop_id = self.after(15, self.show_feed)

    def save_frame(self):
        # Get the current frame from the camera feed
        ret, frame = self.capture.read()
        if ret:
            # Save the frame to a file
            cv2.imwrite("frame_chosen.jpg", frame)

            # kill the camera feed to prevent memory leaks
            if self.loop_id is not None:
                self.after_cancel(self.loop_id)
                self.loop_id = None # Reset the loop_id for later
            
            # Prepare this frame
            photo = self.__prepare_frame()
            self.__update_canvas(photo)
            
    def __update_canvas(self, photo):
        # ─── UPDATE IMAGE TRACKING VALUES LIVE ───
        self.current_img_w = photo.width()
        self.current_img_h = photo.height()

        # Get the center of canvas
        center_x, center_y = self.__return_center()

        # Update the existing image, or create a new one if it doesn't exist
        if self.canvas_image_id is None:
            self.canvas_image_id = self.canvas.create_image(center_x, center_y, image=photo, anchor=tk.CENTER)
        else:
            self.canvas.itemconfig(self.canvas_image_id, image=photo)
            self.canvas.coords(self.canvas_image_id, center_x, center_y)

        self.canvas.image = photo
        # Tkinter clears all shapes when you update the image, so we need to redraw the drawn points on top of the new image
        # So we bring the drawn points to the front after updating the image, so they are visible on top of the new image
        for point in self.drawn_points:
            self.canvas.tag_raise(point)
    
    def show_zone(self):
        # Create a Zone object with the drawn points and display it on the canvas
        if self.clicked_points:
            zone = Zone(self.clicked_points)
            # Here you would add code to display the zone on the canvas, e.g. by drawing a polygon using the zone's points
            for i in range(len(zone.points)):
                x1, y1 = zone.points[i]
                x2, y2 = zone.points[(i + 1) % len(zone.points)]  # Wrap around to the first point
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
            print("Zone displayed with points:", zone.points)
        else:
            print("No points drawn to create a zone.")

    
    def __prepare_frame(self, frame):
        # Resize the frame to fit the canvas
        frame = self.__resize_frame(frame)

        # Convert the frame to RGB format from BGR format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to a PIL image
        image = Image.fromarray(frame)

        # Convert the PIL image to a PhotoImage
        photo = ImageTk.PhotoImage(image)

        return photo

    def __resize_frame(self, frame):
        # current canvas dimensions
        current_canvas_w = max(self.canvas.winfo_width(), self.max_width)
        current_canvas_h = max(self.canvas.winfo_height(), self.max_height)

        # Get the dimensions of the frame and calculate the scaling factor to fit it within the canvas while maintaining the aspect ratio
        frame_height, frame_width = frame.shape[:2]
        self.current_img_scale = min(current_canvas_w / frame_width, current_canvas_h / frame_height)
        new_width = int(frame_width * self.current_img_scale)
        new_height = int(frame_height * self.current_img_scale)
        
        # Resize the frame to fit the canvas
        return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    def __return_center(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        centre_x = w // 2 if w > 1 else self.max_width // 2
        centre_y = h // 2 if h > 1 else self.max_height // 2

        return centre_x, centre_y
