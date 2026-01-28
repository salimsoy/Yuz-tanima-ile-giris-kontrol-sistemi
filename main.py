import cv2 
from facial_recognition import FaceRecognizer
from camera_manager import CameraManager
from logger import Logger
from face_draw import FaceDraw



class FaceAuthApp:
    
    
    def main(self):
        
        try:
            cam = CameraManager(0)          # kamera
            recognizer = FaceRecognizer()   # yüz algılama karşılaştırma
            logger = Logger()               # kaydetme
            draw = FaceDraw()
            
        except Exception as e:
            print(f"Sistem başlatılamadı: {e}")
            return
    
        print("Sistem Çalışıyor... Çıkmak için 'q' basın.")
        if not recognizer.known_encodings:
            print("HATA: Veritabanı boş Lütfen önce kişi kaydedin")
            return
        
        try:
            
            while True:
                success, frame = cam.get_frame()
                if not success:
                    print("HATA: Kamera açılamadı")
                    break
                
                # Görüntüdeki yüzleri analiz et
                face_locations, face_encodings = recognizer.detect_face(frame)
                # Ekranda 1 Yüz Varsa çalıştır yoksa uyarı ver
                if len(face_locations) == 1:
                    face_encoding = face_encodings[0]
                    face_location = face_locations[0]
                   
                    # Bulunan yüzü kayıtlı yüzlerle karşılaştırma
                    # Eğer mesafe 0.50'den küçükse tanı, yoksa tanıma.
                    name = recognizer.identify(face_encoding)
                    
                    # CSV Dosyasına Kaydeder
                    logger.log_access(name)
                    
                    # Ekrana Çizim Yap
                    frame = draw.face_drawing(frame, name, face_location)
                    
                    cv2.imshow("Kamera", frame)
                    cv2.waitKey(0)
                    
                    return
                
                elif len(face_locations) == 0:
                    cv2.putText(frame, "Yuz Bulunamadi", (20, 20), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)
                    
                else:
                    cv2.putText(frame, "Birden Fazla Yuz Var", (20, 20), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)
                
                cv2.imshow("Kamera", frame)       
                
                # 'q' tuşuna basılırsa manuel çıkış yap
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
        except Exception as e:
            # Beklenmedik bir hata olursa program çökmesin, hatayı yazar
            print(f"HATA: {e}")
                
        finally:
            # Sistem güvenli bir şekilde kapatılır
            cam.stop()
            
    
        
if __name__ == "__main__":
    proses = FaceAuthApp()
    proses.main()