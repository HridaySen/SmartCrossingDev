import tkinter as tk
from frame_canvas import FrameCanvas
from control_panel import ControlPanel


# Main application window.
# Creates and arranges the canvas and control panel.
class GUIZoneEditor:

    def __init__(self, root):
        self.master = root

        # Configure application window.
        self.master.title("Zone Editor")
        self.master.geometry("1800x900")

        # Create main GUI components.
        self.canvas = FrameCanvas(self.master)
        self.panel = ControlPanel(self.master, self.canvas)

        # Ensure camera resources are released on exit.
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def display(self):
        # Place control panel on the right and
        # allow the canvas to occupy the remaining space.
        self.panel.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

    def on_close(self):
        # Cleanly release camera resources before exiting.
        self.canvas.release_camera()
        self.master.destroy()


if __name__ == "__main__":
    # Create and start the application.
    root = tk.Tk()
    app = GUIZoneEditor(root)
    app.display()
    root.mainloop()