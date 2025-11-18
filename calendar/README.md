# Google Calendar API Integration

Quick guide for integrating with Google Calendar for appointment booking.

## Setup

**Environment Variables (.env):**
```env
GOOGLE_CALENDAR_CREDENTIALS_FILE=dental-clinic-ai-demo-a7d5e03f4d6d.json
GOOGLE_CALENDAR_ID=7ba6bd8051512d0690be3d76def5ea4e23b3e862be458137d1fd8744e2e62bae@group.calendar.google.com
```

**Dependencies:**
```bash
google-auth==2.37.0
google-auth-oauthlib==1.2.1
google-auth-httplib2==0.2.0
google-api-python-client==2.156.0
```

---

## Basic Usage

### Connect to Calendar

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

credentials = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE"),
    scopes=SCOPES
)

service = build('calendar', 'v3', credentials=credentials)
calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
```

### Create Appointment

```python
from datetime import datetime, timedelta

start_time = datetime.now() + timedelta(days=1)
start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)
end_time = start_time + timedelta(minutes=30)

event = {
    'summary': 'Patient Name - Service Name',
    'description': 'Patient: أحمد العتيبي\nPhone: +966-50-123-4567\nDoctor: د. سعد',
    'start': {
        'dateTime': start_time.isoformat(),
        'timeZone': 'Asia/Riyadh',
    },
    'end': {
        'dateTime': end_time.isoformat(),
        'timeZone': 'Asia/Riyadh',
    },
    'location': 'Dental Clinic - عيادة الأسنان',
}

created = service.events().insert(calendarId=calendar_id, body=event).execute()
print(f"Created: {created['htmlLink']}")
```

### List Appointments

```python
from datetime import datetime

now = datetime.now().isoformat() + 'Z'

events = service.events().list(
    calendarId=calendar_id,
    timeMin=now,
    maxResults=10,
    singleEvents=True,
    orderBy='startTime'
).execute()

for event in events.get('items', []):
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(f"{event['summary']} - {start}")
```

### Update Appointment

```python
event_id = "existing_event_id"

event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
event['summary'] = 'Updated Appointment Title'

updated = service.events().update(
    calendarId=calendar_id,
    eventId=event_id,
    body=event
).execute()
```

### Cancel Appointment

```python
service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
```

---

## Important Notes

- **Timezone:** Always use `Asia/Riyadh`
- **No Email Invites:** Service accounts can't send attendee invites (put contact info in description instead)
- **Event Colors:** Use `colorId` (1-11) to categorize appointments
- **Credentials:** JSON file is gitignored for security

---

## Calendar Details

- **Name:** Dental Clinic Appointments
- **Timezone:** Asia/Riyadh (GMT+3)
- **Access:** Shared with service account (Make changes to events)