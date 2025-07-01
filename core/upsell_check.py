import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from time import sleep
import os

# Google Sheets bağlantısı
def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

# UPSell kontrol fonksiyonu
def upsell_on_service_history(row):
    try:
        onceki = (row.get("Önceki Servis") or "").lower()
        son = (row.get("Son Servis") or "").lower()
        tarih_str = row.get("Tarih", "")
        if not tarih_str:
            return

        tarih = datetime.strptime(tarih_str, "%d.%m.%Y")
        bugun = datetime.today()
        fark = (bugun - tarih).days

        öneriler = []

        if ("lastik" in onceki or "lastik" in son) and fark > 180:
            öneriler.append(" Lastik rotasyonu veya yeni lastik kontrolü önerilir.")
        if ("yağ" in onceki or "yağ" in son) and fark > 180:
            öneriler.append(" Motor yağı değişimi zamanı gelmiş olabilir.")
        if ("akü" in onceki or "akü" in son) and fark > 180:
            öneriler.append(" Akü voltaj testi yapılması önerilir.")
        if ("balata" in onceki or "balata" in son or "fren" in onceki or "fren" in son) and fark > 180:
            öneriler.append(" Fren balataları tekrar kontrol edilmeli.")

        if öneriler:
            print(f"\n Upsell Fırsatı - {row.get('Ad Soyad', 'Bilinmiyor')} ({tarih_str}):")
            for o in öneriler:
                print(f" → {o}")
    except Exception as e:
        print("Hata:", e)

# Sürekli kontrol fonksiyonu (15 dakikada bir)
def run_upsell_checker():
    while True:
        print("\n Yeni kontrol başlatılıyor...")
        sheet = connect_to_google_sheet("service reservation")
        veriler = sheet.get_all_records()
        for satir in veriler:
            upsell_on_service_history(satir)
        print("\n Kontrol tamamlandı. 15 dakika sonra yeniden çalışacak...")
        sleep(900)  # 900 saniye = 15 dakika

if __name__ == "__main__":
    run_upsell_checker()
