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