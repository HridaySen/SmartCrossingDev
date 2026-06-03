import tkinter as tk
import sys
import os
import cv2
from PIL import Image, ImageTk

# Look for imports starting from the project root.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.camera_module import CameraModule


class FrameCanvas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Maximum canvas display size.
        self.max_width = 1500
        self.max_height = 860

        # Label for displaying real frame coordinates under the mouse.
        # It is packed first at the bottom so the canvas cannot hide it.
        self.coordinate_label = tk.Label(
            self,
            text="Coordinates: X = -, Y = -",
            anchor="w"
        )
        self.coordinate_label.pack(side=tk.BOTTOM, fill="x")

        # Create canvas where the camera frame and zone overlay are displayed.
        self.canvas = tk.Canvas(
            self,
            bg="red",
            width=self.max_width,
            height=self.max_height
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Drawing/editing states.
        self.drawing = False
        self.editing = True

        # Points are stored in original camera-frame coordinates.
        self.drawn_points = []

        # Current displayed image information.
        self.current_img_w = 0
        self.current_img_h = 0
        self.current_img_scale = 1.0
        self.zoom_factor = 1.0

        # Canvas image and overlay tracking.
        self.canvas_image_id = None
        self.overlay_ids = []

        # Used for dragging/editing existing points.
        self.selected_point_index = None

        # Controls whether the final closing edge of the polygon is shown.
        self.closed_zone_visible = False

        # Initialize camera through CameraModule.
        self.capture = CameraModule().get_webcam_capture()

        # Set camera resolution.
        # This version uses 640x480, so the saved zone coordinates
        # will match this camera resolution.
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Store latest frame for freezing, zooming, and snapshot saving.
        self.last_frame = None

        # Store Tkinter after() loop ID so it can be cancelled.
        self.loop_id = None
        self.feed_running = True

        # Mouse bindings.
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag_point)
        self.canvas.bind("<ButtonRelease-1>", self.on_release_point)
        self.canvas.bind("<Motion>", self.show_real_coordinates)

        # Windows/macOS mouse wheel.
        self.canvas.bind("<MouseWheel>", self.zoom)

        # Linux mouse wheel.
        self.canvas.bind("<Button-4>", self.zoom)
        self.canvas.bind("<Button-5>", self.zoom)

        # Start camera feed.
        self.show_feed()

    def show_feed(self):
        # Continuously update live camera feed without freezing the GUI.
        if not self.feed_running:
            return

        ret, frame = self.capture.read()

        if ret:
            self.last_frame = frame.copy()
            self.display_frame(frame)

        self.loop_id = self.after(15, self.show_feed)

    def save_frame(self):
        # Freeze and save the current camera frame.
        ret, frame = self.capture.read()

        if not ret:
            print("Could not read frame from camera.")
            return

        self.last_frame = frame.copy()

        cv2.imwrite("frame_chosen.jpg", frame)

        # Stop live feed after frame selection.
        self.feed_running = False

        if self.loop_id is not None:
            self.after_cancel(self.loop_id)
            self.loop_id = None

        self.display_frame(frame)

        print("Frame saved as frame_chosen.jpg")

    def display_frame(self, frame):
        # Prepare frame for Tkinter and redraw overlays.
        photo = self.__prepare_frame(frame)
        self.__update_canvas(photo)
        self.__redraw_overlay()

    def on_canvas_click(self, event):
        # Convert click location to original camera-frame coordinates.
        original_point = self.canvas_to_original_coordinates(event.x, event.y)

        if original_point is None:
            print("Clicked outside the camera frame. Ignored.")
            return

        # Drawing mode: clicking adds a new point.
        if self.drawing:
            self.drawn_points.append(original_point)
            self.closed_zone_visible = False
            self.__redraw_overlay()

            print(f"Point added: X={original_point[0]}, Y={original_point[1]}")
            return

        # Editing mode: clicking near an existing point selects it.
        if self.editing:
            self.selected_point_index = self.find_nearest_point(event.x, event.y)

            if self.selected_point_index is not None:
                print(f"Selected point {self.selected_point_index + 1} for editing.")
            else:
                print("No point selected.")

    def on_drag_point(self, event):
        # Drag selected point to a new position.
        if not self.editing:
            return

        if self.selected_point_index is None:
            return

        original_point = self.canvas_to_original_coordinates(event.x, event.y)

        if original_point is None:
            return

        self.drawn_points[self.selected_point_index] = original_point
        self.__redraw_overlay()

        x, y = original_point
        self.coordinate_label.config(
            text=f"Coordinates: X = {int(x)}, Y = {int(y)}"
        )

    def on_release_point(self, event):
        # Stop editing the selected point.
        if self.selected_point_index is not None:
            print(f"Released point {self.selected_point_index + 1}.")

        self.selected_point_index = None

    def undo_last_point(self):
        # Remove most recently added point.
        if not self.drawn_points:
            print("No points to undo.")
            return

        removed_point = self.drawn_points.pop()
        self.closed_zone_visible = False
        self.__redraw_overlay()

        print("Removed last point:", removed_point)

    def clear_current_zone(self):
        # Clear all points and remove overlay drawings.
        self.drawn_points = []
        self.selected_point_index = None
        self.closed_zone_visible = False
        self.__clear_overlay()

        print("Current zone cleared.")

    def show_zone(self):
        # Display closed polygon.
        if len(self.drawn_points) < 3:
            print("A zone needs at least 3 points.")
            return

        self.closed_zone_visible = True
        self.editing = True
        self.drawing = False

        self.__redraw_overlay()

        print("Zone displayed.")

    def save_snapshot_with_zones(self):
        # Save current frame with zone points, labels, and polygon lines drawn on it.
        if self.last_frame is None:
            print("No frame available to save.")
            return

        snapshot = self.last_frame.copy()

        if len(self.drawn_points) >= 2:
            points = [(int(x), int(y)) for x, y in self.drawn_points]

            # Draw edges between consecutive points.
            for i in range(len(points) - 1):
                cv2.line(snapshot, points[i], points[i + 1], (255, 0, 0), 3)

            # Close polygon if it has at least 3 points.
            if len(points) >= 3:
                cv2.line(snapshot, points[-1], points[0], (255, 0, 0), 3)

            # Draw point markers and numbers.
            for index, point in enumerate(points):
                cv2.circle(snapshot, point, 7, (0, 255, 0), -1)

                cv2.putText(
                    snapshot,
                    str(index + 1),
                    (point[0] + 10, point[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

        cv2.imwrite("frame_with_zones.jpg", snapshot)

        print("Snapshot saved as frame_with_zones.jpg")

    def show_real_coordinates(self, event):
        # Show original camera-frame coordinates under the mouse.
        original_point = self.canvas_to_original_coordinates(event.x, event.y)

        if original_point is None:
            self.coordinate_label.config(text="Coordinates: outside frame")
            return

        x, y = original_point

        self.coordinate_label.config(
            text=f"Coordinates: X = {int(x)}, Y = {int(y)}"
        )

    def zoom(self, event):
        # Mouse wheel zoom.
        # The checks with hasattr make this more stable across Windows, macOS, and Linux.
        if hasattr(event, "num") and event.num == 4:
            self.zoom_factor *= 1.1
        elif hasattr(event, "num") and event.num == 5:
            self.zoom_factor /= 1.1
        elif hasattr(event, "delta") and event.delta > 0:
            self.zoom_factor *= 1.1
        elif hasattr(event, "delta") and event.delta < 0:
            self.zoom_factor /= 1.1

        # Limit zoom level.
        self.zoom_factor = max(0.3, min(self.zoom_factor, 4.0))

        if self.last_frame is not None:
            self.display_frame(self.last_frame)

        print(f"Zoom factor: {self.zoom_factor:.2f}")

    def find_nearest_point(self, canvas_x, canvas_y):
        # Find nearest existing point for editing.
        # A larger threshold makes selecting points easier.
        threshold = 25

        nearest_index = None
        nearest_distance = float("inf")

        for index, point in enumerate(self.drawn_points):
            point_canvas = self.original_to_canvas_coordinates(point[0], point[1])

            if point_canvas is None:
                continue

            px, py = point_canvas

            distance = ((canvas_x - px) ** 2 + (canvas_y - py) ** 2) ** 0.5

            if distance < nearest_distance and distance <= threshold:
                nearest_distance = distance
                nearest_index = index

        return nearest_index

    def canvas_to_original_coordinates(self, canvas_x, canvas_y):
        # Convert canvas coordinates to original camera-frame coordinates.
        if self.last_frame is None:
            return None

        if self.current_img_w == 0 or self.current_img_h == 0:
            return None

        frame_h, frame_w = self.last_frame.shape[:2]

        center_x, center_y = self.__return_center()

        img_start_x = center_x - (self.current_img_w / 2)
        img_start_y = center_y - (self.current_img_h / 2)

        frame_click_x = canvas_x - img_start_x
        frame_click_y = canvas_y - img_start_y

        # Ignore clicks outside displayed frame.
        if not (
            0 <= frame_click_x <= self.current_img_w
            and 0 <= frame_click_y <= self.current_img_h
        ):
            return None

        original_x = frame_click_x / self.current_img_scale
        original_y = frame_click_y / self.current_img_scale

        # Clamp values inside actual frame size.
        original_x = max(0, min(original_x, frame_w - 1))
        original_y = max(0, min(original_y, frame_h - 1))

        return original_x, original_y

    def original_to_canvas_coordinates(self, original_x, original_y):
        # Convert original camera-frame coordinates to displayed canvas coordinates.
        if self.last_frame is None:
            return None

        if self.current_img_w == 0 or self.current_img_h == 0:
            return None

        center_x, center_y = self.__return_center()

        img_start_x = center_x - (self.current_img_w / 2)
        img_start_y = center_y - (self.current_img_h / 2)

        canvas_x = img_start_x + original_x * self.current_img_scale
        canvas_y = img_start_y + original_y * self.current_img_scale

        return canvas_x, canvas_y

    def release_camera(self):
        # Stop feed loop and release camera.
        self.feed_running = False

        if self.loop_id is not None:
            self.after_cancel(self.loop_id)
            self.loop_id = None

        if self.capture is not None and self.capture.isOpened():
            self.capture.release()

    def __prepare_frame(self, frame):
        # Resize frame to fit canvas and convert it for Tkinter display.
        frame = self.__resize_frame(frame)

        # OpenCV uses BGR; Tkinter/PIL expects RGB.
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)

        return photo

    def __resize_frame(self, frame):
        # Resize frame while maintaining aspect ratio.
        current_canvas_w = max(self.canvas.winfo_width(), self.max_width)
        current_canvas_h = max(self.canvas.winfo_height(), self.max_height)

        frame_height, frame_width = frame.shape[:2]

        base_scale = min(
            current_canvas_w / frame_width,
            current_canvas_h / frame_height
        )

        self.current_img_scale = base_scale * self.zoom_factor

        new_width = int(frame_width * self.current_img_scale)
        new_height = int(frame_height * self.current_img_scale)

        return cv2.resize(
            frame,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

    def __update_canvas(self, photo):
        # Update displayed image.
        self.current_img_w = photo.width()
        self.current_img_h = photo.height()

        center_x, center_y = self.__return_center()

        if self.canvas_image_id is None:
            self.canvas_image_id = self.canvas.create_image(
                center_x,
                center_y,
                image=photo,
                anchor=tk.CENTER
            )
        else:
            self.canvas.itemconfig(self.canvas_image_id, image=photo)
            self.canvas.coords(self.canvas_image_id, center_x, center_y)

        # Keep reference to avoid garbage collection.
        self.canvas.image = photo

    def __redraw_overlay(self):
        # Redraw points, point numbers, and polygon lines.
        self.__clear_overlay()

        if not self.drawn_points:
            return

        canvas_points = [
            self.original_to_canvas_coordinates(x, y)
            for x, y in self.drawn_points
        ]

        canvas_points = [
            point for point in canvas_points
            if point is not None
        ]

        # Draw lines between consecutive points.
        for i in range(len(canvas_points) - 1):
            x1, y1 = canvas_points[i]
            x2, y2 = canvas_points[i + 1]

            line_id = self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="blue",
                width=2,
                tags=("zone_overlay",)
            )

            self.overlay_ids.append(line_id)

        # Draw closing line if requested.
        if self.closed_zone_visible and len(canvas_points) >= 3:
            x1, y1 = canvas_points[-1]
            x2, y2 = canvas_points[0]

            line_id = self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="blue",
                width=2,
                tags=("zone_overlay",)
            )

            self.overlay_ids.append(line_id)

        # Draw green points and point numbers.
        for index, point in enumerate(canvas_points):
            x, y = point

            # Slightly larger radius makes points easier to select for editing.
            radius = 7

            point_id = self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="green",
                outline="black",
                width=1.5,
                tags=("zone_overlay", "zone_point")
            )

            text_id = self.canvas.create_text(
                x + 14,
                y - 14,
                text=str(index + 1),
                fill="white",
                font=("Arial", 12, "bold"),
                tags=("zone_overlay",)
            )

            self.overlay_ids.append(point_id)
            self.overlay_ids.append(text_id)

    def __clear_overlay(self):
        # Remove all existing overlay drawings.
        for item_id in self.overlay_ids:
            self.canvas.delete(item_id)

        self.overlay_ids = []

    def __return_center(self):
        # Return current canvas center.
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        center_x = w // 2 if w > 1 else self.max_width // 2
        center_y = h // 2 if h > 1 else self.max_height // 2

        return center_x, center_y