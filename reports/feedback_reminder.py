import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import os

def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def kontrol_geribildirim(satir):
    try:
        tarih_str = satir["Tarih"]
        tarih = datetime.strptime(tarih_str, "%d.%m.%Y")
        bugun = datetime.today().date()
        if bugun - tarih.date() == timedelta(days=1):
            print(f" Geri Bildirim: {satir['Ad Soyad']} adlı kişi için dünkü servis sonrası geri bildirim isteyin ({tarih_str})")
    except Exception as e:
        print("Hata:", e)

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    veriler = sheet.get_all_records()

    for satir in veriler:
        kontrol_geribildirim(satir)
