from frame_canvas import FrameCanvas
from control_panel import ControlPanel
import tkinter as tk

class GUIZoneEditor:
    def __init__(self, root):
        self.master = root

        # Set the title and size of the main window
        self.master.title("Zone Editor")
        self.master.geometry("1600x900")

        # Initialize the canvas and control panel
        self.canvas = FrameCanvas(self.master)
        self.panel = ControlPanel(self.master, self.canvas)

    def display(self):
        # Arrange the canvas and control panel in the main window
        self.canvas.pack(side="left",fill="both", expand=True)
        self.panel.pack(side="right", fill="y")

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIZoneEditor(root)
    app.display()
    root.mainloop()