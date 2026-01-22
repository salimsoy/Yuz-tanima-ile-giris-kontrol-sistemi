import cv2
import face_recognition
import os
import numpy as np
from facial_recognition import FacialRecognition



class SaveFace:
    def __init__(self):
        # Klasör yoksa oluştur
        os.makedirs('faces', exist_ok=True)
        encodings_path = 'faces'
        # Yardımcı sınıfı FacialRecognition başlatır
        self.face_detect = FacialRecognition()
        # Daha önce kaydedilmiş yüzleri yükle
        self.known_encodings, self.class_names = self.face_detect.load_encodings(encodings_path)
        
        
    def face_detection(self, frame):
        # BGR den RGB ye çevir
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Yüzleri bul
        encodings = face_recognition.face_encodings(img_rgb)
        return encodings
        
    
    def face_save(self, encodings, name):
        # İlk bulunan yüzü kaydet
        np.save(f'faces/{name}_encoding.npy', encodings[0])
        print(f"Yüz verisi (encoding) başarıyla kaydedildi: {name}")
    
    
    def main(self):
        
        name = input("Enter name: ")
        
        try:
            cap = cv2.VideoCapture(0)
            print(f"'{name}' için kayıt başladı. Fotoğraf çekmek için 'c', çıkmak için 'q' basın.")
            
            while True:
                success, frame = cap.read()
                # Eğer kamera açılmazsa veya görüntü gelmezse durdur
                if not success:
                    print("HATA: Kamera açılamadı")
                    break
                
                # Ekranda görüntüyü göster
                cv2.imshow("Kamera", frame)
                
                # Tuş basımını bir değişkene ata
                key = cv2.waitKey(1) & 0xFF
                
                # 'c' tuşuna basılırsa
                if key == ord('c'):
                    img_path = f'faces/{name}.jpg'
                    
                    # Önce resmi diske kaydet
                    cv2.imwrite(img_path, frame)
    
                    # Yüzleri bul
                    encodings = self.face_detection(frame)
                    
                    # Ekranda SADECE 1 yüz olup olmadığını kontrol et
                    if len(encodings) == 1:
                        # Veritabanında kayıtlı yüz varsa karşılaştır
                        if self.known_encodings:
                            min_distance, best_match_index = self.face_detect.face_comparison(self.known_encodings, encodings[0])
                        # Veritabanı boşsa (ilk kayıt), mesafe 1.0 (benzemiyor) kabul et
                        else:
                            min_distance = 1.0
                       
                        # Eğer fark 0.40'tan küçükse, bu kişi zaten kayıtlıdır!
                        if min_distance < 0.40:
                            print("HATA: Aynı yüz mevcut! Lütfen tekrar deneyin.")
                            # Yeni yüz resmini sil
                            if os.path.exists(img_path):
                                os.remove(img_path)
                        else:
                            # İlk bulunan yüzü kaydet
                            self.face_save(encodings, name)
                            return
                        
                    else:
                        print("HATA: Görüntüde yüz bulunamadı yada 1 den fazla yüz var! Lütfen tekrar deneyin.")
                        # Yüz yoksa yada 1 den fazla yüz varsa resmi sil
                        if os.path.exists(img_path):
                            os.remove(img_path)
            
                # 'q' tuşuna basılırsa çık
                elif key == ord('q'):
                    break
        except Exception as e:
            print(f"HATA: {e}")
                
        finally:
            # Sistem güvenli bir şekilde kapatılır
            cap.release()
            cv2.destroyAllWindows()
 

if __name__ == "__main__":
    proses = SaveFace()
    proses.main()