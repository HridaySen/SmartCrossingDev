import tkinter as tk

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

    def start_drawing(self):
        # Placeholder for starting the drawing process
        print("Start Drawing button clicked")

    def select_frame(self):
        # Placeholder for selecting a frame
        print("Select Frame button clicked")

        self.canvas.save_frame()

    def save_zone(self):
        # Placeholder for saving a zone
        print("Save Zone button clicked")