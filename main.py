import sys
import os
from core.system_controller import SystemController

# Look for imports starting from the project root.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

system_controller = SystemController()
system_controller.start_system(camera_source="webcam")