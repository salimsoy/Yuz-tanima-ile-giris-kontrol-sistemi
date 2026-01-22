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

1. Yüz Kayıt Modülü (SaveFace)
Bu modül (add_user.py), veritabanına yeni kullanıcı eklemek için kullanılır. Basit bir fotoğraf çekme işleminden ziyade, hatalı ve mükerrer kayıtları önlemek için bir dizi doğrulama algoritması çalıştırır.

**Sınıf Yapısı ve Metotlar**

- __init__(self) - Başlatma ve Hazırlık:

Sistem açıldığında faces klasörünü kontrol eder, yoksa oluşturur.

FacialRecognition yardımcı sınıfını kullanarak, mevcut veritabanındaki tüm yüz verilerini (.npy dosyaları) hafızaya yükler. Bu işlem, yeni kaydedilecek kişinin daha önce kaydedilip kaydedilmediğini (Duplicate Check) kontrol etmek için gereklidir.

- face_detection(self, frame) - Yüz Analizi:

OpenCV'den gelen BGR formatındaki görüntüyü, face_recognition kütüphanesinin işleyebileceği RGB formatına çevirir.

Görüntüdeki yüzün 128 boyutlu matematiksel vektörünü (encoding) çıkarır.

- face_save(self, encodings, name) - Veri Saklama:

Yüz verisini .jpg resim dosyası olarak değil, işlenmiş .npy (NumPy Array) formatında saklar.

Avantajı: Sistem her açıldığında yüzleri tekrar tekrar analiz etmek zorunda kalmaz, doğrudan matematiksel veriyi okur. Bu da açılış hızını %90 artırır.

## Çalışma Algoritması (Main Loop)
Kullanıcı c tuşuna bastığında sistem şu Karar Ağacını izler:

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


