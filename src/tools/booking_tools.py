"""
Booking Tools for Calendar Operations
Tools for checking and creating appointments
"""

from datetime import datetime
from langchain.tools import tool
from src.services.calendar import get_calendar
from src.services.database import get_database
from src.services.gmail import get_gmail


@tool
def check_my_bookings(patient_email: str) -> str:
    """
    Check all upcoming appointments for the patient.

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

        # Format appointments
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

            result += f"{i}. {appt['summary']}\n"
            result += f"   Time: {formatted_time}\n"
            if appt['description']:
                result += f"   Details: {appt['description']}\n"
            result += "\n"

        return result.strip()

    except Exception as e:
        return f"Error retrieving appointments: {str(e)}"


@tool
def get_available_doctors() -> str:
    """
    Get list of all available doctors.

    Returns:
        Formatted string with doctor details
    """
    try:
        db = get_database()
        doctors = db.get_available_doctors()

        if not doctors:
            return "No doctors are currently available."

        result = "Available doctors:\n\n"
        for i, doctor in enumerate(doctors, 1):
            result += f"{i}. {doctor['name']}\n"
            result += f"   Specialization: {doctor['specialization']}\n"
            result += f"   ID: {doctor['id']}\n\n"

        return result.strip()

    except Exception as e:
        return f"Error retrieving doctors: {str(e)}"


@tool
def get_available_services() -> str:
    """
    Get list of all dental services.

    Returns:
        Formatted string with service details
    """
    try:
        db = get_database()
        services = db.get_all_services()

        if not services:
            return "No services are currently available."

        result = "Available services:\n\n"
        for i, service in enumerate(services, 1):
            result += f"{i}. {service['name']}\n"
            result += f"   Description: {service['description']}\n"
            result += f"   Duration: {service['duration_minutes']} minutes\n"
            result += f"   Price: {service['price']} SAR\n"
            result += f"   ID: {service['id']}\n\n"

        return result.strip()

    except Exception as e:
        return f"Error retrieving services: {str(e)}"


@tool
def create_new_booking(
    patient_email: str,
    patient_name: str,
    doctor_id: str,
    service_id: str,
    appointment_datetime: str
) -> str:
    """
    Create a new appointment in Google Calendar.

    Args:
        patient_email: Patient's email address
        patient_name: Patient's name
        doctor_id: Doctor's ID from database
        service_id: Service ID from database
        appointment_datetime: Appointment date and time in ISO format (YYYY-MM-DD HH:MM)

    Returns:
        Success or error message
    """
    try:
        # Get doctor and service details from database
        db = get_database()

        # Get doctor info
        doctor = db.client.table("doctors").select("*").eq("id", doctor_id).execute()
        if not doctor.data:
            return f"Error: Doctor with ID {doctor_id} not found."
        doctor = doctor.data[0]

        # Get service info
        service = db.client.table("services").select("*").eq("id", service_id).execute()
        if not service.data:
            return f"Error: Service with ID {service_id} not found."
        service = service.data[0]

        # Parse datetime
        try:
            # Try parsing with different formats
            for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]:
                try:
                    start_time = datetime.strptime(appointment_datetime, fmt)
                    break
                except ValueError:
                    continue
            else:
                return f"Error: Invalid date format. Please use YYYY-MM-DD HH:MM (e.g., 2024-11-25 14:00)"
        except Exception as e:
            return f"Error parsing date: {str(e)}"

        # Get doctor's email for calendar
        doctor_email = doctor.get('email', f"doctor_{doctor_id}@clinic.com")

        # Create appointment in Google Calendar
        calendar = get_calendar()
        result = calendar.create_appointment(
            patient_email=patient_email,
            patient_name=patient_name,
            doctor_name=doctor['name'],
            doctor_email=doctor_email,
            service_name=service['name'],
            start_time=start_time,
            duration_minutes=service['duration_minutes']
        )

        # Check for errors
        if result.get('error') == 'conflict':
            return f"❌ {result['message']}\n\nPlease choose a different time slot."

        if result.get('error'):
            return f"❌ Failed to create appointment: {result['message']}"

        # Success
        formatted_time = start_time.strftime('%A, %B %d, %Y at %I:%M %p')
        return f"""✅ Appointment successfully booked!

Service: {service['name']}
Doctor: {doctor['name']}
Date & Time: {formatted_time}
Duration: {service['duration_minutes']} minutes
Price: {service['price']} SAR

IMPORTANT: You MUST now call send_booking_confirmation_email() with these exact parameters:
- patient_email: {patient_email}
- patient_name: {patient_name}
- service_name: {service['name']}
- doctor_name: {doctor['name']}
- appointment_datetime: {start_time.strftime('%Y-%m-%d %H:%M')}
- duration_minutes: {service['duration_minutes']}
- price: {service['price']}"""

    except Exception as e:
        return f"Error creating appointment: {str(e)}"


@tool
def send_booking_confirmation_email(
    patient_email: str,
    patient_name: str,
    service_name: str,
    doctor_name: str,
    appointment_datetime: str,
    duration_minutes: int,
    price: float
) -> str:
    """
    Send booking confirmation email to patient.
    Call this AFTER successfully creating a booking to notify the patient.

    Args:
        patient_email: Patient's email address
        patient_name: Patient's name
        service_name: Service name (e.g., "تنظيف الأسنان")
        doctor_name: Doctor's name (e.g., "Dr. Saad Al-Mutairi")
        appointment_datetime: Appointment datetime in ISO format (YYYY-MM-DD HH:MM)
        duration_minutes: Duration in minutes
        price: Service price in SAR

    Returns:
        Success or error message
    """
    print("\n" + "="*60)
    print("[TOOL DEBUG] send_booking_confirmation_email called")
    print(f"[TOOL DEBUG] patient_email: {patient_email}")
    print(f"[TOOL DEBUG] patient_name: {patient_name}")
    print(f"[TOOL DEBUG] service_name: {service_name}")
    print(f"[TOOL DEBUG] doctor_name: {doctor_name}")
    print(f"[TOOL DEBUG] appointment_datetime: {appointment_datetime}")
    print(f"[TOOL DEBUG] duration_minutes: {duration_minutes}")
    print(f"[TOOL DEBUG] price: {price}")
    print("="*60 + "\n")

    try:
        # Parse datetime
        dt = datetime.strptime(appointment_datetime, "%Y-%m-%d %H:%M")
        print(f"[TOOL DEBUG] Parsed datetime: {dt}")

        # Send email
        print(f"[TOOL DEBUG] Getting Gmail service...")
        gmail = get_gmail()

        print(f"[TOOL DEBUG] Calling gmail.send_booking_confirmation()...")
        result = gmail.send_booking_confirmation(
            patient_email=patient_email,
            patient_name=patient_name,
            service_name=service_name,
            doctor_name=doctor_name,
            appointment_datetime=dt,
            duration_minutes=duration_minutes,
            price=price
        )

        print(f"[TOOL DEBUG] Email result: {result}")

        if result['status'] == 'success':
            return f"✅ Confirmation email sent to {patient_email}"
        else:
            return f"⚠️ Booking successful but email failed: {result['message']}"

    except Exception as e:
        print(f"[TOOL DEBUG] ❌ Exception in send_booking_confirmation_email: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"⚠️ Booking successful but email failed: {str(e)}"


# Tool list for booking agent
booking_tools = [
    check_my_bookings,
    get_available_doctors,
    get_available_services,
    create_new_booking,
    send_booking_confirmation_email
]
