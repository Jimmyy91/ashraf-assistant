from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

# Replace with your full calendar ID
CALENDAR_ID = '5b9bcd1d8140ae28585dad4649399f52ee4f6403c8211295d8970300c2afce83@group.calendar.google.com'
SERVICE_ACCOUNT_FILE = 'ashraf-assistant-3011889b5b2e.json'

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def create_event(summary, start_time_str, duration_minutes=60):
    service = get_calendar_service()

    start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
    end_time = start_time + timedelta(minutes=duration_minutes)

    timezone = 'Africa/Cairo'
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': timezone,
        },
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return event.get('htmlLink')
