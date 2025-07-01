from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Google Sheet'e bağlan
def connect_to_google_sheet(sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

# Ana işlem
if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    records = sheet.get_all_records()
    bugun = datetime.now().date()

    for r in records:
        try:
            r = {k.strip(): v for k, v in r.items()}  # Başlıklar için boşluk temizliği
            ad = r["Ad"]
            tarih = datetime.strptime(r["Tarih"], "%d.%m.%Y").date()
            saat = str(r["Saat"])  # float olsa bile string'e çevir

            if "." in saat:
                try:
                    h, m = saat.split(".")
                    saat = f"{h}:{m.zfill(2)}"
                except:
                    pass  # sorun olursa dokunma
            if tarih == bugun:
                print(f"🔔 Hatırlatma: {ad} adlı kişinin bugün ({tarih}) saat {saat}'te randevusu var.")
        except Exception as e:
            print("Hata:", e)
