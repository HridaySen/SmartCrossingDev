# Usage Instructions

First ensure you have vscode and python already installed. 

## Installation Guide
1. Clone this repo from github: https://github.com/HridaySen/SmartCrossingDev.git
2. Then the folder where core, data etc is a direct sub-folder, open that folder in the vscode terminal.
3. type: python -m venv venv
4. then type: venv\Scripts\activate
5. then type: pip install -r requirements_dev.txt
6. Now ensure you have a camera in your laptop.

## How to run?
1. In the same terminal in step 5, type: python gui_app/gui_zone_editor.py
2. Then you should see your camera displayed in the app. 
3. Now pick a frame that you want to use to make zones and click: select frame button. 
4. Then click on "start drawing" button.
5. Then start clicking on the image. Once you have at least 3 points clicked, click: "show zones"
6. Click "save zones"
7. You can check the saved zones in zones.json in the 1920x1080 cartesian plane space (NOT YOUR SCREEN SCALE)