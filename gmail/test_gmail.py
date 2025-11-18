#!/usr/bin/env python3
"""
Test Gmail SMTP - Send email using Gmail's SMTP server
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_test_email():
    """Send a test email using Gmail SMTP"""

    # Get credentials from environment
    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_address or not gmail_password:
        print("❌ Error: Gmail credentials not found in .env file")
        return

    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = gmail_address
    msg['To'] = 'musaed9222@gmail.com'
    msg['Subject'] = 'Test Email - Dental Clinic AI Agent'

    # Email body (plain text and HTML)
    text_body = """
مرحباً!

هذه رسالة تجريبية من نظام عيادة الأسنان الذكي.

Hello!

This is a test email from the Dental Clinic AI Agent.

---
Dental Clinic AI System
عيادة الأسنان - النظام الذكي
    """

    html_body = """
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2563eb;">مرحباً! / Hello!</h2>

        <p>هذه رسالة تجريبية من نظام عيادة الأسنان الذكي.</p>
        <p>This is a test email from the Dental Clinic AI Agent.</p>

        <hr style="margin: 20px 0;">

        <p style="color: #666; font-size: 12px;">
          <strong>Dental Clinic AI System</strong><br>
          عيادة الأسنان - النظام الذكي
        </p>
      </body>
    </html>
    """

    # Attach both plain text and HTML versions
    part1 = MIMEText(text_body, 'plain', 'utf-8')
    part2 = MIMEText(html_body, 'html', 'utf-8')
    msg.attach(part1)
    msg.attach(part2)

    # Send email via Gmail SMTP
    try:
        print("Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable TLS encryption

        print("Logging in...")
        server.login(gmail_address, gmail_password)

        print("Sending email...")
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully!")
        print(f"From: {gmail_address}")
        print(f"To: musaed9222@gmail.com")
        print(f"Subject: Test Email - Dental Clinic AI Agent")

    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    print("Testing Gmail SMTP...")
    print("=" * 50)
    send_test_email()