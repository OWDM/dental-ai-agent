"""
Google Calendar Service
Handles appointment scheduling and retrieval
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.config.settings import settings


class CalendarService:
    """Google Calendar API service"""

    def __init__(self):
        """Initialize Google Calendar client"""
        # Scopes required for calendar operations
        SCOPES = ['https://www.googleapis.com/auth/calendar']

        # Load credentials from service account file
        if not settings.google_calendar_credentials_file:
            raise ValueError("GOOGLE_CALENDAR_CREDENTIALS_FILE not set in .env")

        try:
            credentials = service_account.Credentials.from_service_account_file(
                settings.google_calendar_credentials_file,
                scopes=SCOPES
            )
            self.service = build('calendar', 'v3', credentials=credentials)
            self.calendar_id = settings.google_calendar_id or 'primary'
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Calendar: {str(e)}")

    def get_patient_appointments(self, patient_email: str) -> List[Dict]:
        """
        Get all appointments for a patient by email

        Args:
            patient_email: Patient's email address

        Returns:
            List of appointment dictionaries with details
        """
        try:
            # Get current time
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime',
                q=patient_email  # Search for events containing patient email
            ).execute()

            events = events_result.get('items', [])

            # Format appointments
            appointments = []
            for event in events:
                # Extract appointment details
                start = event.get('start', {})
                start_time = start.get('dateTime', start.get('date'))

                appointments.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'Dental Appointment'),
                    'description': event.get('description', ''),
                    'start_time': start_time,
                    'end_time': event.get('end', {}).get('dateTime', ''),
                })

            return appointments

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def create_appointment(
        self,
        patient_email: str,
        patient_name: str,
        doctor_name: str,
        doctor_email: str,
        service_name: str,
        start_time: datetime,
        duration_minutes: int = 60
    ) -> Optional[Dict]:
        """
        Create a new appointment in Google Calendar

        Args:
            patient_email: Patient's email
            patient_name: Patient's name
            doctor_name: Doctor's name
            doctor_email: Doctor's email (to check for conflicts)
            service_name: Service/procedure name
            start_time: Appointment start time
            duration_minutes: Duration in minutes (default: 60)

        Returns:
            Created event dictionary or None if failed/conflict exists
        """
        try:
            # Check for doctor conflicts (no duplicate bookings for same doctor)
            end_time = start_time + timedelta(minutes=duration_minutes)

            # Check if doctor already has an appointment at this time
            doctor_conflict = self._check_doctor_conflict(doctor_name, doctor_email, start_time, end_time)
            if doctor_conflict:
                return {
                    'error': 'conflict',
                    'message': f'Dr. {doctor_name} already has an appointment at this time'
                }

            # Check if patient already has an appointment at this time
            patient_conflict = self._check_patient_conflict(patient_email, start_time, end_time)
            if patient_conflict:
                return {
                    'error': 'conflict',
                    'message': f'You already have an appointment at this time'
                }

            # Create event
            event = {
                'summary': f'{service_name} - {patient_name}',
                'description': f'Service: {service_name}\nPatient: {patient_name} ({patient_email})\nDoctor: {doctor_name} ({doctor_email})',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Riyadh',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Riyadh',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 60},  # 1 hour before
                    ],
                },
            }

            # Insert event into calendar (without sending email notifications)
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()

            return {
                'id': created_event['id'],
                'summary': created_event.get('summary'),
                'start_time': created_event.get('start', {}).get('dateTime'),
                'end_time': created_event.get('end', {}).get('dateTime'),
                'link': created_event.get('htmlLink'),
                'status': 'success'
            }

        except HttpError as error:
            print(f"An error occurred: {error}")
            return {
                'error': 'api_error',
                'message': f'Failed to create appointment: {str(error)}'
            }

    def _check_doctor_conflict(
        self,
        doctor_name: str,
        doctor_email: str,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Check if doctor has a conflicting appointment

        Args:
            doctor_name: Doctor's name (to check in event summary)
            doctor_email: Doctor's email (to check in description)
            start_time: Proposed appointment start time
            end_time: Proposed appointment end time

        Returns:
            True if conflict exists, False otherwise
        """
        try:
            # Get all events on the same day
            # Use a wider time range to ensure we catch all appointments
            day_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = start_time.replace(hour=23, minute=59, second=59, microsecond=999999)

            print(f"\n[DEBUG] Checking conflicts for doctor: {doctor_email}")
            print(f"[DEBUG] New appointment: {start_time} to {end_time}")
            print(f"[DEBUG] Searching day: {day_start} to {day_end}")

            # Search for events on this day
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=day_start.isoformat() + 'Z',
                timeMax=day_end.isoformat() + 'Z',
                singleEvents=True
            ).execute()

            events = events_result.get('items', [])
            print(f"[DEBUG] Found {len(events)} events on this day")

            # Check each event for conflicts
            for i, event in enumerate(events):
                description = event.get('description', '')
                summary = event.get('summary', '')
                print(f"\n[DEBUG] Event {i+1}: {summary}")
                print(f"[DEBUG] Description snippet: {description[:100]}...")

                # Check if this event is for the same doctor (check both email in description and name in summary)
                if doctor_email not in description and doctor_name not in summary:
                    print(f"[DEBUG] Doctor not found in description or summary - skipping")
                    continue

                print(f"[DEBUG] Doctor match found!")

                # Get event times
                event_start_str = event.get('start', {}).get('dateTime')
                event_end_str = event.get('end', {}).get('dateTime')

                if not event_start_str or not event_end_str:
                    print(f"[DEBUG] Missing times - skipping")
                    continue

                # Parse event times (remove timezone info for comparison)
                event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))

                # Make naive datetimes for comparison
                event_start = event_start.replace(tzinfo=None)
                event_end = event_end.replace(tzinfo=None)

                print(f"[DEBUG] Existing: {event_start} to {event_end}")
                print(f"[DEBUG] Checking overlap: {start_time} < {event_end} AND {end_time} > {event_start}")

                # Check for time overlap
                # Conflict if: new_start < existing_end AND new_end > existing_start
                if start_time < event_end and end_time > event_start:
                    print(f"[DEBUG] ⚠️ CONFLICT DETECTED!")
                    return True  # Conflict found

            print(f"[DEBUG] ✅ No conflicts found")
            return False  # No conflict

        except HttpError as error:
            print(f"Error checking conflicts: {error}")
            return False  # Assume no conflict if check fails
        except Exception as e:
            print(f"Error parsing times: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _check_patient_conflict(
        self,
        patient_email: str,
        start_time: datetime,
        end_time: datetime,
        exclude_event_id: str = None
    ) -> bool:
        """
        Check if patient already has an appointment at this time

        Args:
            patient_email: Patient's email
            start_time: Proposed appointment start time
            end_time: Proposed appointment end time
            exclude_event_id: Event ID to exclude from conflict check (for rescheduling)

        Returns:
            True if conflict exists, False otherwise
        """
        try:
            # Get all events on the same day
            day_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = start_time.replace(hour=23, minute=59, second=59, microsecond=999999)

            print(f"\n[DEBUG] Checking patient conflicts for: {patient_email}")
            print(f"[DEBUG] New appointment: {start_time} to {end_time}")

            # Search for events on this day
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=day_start.isoformat() + 'Z',
                timeMax=day_end.isoformat() + 'Z',
                singleEvents=True
            ).execute()

            events = events_result.get('items', [])
            print(f"[DEBUG] Found {len(events)} events on this day")

            # Check each event for conflicts
            for i, event in enumerate(events):
                # Skip the event being rescheduled
                if exclude_event_id and event['id'] == exclude_event_id:
                    continue

                description = event.get('description', '')

                # Check if this event is for the same patient
                if patient_email not in description:
                    continue

                print(f"\n[DEBUG] Patient match found in event: {event.get('summary')}")

                # Get event times
                event_start_str = event.get('start', {}).get('dateTime')
                event_end_str = event.get('end', {}).get('dateTime')

                if not event_start_str or not event_end_str:
                    continue

                # Parse event times
                event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))

                # Make naive datetimes for comparison
                event_start = event_start.replace(tzinfo=None)
                event_end = event_end.replace(tzinfo=None)

                print(f"[DEBUG] Existing appointment: {event_start} to {event_end}")
                print(f"[DEBUG] Checking overlap: {start_time} < {event_end} AND {end_time} > {event_start}")

                # Check for time overlap
                if start_time < event_end and end_time > event_start:
                    print(f"[DEBUG] ⚠️ PATIENT CONFLICT DETECTED!")
                    return True  # Conflict found

            print(f"[DEBUG] ✅ No patient conflicts found")
            return False  # No conflict

        except Exception as e:
            print(f"Error checking patient conflicts: {e}")
            import traceback
            traceback.print_exc()
            return False

    def find_appointment_by_criteria(
        self,
        patient_email: str,
        doctor_name: str = None,
        service_name: str = None,
        date_str: str = None
    ) -> Optional[Dict]:
        """
        Find a specific appointment based on natural language criteria

        Args:
            patient_email: Patient's email
            doctor_name: Doctor's name (optional)
            service_name: Service name (optional)
            date_str: Date string in various formats (optional)

        Returns:
            Appointment dict if found, None otherwise
        """
        try:
            appointments = self.get_patient_appointments(patient_email)

            if not appointments:
                return None

            # Filter by criteria
            matches = []
            for appt in appointments:
                match = True

                # Check doctor name
                if doctor_name and doctor_name.lower() not in appt['description'].lower():
                    match = False

                # Check service name
                if service_name and service_name.lower() not in appt['summary'].lower():
                    match = False

                # Check date (flexible matching)
                if date_str:
                    appt_date = datetime.fromisoformat(appt['start_time'].replace('Z', '+00:00'))
                    appt_date_str = appt_date.strftime('%Y-%m-%d')

                    # Try to match the date in various formats
                    if date_str.lower() not in appt_date_str and \
                       date_str.lower() not in appt_date.strftime('%A').lower() and \
                       date_str.lower() not in appt_date.strftime('%B %d').lower():
                        match = False

                if match:
                    matches.append(appt)

            # If exactly one match, return it
            if len(matches) == 1:
                return matches[0]

            # If multiple matches, return the first one (could be improved with better disambiguation)
            if len(matches) > 1:
                return matches[0]

            return None

        except Exception as e:
            print(f"Error finding appointment: {e}")
            return None

    def update_appointment(
        self,
        event_id: str,
        new_start_time: datetime = None,
        new_doctor_name: str = None,
        new_doctor_email: str = None,
        new_service_name: str = None,
        new_duration_minutes: int = None
    ) -> Optional[Dict]:
        """
        Update an existing appointment

        Args:
            event_id: Google Calendar event ID
            new_start_time: New appointment start time (optional)
            new_doctor_name: New doctor name (optional)
            new_doctor_email: New doctor email (optional)
            new_service_name: New service name (optional)
            new_duration_minutes: New duration (optional)

        Returns:
            Updated event dict or error dict
        """
        try:
            # Get the existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            # Extract current values
            current_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00')).replace(tzinfo=None)
            current_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00')).replace(tzinfo=None)
            current_duration = int((current_end - current_start).total_seconds() / 60)
            description = event.get('description', '')

            # Parse current info from description
            patient_email = ''
            patient_name = ''
            current_doctor_email = ''
            current_doctor_name = ''
            for line in description.split('\n'):
                if 'Patient:' in line:
                    parts = line.split('(')
                    if len(parts) > 1:
                        patient_email = parts[1].replace(')', '').strip()
                        patient_name = parts[0].replace('Patient:', '').strip()
                if 'Doctor:' in line and '(' in line:
                    # Extract both name and email from "Doctor: Name (email)"
                    parts = line.split('(')
                    current_doctor_name = parts[0].replace('Doctor:', '').strip()
                    current_doctor_email = parts[1].replace(')', '').strip()

            # Determine new values
            start_time = new_start_time if new_start_time else current_start
            duration = new_duration_minutes if new_duration_minutes else current_duration
            end_time = start_time + timedelta(minutes=duration)
            doctor_name = new_doctor_name if new_doctor_name else current_doctor_name
            doctor_email = new_doctor_email if new_doctor_email else current_doctor_email
            service_name = new_service_name if new_service_name else event.get('summary', '').split('-')[0].strip()

            # Check for conflicts if time is changing
            if new_start_time:
                # Check doctor conflict
                if doctor_email:
                    doctor_conflict = self._check_doctor_conflict(doctor_name, doctor_email, start_time, end_time)
                    if doctor_conflict:
                        return {
                            'error': 'conflict',
                            'message': f'Dr. {doctor_name} already has an appointment at this time'
                        }

                # Check patient conflict (exclude current event)
                patient_conflict = self._check_patient_conflict(patient_email, start_time, end_time, exclude_event_id=event_id)
                if patient_conflict:
                    return {
                        'error': 'conflict',
                        'message': f'You already have another appointment at this time'
                    }

            # Update event
            event['summary'] = f'{service_name} - {patient_name}'
            event['description'] = f'Service: {service_name}\nPatient: {patient_name} ({patient_email})\nDoctor: {doctor_name} ({doctor_email})'
            event['start'] = {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Riyadh',
            }
            event['end'] = {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Riyadh',
            }

            # Update in calendar
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            return {
                'id': updated_event['id'],
                'summary': updated_event.get('summary'),
                'start_time': updated_event.get('start', {}).get('dateTime'),
                'end_time': updated_event.get('end', {}).get('dateTime'),
                'status': 'success'
            }

        except HttpError as error:
            print(f"An error occurred: {error}")
            return {
                'error': 'api_error',
                'message': f'Failed to update appointment: {str(error)}'
            }

    def delete_appointment(self, event_id: str) -> Dict:
        """
        Delete an appointment from Google Calendar

        Args:
            event_id: Google Calendar event ID

        Returns:
            Success or error dict
        """
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            return {
                'status': 'success',
                'message': 'Appointment cancelled successfully'
            }

        except HttpError as error:
            print(f"An error occurred: {error}")
            return {
                'error': 'api_error',
                'message': f'Failed to cancel appointment: {str(error)}'
            }


# Singleton instance
_calendar_instance = None


def get_calendar() -> CalendarService:
    """Get or create calendar service instance"""
    global _calendar_instance
    if _calendar_instance is None:
        _calendar_instance = CalendarService()
    return _calendar_instance
