import cv2
from core.camera_module import CameraModule
from core.yolo_detector import YOLODetector
from core.zone import ZoneLoader
import os

class SystemController:
    def __init__(self):
        # Initialize components
        self.camera_module = CameraModule()
        self.yolo_detector = YOLODetector()
        self.zones = ZoneLoader().zones
    
    def start_system(self, camera_source="webcam"):
        # Get camera capture
        if camera_source == "webcam":
            cap = self.camera_module.get_webcam_capture()
        elif camera_source == "raspberry_pi":
            cap = self.camera_module.get_raspberry_pi_capture()

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Failed to grab frame")
                break

            results = self.yolo_detector.return_results(frame)
            persons = self.yolo_detector.get_person_bounding_boxes(frame, results)
            annotated_frame = self.yolo_detector.return_annotated_frame(frame, results)

            # Check for intersections with zones here
            for person in persons:
                for zone in self.zones:
                    if zone.check_intersection(person):
                        print(f"Person detected in zone {zone.zone_id}!")
                        # Write detection text on annotated frame
                        cv2.putText(annotated_frame, f"Detected in Zone {zone.zone_id}", (int(person.x1), int(person.y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("Annotated Feed", annotated_frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    
    def stop_system(self):
        # Clean up resources if needed
        pass