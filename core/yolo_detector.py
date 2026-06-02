import cv2
from ultralytics import YOLO
from core.camera_module import CameraModule
from core.bounding_box import BoundingBox

class YOLODetector:
    def __init__(self):
        # Initialize camera module
        self.camera = CameraModule()

        # Load YOLOv8n model (downloads automatically first time)
        self.model = YOLO("models/yolov8n.pt")

    def return_results(self, frame):
        # Run YOLO inference
        results = self.model(frame, imgsz=640, conf=0.5, verbose=False)

        return results

    def get_person_bounding_boxes(self, frame, results):

        # Extract bounding boxes for detected persons
        person_boxes = []
        for result in results:
            for box in result.boxes:
                if box.cls == 0:  # Class 0 corresponds to 'person' in COCO dataset
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    person_boxes.append(BoundingBox(x1, y1, x2, y2, confidence, "person"))

        return person_boxes
    
    def return_annotated_frame(self, frame, results):

        # Draw detections
        annotated_frame = results[0].plot()

        return annotated_frame
    