import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# Google Sheet bağlantısı
def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

# 6 ay kontrol fonksiyonu
def kontrol_6ay(satir):
    try:
        tarih_str = satir["Tarih"]
        tarih = datetime.strptime(tarih_str, "%d.%m.%Y")
        bugun = datetime.today()
        fark = relativedelta(bugun, tarih)

        if fark.years == 0 and fark.months == 6 and fark.days == 0:
            ad = satir.get("Ad Soyad", "Bilinmeyen")
            print(f" Hatırlatma: {ad} adlı kişinin son servisi 6 ay önceydi ({tarih_str})")

    except Exception as e:
        print("Hata:", e)

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    veriler = sheet.get_all_records()

    for satir in veriler:
        kontrol_6ay(satir)
