"""
Gmail Service
Handles sending email notifications via Gmail SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from src.config.settings import settings


class GmailService:
    """Gmail SMTP service for sending emails"""

    def __init__(self):
        """Initialize Gmail SMTP client"""
        if not settings.gmail_address or not settings.gmail_app_password:
            raise ValueError("Gmail credentials not set in .env file")

        self.gmail_address = settings.gmail_address
        self.gmail_password = settings.gmail_app_password
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587

    def send_booking_confirmation(
        self,
        patient_email: str,
        patient_name: str,
        service_name: str,
        doctor_name: str,
        appointment_datetime: datetime,
        duration_minutes: int,
        price: float
    ) -> dict:
        """
        Send booking confirmation email to patient

        Args:
            patient_email: Patient's email address
            patient_name: Patient's name
            service_name: Service name
            doctor_name: Doctor's name
            appointment_datetime: Appointment date and time
            duration_minutes: Duration in minutes
            price: Service price in SAR

        Returns:
            Success or error dict
        """
        print("\n" + "="*60)
        print("[EMAIL DEBUG] Starting send_booking_confirmation")
        print(f"[EMAIL DEBUG] To: {patient_email}")
        print(f"[EMAIL DEBUG] Patient: {patient_name}")
        print(f"[EMAIL DEBUG] Service: {service_name}")
        print(f"[EMAIL DEBUG] Doctor: {doctor_name}")
        print(f"[EMAIL DEBUG] DateTime: {appointment_datetime}")
        print("="*60 + "\n")

        try:
            # Format datetime
            formatted_date = appointment_datetime.strftime('%A, %B %d, %Y')
            formatted_time = appointment_datetime.strftime('%I:%M %p')

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.gmail_address
            msg['To'] = patient_email
            msg['Subject'] = f'Appointment Confirmation - {service_name}'

            # Plain text version (Arabic and English)
            text_body = f"""
مرحباً {patient_name}،

تم تأكيد موعدك بنجاح!

الخدمة: {service_name}
الطبيب: {doctor_name}
التاريخ: {formatted_date}
الوقت: {formatted_time}
المدة: {duration_minutes} دقيقة
السعر: {price} ريال سعودي

---

Hello {patient_name},

Your appointment has been confirmed successfully!

Service: {service_name}
Doctor: {doctor_name}
Date: {formatted_date}
Time: {formatted_time}
Duration: {duration_minutes} minutes
Price: {price} SAR

If you need to reschedule or cancel, please contact us.

---
Riyadh Dental Care Clinic
عيادة الرياض لطب الأسنان
            """

            # HTML version
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">

                  <h2 style="color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px;">
                    ✅ Appointment Confirmed / تم تأكيد الموعد
                  </h2>

                  <p style="font-size: 16px; color: #333;">
                    <strong>مرحباً {patient_name} / Hello {patient_name},</strong>
                  </p>

                  <p style="color: #666;">
                    تم تأكيد موعدك بنجاح! / Your appointment has been confirmed successfully!
                  </p>

                  <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">الخدمة / Service:</td>
                        <td style="padding: 8px 0; color: #333;">{service_name}</td>
                      </tr>
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">الطبيب / Doctor:</td>
                        <td style="padding: 8px 0; color: #333;">{doctor_name}</td>
                      </tr>
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">التاريخ / Date:</td>
                        <td style="padding: 8px 0; color: #333;">{formatted_date}</td>
                      </tr>
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">الوقت / Time:</td>
                        <td style="padding: 8px 0; color: #333;">{formatted_time}</td>
                      </tr>
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">المدة / Duration:</td>
                        <td style="padding: 8px 0; color: #333;">{duration_minutes} دقيقة / minutes</td>
                      </tr>
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">السعر / Price:</td>
                        <td style="padding: 8px 0; color: #333; font-size: 18px; font-weight: bold; color: #2563eb;">{price} ريال سعودي / SAR</td>
                      </tr>
                    </table>
                  </div>

                  <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    إذا كنت بحاجة لإعادة الجدولة أو الإلغاء، يرجى التواصل معنا.<br>
                    If you need to reschedule or cancel, please contact us.
                  </p>

                  <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">

                  <p style="color: #999; font-size: 12px; text-align: center;">
                    <strong>Riyadh Dental Care Clinic</strong><br>
                    <strong>عيادة الرياض لطب الأسنان</strong>
                  </p>
                </div>
              </body>
            </html>
            """

            # Attach both versions
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            print(f"[EMAIL DEBUG] Attempting to send email via SMTP...")
            self._send_email(msg)
            print(f"[EMAIL DEBUG] ✅ Email sent successfully to {patient_email}")

            return {
                'status': 'success',
                'message': f'Confirmation email sent to {patient_email}'
            }

        except Exception as e:
            print(f"[EMAIL DEBUG] ❌ Failed to send email: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'Failed to send email: {str(e)}'
            }

    def send_cancellation_confirmation(
        self,
        patient_email: str,
        patient_name: str,
        service_name: str,
        doctor_name: str,
        appointment_datetime: datetime
    ) -> dict:
        """
        Send cancellation confirmation email to patient

        Args:
            patient_email: Patient's email address
            patient_name: Patient's name
            service_name: Service name
            doctor_name: Doctor's name
            appointment_datetime: Original appointment date and time

        Returns:
            Success or error dict
        """
        print("\n" + "="*60)
        print("[EMAIL DEBUG] Starting send_cancellation_confirmation")
        print(f"[EMAIL DEBUG] To: {patient_email}")
        print(f"[EMAIL DEBUG] Patient: {patient_name}")
        print(f"[EMAIL DEBUG] Service: {service_name}")
        print("="*60 + "\n")

        try:
            # Format datetime
            formatted_date = appointment_datetime.strftime('%A, %B %d, %Y')
            formatted_time = appointment_datetime.strftime('%I:%M %p')

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.gmail_address
            msg['To'] = patient_email
            msg['Subject'] = f'Appointment Cancelled - {service_name}'

            # Plain text version
            text_body = f"""
مرحباً {patient_name},

تم إلغاء موعدك بنجاح.

الخدمة: {service_name}
الطبيب: {doctor_name}
التاريخ: {formatted_date}
الوقت: {formatted_time}

---

Hello {patient_name},

Your appointment has been cancelled successfully.

Service: {service_name}
Doctor: {doctor_name}
Date: {formatted_date}
Time: {formatted_time}

If you need to book a new appointment, please contact us.

---
Riyadh Dental Care Clinic
عيادة الرياض لطب الأسنان
            """

            # HTML version
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">

                  <h2 style="color: #dc2626; border-bottom: 3px solid #dc2626; padding-bottom: 10px;">
                    🗑️ Appointment Cancelled / تم إلغاء الموعد
                  </h2>

                  <p style="font-size: 16px; color: #333;">
                    <strong>مرحباً {patient_name} / Hello {patient_name},</strong>
                  </p>

                  <p style="color: #666;">
                    تم إلغاء موعدك بنجاح. / Your appointment has been cancelled successfully.
                  </p>

                  <div style="background-color: #fef2f2; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626;">
                    <table style="width: 100%; border-collapse: collapse;">
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">الخدمة / Service:</td>
                        <td style="padding: 8px 0; color: #333;">{service_name}</td>
                      </tr>
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">الطبيب / Doctor:</td>
                        <td style="padding: 8px 0; color: #333;">{doctor_name}</td>
                      </tr>
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">التاريخ / Date:</td>
                        <td style="padding: 8px 0; color: #333;">{formatted_date}</td>
                      </tr>
                      <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">الوقت / Time:</td>
                        <td style="padding: 8px 0; color: #333;">{formatted_time}</td>
                      </tr>
                    </table>
                  </div>

                  <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    إذا كنت بحاجة لحجز موعد جديد، يرجى التواصل معنا.<br>
                    If you need to book a new appointment, please contact us.
                  </p>

                  <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">

                  <p style="color: #999; font-size: 12px; text-align: center;">
                    <strong>Riyadh Dental Care Clinic</strong><br>
                    <strong>عيادة الرياض لطب الأسنان</strong>
                  </p>
                </div>
              </body>
            </html>
            """

            # Attach both versions
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            self._send_email(msg)

            return {
                'status': 'success',
                'message': f'Cancellation email sent to {patient_email}'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to send email: {str(e)}'
            }

    def send_reschedule_confirmation(
        self,
        patient_email: str,
        patient_name: str,
        service_name: str,
        doctor_name: str,
        old_datetime: datetime,
        new_datetime: datetime
    ) -> dict:
        """
        Send reschedule confirmation email to patient

        Args:
            patient_email: Patient's email address
            patient_name: Patient's name
            service_name: Service name
            doctor_name: Doctor's name
            old_datetime: Previous appointment date and time
            new_datetime: New appointment date and time

        Returns:
            Success or error dict
        """
        print("\n" + "="*60)
        print("[EMAIL DEBUG] Starting send_reschedule_confirmation")
        print(f"[EMAIL DEBUG] To: {patient_email}")
        print(f"[EMAIL DEBUG] Patient: {patient_name}")
        print(f"[EMAIL DEBUG] Old: {old_datetime}, New: {new_datetime}")
        print("="*60 + "\n")

        try:
            # Format datetimes
            old_date = old_datetime.strftime('%A, %B %d, %Y')
            old_time = old_datetime.strftime('%I:%M %p')
            new_date = new_datetime.strftime('%A, %B %d, %Y')
            new_time = new_datetime.strftime('%I:%M %p')

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.gmail_address
            msg['To'] = patient_email
            msg['Subject'] = f'Appointment Rescheduled - {service_name}'

            # Plain text version
            text_body = f"""
مرحباً {patient_name},

تم إعادة جدولة موعدك بنجاح!

الخدمة: {service_name}
الطبيب: {doctor_name}

الموعد السابق:
  التاريخ: {old_date}
  الوقت: {old_time}

الموعد الجديد:
  التاريخ: {new_date}
  الوقت: {new_time}

---

Hello {patient_name},

Your appointment has been rescheduled successfully!

Service: {service_name}
Doctor: {doctor_name}

Previous Appointment:
  Date: {old_date}
  Time: {old_time}

New Appointment:
  Date: {new_date}
  Time: {new_time}

See you at the new time!

---
Riyadh Dental Care Clinic
عيادة الرياض لطب الأسنان
            """

            # HTML version
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">

                  <h2 style="color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px;">
                    🔄 Appointment Rescheduled / تم إعادة جدولة الموعد
                  </h2>

                  <p style="font-size: 16px; color: #333;">
                    <strong>مرحباً {patient_name} / Hello {patient_name},</strong>
                  </p>

                  <p style="color: #666;">
                    تم إعادة جدولة موعدك بنجاح! / Your appointment has been rescheduled successfully!
                  </p>

                  <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="color: #666; font-weight: bold; margin: 0 0 10px 0;">الخدمة / Service:</p>
                    <p style="color: #333; margin: 0 0 15px 0;">{service_name}</p>

                    <p style="color: #666; font-weight: bold; margin: 0 0 10px 0;">الطبيب / Doctor:</p>
                    <p style="color: #333; margin: 0 0 20px 0;">{doctor_name}</p>

                    <div style="display: flex; gap: 20px;">
                      <div style="flex: 1; background-color: #fee2e2; padding: 15px; border-radius: 6px;">
                        <p style="color: #991b1b; font-weight: bold; margin: 0 0 10px 0;">الموعد السابق / Previous:</p>
                        <p style="color: #333; margin: 0; font-size: 14px;">{old_date}</p>
                        <p style="color: #333; margin: 5px 0 0 0; font-weight: bold;">{old_time}</p>
                      </div>

                      <div style="flex: 1; background-color: #dbeafe; padding: 15px; border-radius: 6px;">
                        <p style="color: #1e40af; font-weight: bold; margin: 0 0 10px 0;">الموعد الجديد / New:</p>
                        <p style="color: #333; margin: 0; font-size: 14px;">{new_date}</p>
                        <p style="color: #333; margin: 5px 0 0 0; font-weight: bold;">{new_time}</p>
                      </div>
                    </div>
                  </div>

                  <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    نراك في الموعد الجديد! / See you at the new time!
                  </p>

                  <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">

                  <p style="color: #999; font-size: 12px; text-align: center;">
                    <strong>Riyadh Dental Care Clinic</strong><br>
                    <strong>عيادة الرياض لطب الأسنان</strong>
                  </p>
                </div>
              </body>
            </html>
            """

            # Attach both versions
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            self._send_email(msg)

            return {
                'status': 'success',
                'message': f'Reschedule confirmation email sent to {patient_email}'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to send email: {str(e)}'
            }

    def _send_email(self, msg: MIMEMultipart):
        """
        Internal method to send email via SMTP

        Args:
            msg: MIMEMultipart message object

        Raises:
            Exception if sending fails
        """
        try:
            print(f"[SMTP DEBUG] Connecting to {self.smtp_server}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)

            print(f"[SMTP DEBUG] Starting TLS...")
            server.starttls()

            print(f"[SMTP DEBUG] Logging in as {self.gmail_address}...")
            server.login(self.gmail_address, self.gmail_password)

            print(f"[SMTP DEBUG] Sending message...")
            server.send_message(msg)

            print(f"[SMTP DEBUG] Closing connection...")
            server.quit()

            print(f"[SMTP DEBUG] ✅ Email sent successfully!")
        except Exception as e:
            print(f"[SMTP DEBUG] ❌ SMTP error: {str(e)}")
            raise Exception(f"SMTP error: {str(e)}")


# Singleton instance
_gmail_instance = None


def get_gmail() -> GmailService:
    """Get or create Gmail service instance"""
    global _gmail_instance
    if _gmail_instance is None:
        _gmail_instance = GmailService()
    return _gmail_instance