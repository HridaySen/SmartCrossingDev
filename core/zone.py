from shapely.geometry import Polygon
import os
import json

class Zone:
    def __init__(self, points):
        # Initialize relevant variables
        self.points = points
        self.__build_polygon()
        self.__build_zone_id()
    
    def __build_polygon(self):
        # Create a Shapely polygon from the list of points
        self.polygon = Polygon(self.points)
    
    def __build_zone_id(self):
        # Get the file path using the current working directory and the zone_id
        file_path = os.path.join(os.getcwd(), 'data', 'zones.json')
        
        # Does the file exist?
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:

                # Load the existing data from the file
                data = json.load(f)

                # If the file is empty, set the zone_id to 0, otherwise set it to the total number of zones + 1
                if data == None:
                    self.zone_id = 0
                else:
                    total_zones = len(data)
                    self.zone_id = total_zones + 1
        else:
            print(f"File {file_path} does not exist. Creating new file.")

    def save_zone(self):
        # Get the file path using the current working directory and the zone_id
        file_path = os.path.join(os.getcwd(), 'data', 'zones.json')

        # Create a dictionary to store the zone data
        zone_data = {
            'zone_id': self.zone_id,
            'points': self.points
        }

        # Save the zone data to a JSON file
        with open(file_path, 'w') as f:
            json.dump(zone_data, f, indent=4)

# Example usage, just initial test
zone = Zone([(0, 0), (1, 0), (1, 1), (0, 1)])
zone.save_zone()