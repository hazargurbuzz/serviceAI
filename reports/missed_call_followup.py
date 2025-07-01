import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime

def connect_to_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).worksheet("missed_calls")  # Sayfa adı: missed_calls

def takip_et():
    sheet = connect_to_sheet("service reservation")
    veriler = sheet.get_all_records()
    bugun = datetime.today().strftime("%d.%m.%Y")

    for row in veriler:
        try:
            if row["Durum"].lower() == "cevapsız" and row["Tarih"] == bugun:
                print(f" Takip: {row['Ad Soyad']} kişisine bugün {row['Saat']}'teki cevapsız çağrı için geri dönüş yapılmalı.")
        except Exception as e:
            print("Hata:", e)

if __name__ == "__main__":
    takip_et()
