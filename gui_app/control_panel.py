import tkinter as tk
from core.zone import Zone

class ControlPanel(tk.Frame):
    def __init__(self, parent, canvas):
        super().__init__(parent)
        self.canvas = canvas
        self.create_widgets()

    def create_widgets(self):
        self.start_drawing_button = tk.Button(self, text="Start Drawing", command=self.start_drawing)
        self.start_drawing_button.pack(pady=10)

        self.save_zone_button = tk.Button(self, text="Save Zone", command=self.save_zone)
        self.save_zone_button.pack(pady=10)

        self.select_frame_button = tk.Button(self, text="Select Frame", command=self.select_frame)
        self.select_frame_button.pack(pady=10)

        self.show_zones_button = tk.Button(self, text="Show Zones", command=self.show_zones)
        self.show_zones_button.pack(pady=10)

    def start_drawing(self):
        self.canvas.drawing = True
        print("Start Drawing button clicked")

    def show_zones(self):
        print("Show Zones button clicked")
        self.canvas.show_zone()

    def select_frame(self):
        print("Select Frame button clicked")
        self.canvas.save_frame()

    def save_zone(self):
        if self.canvas.drawing:
            self.canvas.drawing = False
            print("Finished drawing zone with points:", self.canvas.drawn_points)
            # Here you would create a Zone object and save it using the points in self.canvas.drawn_points
            zone = Zone(self.canvas.drawn_points)
            zone.save_zone()
            self.canvas.drawn_points = [] # Clear the drawn points after saving
            self.canvas.drawn_points_current_resolution = [] # Clear the drawn points in current resolution after saving
            self.canvas.clicked_points = [] # Clear the clicked points after saving
        print("Save Zone button clicked")