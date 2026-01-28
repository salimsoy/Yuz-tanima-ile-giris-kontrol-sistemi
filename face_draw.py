import cv2


class FaceDraw:
    
    def face_drawing(self, frame, name, face_location):
        names = name.upper()
        y1, x2, y2, x1 = face_location
        # Yüzün etrafına dikdörtgen çizer ve 
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) 
        cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED) 
        cv2.putText(frame, names, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
        return frame