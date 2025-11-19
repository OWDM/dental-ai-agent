"""
Management Tools for Appointment Operations
Tools for viewing, cancelling, and rescheduling appointments
"""

from datetime import datetime
from langchain.tools import tool
from src.services.calendar import get_calendar


@tool
def view_my_appointments(patient_email: str) -> str:
    """
    View all upcoming appointments for the patient.
    Shows appointment details in a user-friendly format without IDs.

    Args:
        patient_email: Patient's email address

    Returns:
        Formatted string with appointment details
    """
    try:
        calendar = get_calendar()
        appointments = calendar.get_patient_appointments(patient_email)

        if not appointments:
            return "You don't have any upcoming appointments."

        # Format appointments in a friendly way
        result = f"You have {len(appointments)} upcoming appointment(s):\n\n"
        for i, appt in enumerate(appointments, 1):
            # Parse datetime
            start_time = appt['start_time']
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
                except:
                    formatted_time = start_time

            # Parse description to get doctor and service info
            description = appt.get('description', '')
            summary = appt.get('summary', '')

            # Extract service name (before the dash in summary)
            service = summary.split(' - ')[0] if ' - ' in summary else summary

            # Extract doctor name from description
            doctor = ""
            for line in description.split('\n'):
                if 'Doctor:' in line:
                    doctor = line.replace('Doctor:', '').split('(')[0].strip()
                    break

            result += f"{i}. {service}\n"
            result += f"   Doctor: {doctor}\n"
            result += f"   Time: {formatted_time}\n\n"

        return result.strip()

    except Exception as e:
        return f"Error retrieving appointments: {str(e)}"


@tool
def cancel_appointment(
    patient_email: str,
    doctor_name: str = None,
    service_name: str = None,
    date_str: str = None
) -> str:
    """
    Cancel an appointment based on natural criteria (doctor name, service, or date).

    Args:
        patient_email: Patient's email address
        doctor_name: Doctor's name (e.g., "Dr. Saad", "Saad", "Sarah") - optional
        service_name: Service name (e.g., "teeth cleaning", "filling") - optional
        date_str: Date or day reference (e.g., "Wednesday", "Nov 25", "2024-11-25") - optional

    Returns:
        Success or error message
    """
    try:
        calendar = get_calendar()

        # Find the appointment using the criteria
        appointment = calendar.find_appointment_by_criteria(
            patient_email=patient_email,
            doctor_name=doctor_name,
            service_name=service_name,
            date_str=date_str
        )

        if not appointment:
            criteria_parts = []
            if doctor_name:
                criteria_parts.append(f"with {doctor_name}")
            if service_name:
                criteria_parts.append(f"for {service_name}")
            if date_str:
                criteria_parts.append(f"on {date_str}")

            criteria_str = " ".join(criteria_parts) if criteria_parts else ""
            return f"I couldn't find an appointment {criteria_str}. Please check your appointments and try again."

        # Get appointment details for confirmation message
        summary = appointment.get('summary', '')
        service = summary.split(' - ')[0] if ' - ' in summary else 'appointment'

        description = appointment.get('description', '')
        doctor = ""
        for line in description.split('\n'):
            if 'Doctor:' in line:
                doctor = line.replace('Doctor:', '').split('(')[0].strip()
                break

        start_time = appointment['start_time']
        try:
            dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
        except:
            formatted_time = start_time

        # Delete the appointment
        result = calendar.delete_appointment(appointment['id'])

        if result.get('status') == 'success':
            return f"""✅ Appointment cancelled successfully!

Cancelled appointment:
- Service: {service}
- Doctor: {doctor}
- Time: {formatted_time}

If you need to book a new appointment, just let me know!"""
        else:
            return f"❌ Failed to cancel appointment: {result.get('message', 'Unknown error')}"

    except Exception as e:
        return f"Error cancelling appointment: {str(e)}"


@tool
def reschedule_appointment(
    patient_email: str,
    new_datetime: str,
    doctor_name: str = None,
    service_name: str = None,
    current_date_str: str = None
) -> str:
    """
    Reschedule an appointment to a new date/time.
    First identifies the appointment using the criteria, then reschedules it.

    Args:
        patient_email: Patient's email address
        new_datetime: New date and time. Can be:
            - Full datetime: "YYYY-MM-DD HH:MM" (e.g., "2025-11-25 14:00")
            - Time only: "HH:MM" (e.g., "15:00") - keeps same date
            - Use 24-hour format for time
        doctor_name: Current doctor's name to identify the appointment - optional
        service_name: Service name to identify the appointment - optional
        current_date_str: Current date to identify the appointment - optional

    Returns:
        Success or error message
    """
    try:
        calendar = get_calendar()

        # Find the appointment using the criteria
        appointment = calendar.find_appointment_by_criteria(
            patient_email=patient_email,
            doctor_name=doctor_name,
            service_name=service_name,
            date_str=current_date_str
        )

        if not appointment:
            criteria_parts = []
            if doctor_name:
                criteria_parts.append(f"with {doctor_name}")
            if service_name:
                criteria_parts.append(f"for {service_name}")
            if current_date_str:
                criteria_parts.append(f"on {current_date_str}")

            criteria_str = " ".join(criteria_parts) if criteria_parts else ""
            return f"I couldn't find the appointment {criteria_str}. Please check your appointments and try again."

        # Get current appointment datetime
        old_start_time = appointment['start_time']
        try:
            old_dt = datetime.fromisoformat(old_start_time.replace('Z', '+00:00')).replace(tzinfo=None)
            old_formatted_time = old_dt.strftime('%A, %B %d, %Y at %I:%M %p')
        except:
            old_formatted_time = old_start_time
            old_dt = None

        # Parse new datetime - support both full datetime and time-only
        new_start_time = None
        try:
            # Try time-only format first (HH:MM or HH:MM:SS)
            for time_fmt in ["%H:%M", "%H:%M:%S"]:
                try:
                    time_obj = datetime.strptime(new_datetime.strip(), time_fmt)
                    # Preserve the original date, only change the time
                    if old_dt:
                        new_start_time = old_dt.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
                        break
                except ValueError:
                    continue

            # If time-only parsing failed, try full datetime formats
            if not new_start_time:
                for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        new_start_time = datetime.strptime(new_datetime, fmt)
                        break
                    except ValueError:
                        continue

            if not new_start_time:
                return f"Error: Invalid date/time format. Use either 'HH:MM' for time only (e.g., '15:00') or 'YYYY-MM-DD HH:MM' for full date/time (e.g., '2025-11-25 15:00')"

        except Exception as e:
            return f"Error parsing date: {str(e)}"

        # Get current appointment details for message
        summary = appointment.get('summary', '')
        service = summary.split(' - ')[0] if ' - ' in summary else 'appointment'

        description = appointment.get('description', '')
        doctor = ""
        for line in description.split('\n'):
            if 'Doctor:' in line:
                doctor = line.replace('Doctor:', '').split('(')[0].strip()
                break

        # Update the appointment
        result = calendar.update_appointment(
            event_id=appointment['id'],
            new_start_time=new_start_time
        )

        # Check for errors
        if result.get('error') == 'conflict':
            return f"❌ {result['message']}\n\nPlease choose a different time slot."

        if result.get('error'):
            return f"❌ Failed to reschedule appointment: {result['message']}"

        # Success
        new_formatted_time = new_start_time.strftime('%A, %B %d, %Y at %I:%M %p')
        return f"""✅ Appointment rescheduled successfully!

Service: {service}
Doctor: {doctor}

Previous time: {old_formatted_time}
New time: {new_formatted_time}

See you at the new time!"""

    except Exception as e:
        return f"Error rescheduling appointment: {str(e)}"


# Tool list for management agent
management_tools = [
    view_my_appointments,
    cancel_appointment,
    reschedule_appointment
]