import tkinter as tk

class ControlPanel(tk.Frame):
    def __init__(self, parent, canvas):
        super().__init__(parent)
        self.canvas = canvas
        self.create_widgets()

    def create_widgets(self):
        self.add_zone_button = tk.Button(self, text="Add Zone", command=self.add_zone)
        self.add_zone_button.pack(pady=10)

    def add_zone(self):
        # Placeholder for adding a zone to the canvas
        print("Add Zone button clicked")