import cv2 
import face_recognition 
import numpy as np 
import os
import csv
from datetime import datetime



class FacialRecognition:
    
    def __init__(self):
    
        self.encodings_path = 'faces'
        
        # Eğer faces klasörü yoksa oluşturur.
        if not os.path.exists(self.encodings_path):
            os.makedirs(self.encodings_path)
            print(f"Uyarı: '{self.encodings_path}' klasörü bulunamadı, yeni oluşturuldu.")
        
        # Klasördeki kayıtlı yüzlerin Yükleme işlemini yapar
        self.known_encodings, self.class_names = self.load_encodings(self.encodings_path)
        
        print(f"Sistem Başlatıldı Yüklenen kişi sayısı: {len(self.class_names)}")
        print(f"Kişiler: {self.class_names}")
        
    
    def load_encodings(self,encodings_path): 
        encodings = [] 
        class_names = [] 
        # Klasörün var olup olmadığını kontrol et
        if not os.path.exists(encodings_path):
            print(f"Hata: '{encodings_path}' klasörü bulunamadı.")
            return [], []
       
        # Klasördeki tüm dosyaları tek tek gezer
        for file in os.listdir(encodings_path): 
            # Sadece .npy uzantılı (NumPy Array) dosyaları alır
            if file.endswith(".npy"): 
                class_name = file.split('_')[0] 
                # Matematiksel yüz verisini yükler
                encoding = np.load(os.path.join(encodings_path, file)) 
                encodings.append(encoding) 
                class_names.append(class_name) 
        return encodings, class_names
    
    
    def detect_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Yüzün kare içindeki koordinatlarını bulur
        face_locations = face_recognition.face_locations(rgb_frame)
        # Yüzün matematiksel modelini (encoding) çıkarır
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        return face_locations, face_encodings
    
    
    def face_comparison(self, known_encodings, face_encoding):
        # Herkesle olan mesafeyi ölç
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        # Eğer veritabanında en az bir kişi varsa işlem yap
        if len(face_distances) > 0:
            # En küçük mesafeye sahip indeksi bulur
            best_match_index = np.argmin(face_distances)
            min_distance = face_distances[best_match_index]
   
        return min_distance, best_match_index
            
        
    def face_drawing(self, frame, name, y1, x2, y2, x1):
        name = name.upper()
        # Yüzün etrafına dikdörtgen çizer ve 
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) 
        cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED) 
        cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
        return frame
    

    def add_record_log(self, name):
        filename = 'access_log.csv'
        # Dosya yoksa başlık satırı açmak veya oluşturmak için kontrol eder
        if not os.path.exists(filename):
            with open(filename, 'w') as f: pass

        with open(filename, "a", newline="") as f: # Ekleme modunda açar
        
            now = datetime.now()
            # Saat formatı
            dtString = now.strftime('%H:%M:%S')
            # Tarih formatı
            dateString = now.strftime('%Y.%m.%d') 
            # Tarih ve Saati birleştirme
            date_marge = dateString + " " + dtString
            # Veriyi yazar
            writer = csv.writer(f)
            writer.writerow([date_marge, name])
            print(f"KAYIT EKLENDİ: {name}")
        
    
    def main(self):
        if not self.known_encodings:
            print("HATA: Veritabanı boş Lütfen önce kişi kaydedin")
            return
        
        try:
            cap = cv2.VideoCapture(0)
            while True:
                success, frame = cap.read()
                if not success:
                    print("HATA: Kamera açılamadı")
                    break
                
                # Görüntüdeki yüzleri analiz et
                face_locations, face_encodings = self.detect_face(frame)
                # Ekranda 1 Yüz Varsa çalıştır yoksa uyarı ver
                if len(face_locations) == 1:
                    face_encoding = face_encodings[0]
                    face_location = face_locations[0]
                   
                    name = "Bilinmiyor"
                    # Bulunan yüzü kayıtlı yüzlerle karşılaştırma
                    min_distance, best_match_index = self.face_comparison(self.known_encodings, face_encoding)
                    
                    # Eğer mesafe 0.50'den küçükse tanı, yoksa tanıma.
                    if min_distance < 0.50:
                        name = self.class_names[best_match_index]
                        print("Giriş başarılı")
                    else:
                        print("Erişim reddedildi")
                    
                    # CSV Dosyasına Kaydeder
                    self.add_record_log(name)
                    # Ekrana Çizim Yap
                    y1, x2, y2, x1 = face_location 
                    frame = self.face_drawing(frame, name, y1, x2, y2, x1)
                    
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
            cap.release()
            cv2.destroyAllWindows()
            
    
        
if __name__ == "__main__":
    proses = FacialRecognition()
    proses.main()