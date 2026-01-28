import cv2

class CameraManager:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise ValueError("Kamera açılamadı")

    def get_frame(self):
        
        success, frame = self.cap.read()
        if success:
            return True, frame
        return False, None

    def stop(self):
        
        self.cap.release()
        cv2.destroyAllWindows()