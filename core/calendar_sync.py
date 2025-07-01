import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

# Google Sheets bağlantısı
def connect_to_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

# Google Calendar bağlantısı
def connect_to_calendar():
    scopes = ['https://www.googleapis.com/auth/calendar']
    creds_path = os.path.join(os.path.dirname(__file__), "calendar_credentials.json")
    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
    service = build('calendar', 'v3', credentials=credentials)
    return service

# Randevu oluştur
def add_appointment(service, calendar_id, name, date_str, time_str):
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
        end_time = dt + timedelta(hours=1)

        event = {
            'summary': f'Servis Randevusu - {name}',
            'start': {'dateTime': dt.isoformat(), 'timeZone': 'Europe/Istanbul'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Europe/Istanbul'},
        }

        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f" Randevu eklendi: {created_event.get('htmlLink')}")
    except Exception as e:
        print(" Hata:", e)

if __name__ == "__main__":
    sheet = connect_to_google_sheet("service reservation")
    rows = sheet.get_all_records()

    calendar_service = connect_to_calendar()

    # Takvim ID'sini elle belirleyebilirsin veya `primary` kullan
    calendar_id = 'primary'

    for row in rows:
        name = row["Ad Soyad"]
        date = row["Tarih"]
        time = row["Saat"]
        add_appointment(calendar_service, calendar_id, name, date, time)
