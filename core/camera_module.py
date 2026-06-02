import cv2

class CameraModule:
    def __init__(self):
        # Raspberry Pi camera stream URL
        self.PI_IP = "192.168.2.7"        
        self.webcam_capture = None
        self.raspberry_pi_capture = None

    def get_webcam_capture(self):
        if self.webcam_capture is None:
            self.webcam_capture = cv2.VideoCapture(0)

            if not self.webcam_capture.isOpened():
                print("Error: Cannot open webcam")
                exit()

        return self.webcam_capture

    def get_raspberry_pi_capture(self):
        if self.raspberry_pi_capture is None:
            stream_url = f"http://{self.PI_IP}:8080/video"
            self.raspberry_pi_capture = cv2.VideoCapture(stream_url)

            if not self.raspberry_pi_capture.isOpened():
                print(f"Error: Cannot open Raspberry Pi camera stream at {stream_url}")
                exit()

        return self.raspberry_pi_capture
    
