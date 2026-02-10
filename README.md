# Yüz Tanıma İle Giriş Kontrol Sistemi

Bu proje, Python ve OpenCV kullanılarak geliştirilmiş, **modüler mimariye sahip** bir biyometrik güvenlik sistemidir. Karmaşıklığı yönetmek ve kodun okunabilirliğini artırmak amacıyla **"Separation of Concerns" (İlgi Alanlarının Ayrılması)** prensibi gözetilerek tasarlanmıştır.

Sistem; gerçek zamanlı yüz tespiti, kimlik doğrulama, log tutma ve yeni kullanıcı kaydetme işlemlerini birbirinden bağımsız sınıflar üzerinden yönetir.

Kamera görüntülerini anlık olarak işleyerek kişileri tanır ve bir güvenlik görevlisi gibi karar verir. Güvenlik sistemlerine giriş niteliğinde olan bu proje, hem yüz tanıma hem de veri kaydetme (logging) yeteneklerine sahiptir.
Yüz algılama için face_recognition kütüphanesi kullanılmıştır.

**Projenin Amacı**
Sistem kameradan kişiyi algılar ve şu işlemleri yapar:

- Tanıdığı Kişiler: Ekrana "Giriş Başarılı" yazar ve yeşil çerçeve çizer.
- Tanımadığı Kişiler: "Erişim Reddedildi" uyarısı verir.
- Kayıt (Log): Kimin, ne zaman (Tarih/Saat) geldiğini access_log.csv dosyasına kaydeder.

## face_recognition Kütüphanesi
Yüz algılama ve tanıma işlemleri için dünyanın en popüler ve kullanımı en kolay kütüphanelerinden biri olan face_recognition kullanılmıştır.

Neden bu kütüphane?

- Arka planda dlib'in son teknoloji derin öğrenme (deep learning) modellerini kullanır.
- LFW (Labeled Faces in the Wild) veri setinde %99.38 gibi çok yüksek bir doğruluk oranına sahiptir.
- Python ile görüntü işlemeyi basit ve etkili hale getirir.

## Modüller
Sistem iki temel modülden ve dört alt modülden oluşur:

- Yüz Kayıt Modülü: Yeni kişileri web kamerası üzerinden kaydeder, aynı kişinin tekrar kaydedilmesini engeller.
- Yüz Tanıma Modülü: Kayıtlı kişileri tanır, erişim izni verir ve giriş saatlerini bir CSV dosyasına (Excel uyumlu) kaydeder.
## 1. Ana Yürütücü Modüller (Main Scripts)

### A. Yüz Kayıt Modülü (add_user.py)
Bu modül (SaveFace sınıfı), veritabanına yeni kullanıcı eklemek için kullanılır. Basit bir fotoğraf kaydından öte, Mükerrer Kayıt (Duplicate Check) algoritması ile veritabanı bütünlüğünü korur.

**Çalışma Mantığı**

Hazırlık: Kamera açılır ve FaceRecognizer sınıfı mevcut yüz verilerini belleğe yükler.

Yüz Tespiti: Kullanıcı c tuşuna bastığında anlık kare alınır. Eğer karede tek bir yüz yoksa işlem reddedilir.

Benzerlik Kontrolü: Tespit edilen yüz, mevcut kayıtlarla karşılaştırılır.

Eğer benzerlik farkı 0.40'ın altındaysa "Bu kişi zaten kayıtlı" uyarısı verir ve kaydı engeller.

Kayıt: Kontrollerden geçerse yüz verisi hem .jpg (görsel) hem de .npy (matematiksel vektör) olarak kaydedilir.

### B. Yüz Tanıma Ana Modülü (main.py)
Bu modül (FaceAuthApp sınıfı), sistemin ana giriş kapısıdır. Helper sınıfları (Kamera, Tanıma, Loglama, Çizim) bir orkestra şefi gibi yönetir.

**Çalışma Mantığı**

Başlatma: CameraManager, Logger, FaceRecognizer ve FaceDraw sınıfları ayağa kaldırılır. Veritabanı boşsa sistem güvenlik moduna geçmez.

Tanıma Döngüsü:

Kameradan kare okunur.

Yüz tespit edilirse veritabanı ile kıyaslanır.

Eşik değer 0.50 altında ise başarılı üstünde ise başarısız olur.

Aksiyon:

Sonuç "Giriş Başarılı" veya "Erişim Reddedildi" olarak belirlenir.

Logger sınıfı bu durumu CSV dosyasına yazar.

FaceDraw sınıfı yüzü çerçeve içine alır ve sonucu ekrana çizer.

Geri Bildirim: sonucun görülmesi için ekran, klavyeden bir tuşa basılana kadar dondurulur.

## Yardımcı Sınıflar
### FaceRecognizer (Tanıma Motoru)

Veri Yükleme: Başlangıçta faces klasöründeki .npy dosyalarını tarar ve RAM'e yükler. 

Matematiksel Analiz: Görüntüdeki yüzü 128 boyutlu bir vektöre dönüştürür ve kayıtlı vektörlerle kıyaslar.

### CameraManager (Kamera Yöneticisi)

Kamera donanımını başlatma, kare okuma ve güvenli kapatma işlemlerini yönetir.

Hata durumunda (kamera kopması vb.) programın çökmesini engelleyen güvenlik bloklarına sahiptir.

### Logger (Kayıtçı)
Sistemin hafızasıdır.

Tanıma işleminin sonucunu access_log.csv dosyasına kaydeder.

Format: YIL.AY.GÜN SAAT:DAKİKA:SANİYE, İSİM

### FaceDraw (Görselleştirici)

OpenCV kütüphanesini kullanarak tespit edilen yüzün etrafına yeşil çerçeve çizer.

Kişinin ismini ve durum mesajını ekran üzerine estetik bir şekilde yerleştirir.

## 1. Yüz Kayıt Modülü (add_user.py)
```python
import cv2
import face_recognition
import os
import numpy as np
from facial_recognition import FaceRecognizer



class SaveFace:
    def __init__(self):
        # Klasör yoksa oluştur
        os.makedirs('faces', exist_ok=True)
        
        
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
            # Yardımcı sınıfı FacialRecognition başlatır
            recognizer = FaceRecognizer()
            
            
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
                    locations, encodings = recognizer.detect_face(frame)
                    
                    # Ekranda SADECE 1 yüz olup olmadığını kontrol et
                    if len(encodings) == 1:
                        # Veritabanında kayıtlı yüz varsa karşılaştır
                        if recognizer.known_encodings:
                            min_distance, best_match_index = recognizer.face_comparison(recognizer.known_encodings, encodings[0])
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
```
## 2.  Yüz Tanıma Ana Modülü (main.py)
```python
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
            draw = FaceDraw()               # yüz çizdirme
            
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
```

## 3.  Tanıma Motoru (facial_recognition.py)
```python
import face_recognition
import numpy as np
import os
import cv2


class FaceRecognizer:
    
    def __init__(self, encodings_path='faces'):
        self.encodings_path = encodings_path
        self.known_encodings = []
        self.class_names = []
        self.load_database()

    def load_database(self):
        # Kayıtlı yüzleri hafızaya yükler.
        # Klasörün var olup olmadığını kontrol et
        if not os.path.exists(self.encodings_path):
            os.makedirs(self.encodings_path)
            print(f"Klasör oluşturuldu:{self.encodings_path}")
            return
        # Klasördeki tüm dosyaları tek tek gezer
        for file in os.listdir(self.encodings_path):
            # Sadece .npy uzantılı (NumPy Array) dosyaları alır
            if file.endswith(".npy"):
                name = file.split('_')[0]
                encoding = np.load(os.path.join(self.encodings_path, file))
                self.known_encodings.append(encoding)
                self.class_names.append(name)
        print(f"{len(self.class_names)} kişi yüklendi.")
        
    def face_comparison(self, known_encodings, face_encoding):
        # Herkesle olan mesafeyi ölç
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        # Eğer veritabanında en az bir kişi varsa işlem yap
        if len(face_distances) > 0:
            # En küçük mesafeye sahip indeksi bulur
            best_match_index = np.argmin(face_distances)
            min_distance = face_distances[best_match_index]
   
        return min_distance, best_match_index
    
    def detect_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Yüzün kare içindeki koordinatlarını bulur
        face_locations = face_recognition.face_locations(rgb_frame)
        # Yüzün matematiksel modelini (encoding) çıkarır
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        return face_locations, face_encodings

    def identify(self, face_encoding):
        name = "Bilinmiyor"
        if not self.known_encodings:
            return "Bilinmiyor"

        min_distance, best_match_index = self.face_comparison(self.known_encodings, face_encoding)
        if min_distance < 0.50:
            name = self.class_names[best_match_index]
            print("Giriş başarılı")
        else:
            print("Erişim reddedildi")
        
        return name
```
## 4.  Kamera Yöneticisi (camera_manager.py)
```python
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
```
## 5.  Kayıtçı (logger.py)
```python
import csv
import os
from datetime import datetime

class Logger:
    def __init__(self, filename='access_log.csv'):
        self.filename = filename
        # Dosya yoksa başlıkları oluşturabiliriz
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Tarih_Saat", "Isim"]) # Başlık ekledik

    def log_access(self, name):
        """İsim ve saati CSV dosyasına kaydeder."""
        try:
            with open(self.filename, "a", newline="") as f:
                now = datetime.now()
                date_str = now.strftime('%Y.%m.%d %H:%M:%S')
                
                writer = csv.writer(f)
                writer.writerow([date_str, name])
                print("Log kaydedildi")
        except Exception as e:
            print(f"HATA: {e}")
```
## 6.  Görselleştirici (face_draw.py)
```python
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
```
