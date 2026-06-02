import tkinter as tk
from core.zone import Zone


# Control panel displayed on the right-hand side of the GUI.
# Contains all buttons used to interact with the zone editor.
class ControlPanel(tk.Frame):

    def __init__(self, parent, canvas):
        # Create a fixed-width frame for the control panel.
        super().__init__(parent, width=300, bg="lightgray")

        # Prevent the frame from shrinking to fit its contents.
        self.pack_propagate(False)

        # Reference to the FrameCanvas object so buttons can access canvas functions.
        self.canvas = canvas

        self.create_widgets()

    def create_widgets(self):
        # List of all buttons and their associated callback functions.
        buttons = [
            ("Start Drawing", self.start_drawing),
            ("Save Zone", self.save_zone),
            ("Select Frame", self.select_frame),
            ("Show Zone", self.show_zones),
            ("Undo Last Point", self.undo_last_point),
            ("Clear Current Zone", self.clear_current_zone),
            ("Save Snapshot With Zones", self.save_snapshot_with_zones),
        ]

        # Create and display all buttons.
        for text, command in buttons:
            button = tk.Button(self, text=text, command=command)
            button.pack(fill="x", padx=15, pady=8)

    # Enable point placement mode.
    def start_drawing(self):
        self.canvas.drawing = True
        self.canvas.editing = False
        print("Drawing mode started.")

    # Save the currently drawn polygon as a zone.
    def save_zone(self):
        # A valid polygon requires at least three vertices.
        if len(self.canvas.drawn_points) < 3:
            print("A zone needs at least 3 points.")
            return

        self.canvas.drawing = False
        self.canvas.editing = True

        zone = Zone(self.canvas.drawn_points)
        zone.save_zone()

        print("Zone saved with points:", self.canvas.drawn_points)

    # Freeze the current camera frame.
    def select_frame(self):
        self.canvas.save_frame()

    # Display a closed polygon on the canvas.
    def show_zones(self):
        self.canvas.show_zone()

    # Remove the most recently added point.
    def undo_last_point(self):
        self.canvas.undo_last_point()

    # Remove all points and drawings from the current zone.
    def clear_current_zone(self):
        self.canvas.clear_current_zone()

    # Save an image containing the frame and zone overlay.
    def save_snapshot_with_zones(self):
        self.canvas.save_snapshot_with_zones()