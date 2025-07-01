from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

def connect_to_calendar():
    creds_path = os.path.join(os.path.dirname(__file__), "calendar_credentials.json")
    scopes = ['https://www.googleapis.com/auth/calendar']

    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)

    service = build('calendar', 'v3', credentials=credentials)
    return service

if __name__ == "__main__":
    service = connect_to_calendar()
    calendars = service.calendarList().list().execute()

    for cal in calendars['items']:
        print(f" Takvim: {cal['summary']} - ID: {cal['id']}")
