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