from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

# Path to your downloaded service account key
SERVICE_ACCOUNT_FILE = 'ashraf-assistant-3011889b5b2e.json'

# Calendar ID you provided
CALENDAR_ID = '5b9bcd1d8140ae28585dad4649399f52ee4f6403c8211295d8970300c2afce83@group.calendar.google.com'

# Required access scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the calendar service
service = build('calendar', 'v3', credentials=credentials)

# Create an event
def create_event(summary, start_time_str, duration_minutes=60):
    start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Africa/Cairo',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Africa/Cairo',
        },
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print("✅ Event created:")
    print(event.get('htmlLink'))

# Example usage
create_event("Ashraf's Smart Calendar Test", "2025-04-01 10:40", 45)
