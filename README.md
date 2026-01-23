# Yüz Tanıma İle Giriş Kontrol Sistemi
Bu proje, gerçek zamanlı çalışan akıllı bir Güvenlik ve Yoklama Sistemidir.

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
Sistem iki temel modülden oluşur:

- Yüz Kayıt Modülü: Yeni kişileri web kamerası üzerinden kaydeder, aynı kişinin tekrar kaydedilmesini engeller.
- Yüz Tanıma Modülü: Kayıtlı kişileri tanır, erişim izni verir ve giriş saatlerini bir CSV dosyasına (Excel uyumlu) kaydeder.

## 1. Yüz Kayıt Modülü (SaveFace)
Bu modül (add_user.py), veritabanına yeni kullanıcı eklemek için kullanılır. Basit bir fotoğraf çekme işleminden ziyade, hatalı ve mükerrer kayıtları önlemek için bir dizi doğrulama algoritması çalıştırır.

**Sınıf Yapısı ve Metotlar**

- `__init__(self)` - Başlatma ve Hazırlık:

Sistem açıldığında faces klasörünü kontrol eder, yoksa oluşturur.

FacialRecognition yardımcı sınıfını kullanarak, mevcut veritabanındaki tüm yüz verilerini (.npy dosyaları) hafızaya yükler. Bu işlem, yeni kaydedilecek kişinin daha önce kaydedilip kaydedilmediğini (Duplicate Check) kontrol etmek için gereklidir.

- `face_detection(self, frame)` - Yüz Analizi:

OpenCV'den gelen BGR formatındaki görüntüyü, face_recognition kütüphanesinin işleyebileceği RGB formatına çevirir.

Görüntüdeki yüzün 128 boyutlu matematiksel vektörünü (encoding) çıkarır.

- `face_save(self, encodings, name)` - Veri Saklama:

Yüz verisini .jpg resim dosyası olarak değil, işlenmiş .npy (NumPy Array) formatında saklar.

Avantajı: Sistem her açıldığında yüzleri tekrar tekrar analiz etmek zorunda kalmaz, doğrudan matematiksel veriyi okur. Bu da açılış hızını %90 artırır.

### Çalışma Algoritması
Kullanıcı `c` tuşuna bastığında sistem şu Karar Ağacını izler:

1. Görüntü Yakalama: Anlık kare geçici olarak diske kaydedilir.

2. Yüz Sayısı Kontrolü:

Eğer görüntüde yüz yoksa veya birden fazla yüz varsa işlem iptal edilir ve uyarı verilir.

Sadece tek bir yüz varsa bir sonraki adıma geçilir.

3. Aynı kayıt var mı Kayıt Kontrolü (Duplicate Check):

Algılanan yüz, hafızadaki kayıtlı yüzlerle karşılaştırılır.

Eğer benzerlik farkı 0.40'ın altındaysa (yani çok benziyorsa), sistem "Bu kişi zaten kayıtlı" uyarısı verir ve kaydı engeller.

4. Kayıt:

Tüm kontrollerden geçerse, yüz verisi İSİM_encoding.npy olarak kaydedilir.

5. Güvenlik:

try-finally bloğu sayesinde, program hata verse bile kamera kaynağı serbest bırakılarak sistemin takılı kalması önlenir.

## 2. Yüz Tanıma ve Loglama Modülü (FacialRecognition)
Bu modül (facial_recognition.py), sistemin çekirdeğidir. Kayıtlı yüz verilerini yükler, canlı kamera görüntüsünü analiz eder ve kimlik doğrulama işlemini gerçekleştirir.

**Sınıf Yapısı ve Metotlar**
- `__init__ ve load_encodings` - Veri Yükleme:

Sistem başlatıldığında faces klasöründeki tüm .npy dosyalarını tarar.

İsimleri ve yüz haritalarını (encodings) RAM'e yükler. Bu sayede tanıma işlemi milisaniyeler sürer.

Güvenlik: Eğer veritabanı boşsa sistemi başlatmaz ve kullanıcıyı uyarır.

- `face_comparison` - Karşılaştırma Motoru:

Canlı görüntüden alınan yüz ile veritabanındaki yüzler arasındaki Öklid Mesafesini (Euclidean Distance) ölçer.

Bu mesafe "Benzerlik Farkını" temsil eder. Sayı ne kadar küçükse, benzerlik o kadar fazladır.

- `add_record_log` - Giriş Kaydı (Logging):

Tanıma işlemi tamamlandığında (Başarılı veya Başarısız), sonucu access_log.csv dosyasına kaydeder.

Format: YIL.AY.GÜN SAAT:DAKİKA:SANİYE, İSİM

- `face_drawing` - Görselleştirme:

Tanınan kişinin yüzünü yeşil bir çerçeve içine alır ve ismini ekrana yazar.

### Çalışma Algoritması
Sistem Tanıma Modunda çalıştırıldığında şu adımları izler:

- Hazırlık: Kamera açılmadan önce kayıtlı kişi olup olmadığı kontrol edilir.

- Yüz Tespiti:

Kamera görüntüsü taranır. Eğer 0 yüz veya birden fazla yüz varsa ekrana uyarı basılır ve işlem yapılmaz.

- Kimlik Doğrulama:

Tespit edilen tek yüz, veritabanı ile karşılaştırılır.

- Eşik Değeri (Threshold): 0.50

Fark < 0.50 ise: "Giriş Başarılı" (İsim belirlenir).

Fark > 0.50 ise: "Erişim Reddedildi" (İsim "Bilinmiyor" olarak kalır).

- Loglama ve Çizim:

Sonuç CSV dosyasına işlenir.

Kullanıcının yüzüne çerçeve çizilir.

- Sonuç ve Kapanış 

Görsel Bildirim: Tanıma işlemi bittiğinde, yakalanan yüz karesi (üzerinde isim ve çerçeve çizili halde) ekrana sabitlenir.

Bekleme Modu: Güvenlik görevlisinin veya kullanıcının sonucu net görebilmesi için ekran bir tuşa basılana kadar dondurulur (cv2.waitKey(0)).

Sistemi Sonlandırma: Herhangi bir tuşa basıldığında işlem tamamlanmış kabul edilir, kamera kapatılır ve sistem güvenli bir şekilde sonlandırılır.


## 1. Yüz Kayıt Modülü (add_user.py)
```python
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
```
## 2. Yüz Tanıma ve Loglama Modülü (facial_recognition.py)
```python
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
```
