from shapely.geometry import Polygon
import os
import json

class Zone:
    def __init__(self, points):
        # Initialize relevant variables
        self.points = points
        self.zone_id = None
        self.polygon = None
        self.file_path = os.path.join(os.getcwd(), 'data', 'zones.json')
        self.data = [] # Initialize an empty list to store zone data
        self.__build_polygon()
        self.__build_zone_id()
    
    def __build_polygon(self):
        # Create a Shapely polygon from the list of points
        self.polygon = Polygon(self.points)
    
    def __build_zone_id(self):
        # Get the file path using the current working directory and the zone_id
        file_path = self.file_path

        # Does the file exist?
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:

                # Load the existing data from the file
                data = json.load(f)
                print(f"Existing zones loaded from {file_path}: {data}, Length: {len(data)}")
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
        self.data = self.load_data()
        # Create a dictionary to store the zone data
        zone_data = {
            'zone_id': self.zone_id,
            'points': self.points
        }

        self.data.append(zone_data)

        # Save the zone data to a JSON file
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def load_data(self):
        # Load the zone data from a JSON file
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            print(f"Zone data loaded from {self.file_path}: {data}")
            return data
    
    def check_intersection(self, bounding_box):
        # Check if the bounding box intersects with the zone polygon
        return self.polygon.intersects(bounding_box.convert_to_polygon())
    

class ZoneLoader:
    def __init__(self):
        self.file_path = os.path.join(os.getcwd(), 'data', 'zones.json')
        self.zones = []
        self.load_zones()
    
    def load_zones(self):
        # Load zones from the JSON file and create Zone objects
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            print(f"Zone data loaded from {self.file_path}: {data}")
            for zone_data in data:
                zone = Zone(zone_data['points'])
                zone.zone_id = zone_data['zone_id']
                self.zones.append(zone)