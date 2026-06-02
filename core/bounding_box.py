import shapely

class BoundingBox:
    def __init__(self, x1, y1, x2, y2, confidence, label):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.confidence = confidence
        self.label = label
    
    def convert_to_polygon(self):
        # Convert the bounding box to a Shapely polygon
        return shapely.geometry.box(self.x1, self.y1, self.x2, self.y2)