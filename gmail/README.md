# Gmail Integration for Dental Clinic AI Agent

This folder contains the Gmail SMTP integration for sending emails from the Dental Clinic AI Agent.

## Overview

The dental clinic agent uses Gmail SMTP to send:
- Appointment confirmations
- Reminder emails (24 hours before appointments)
- Cancellation/modification notifications
- Follow-up emails after patient feedback
- Escalation alerts to clinic staff

## Setup Instructions

### Prerequisites

- A Gmail account (e.g., `yourname@gmail.com`)
- Python 3.7+ with `python-dotenv` installed
- 2-Step Verification enabled on your Gmail account

### Step 1: Enable 2-Step Verification

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "How you sign in to Google", click on **2-Step Verification**
3. Follow the steps to enable it if not already enabled

### Step 2: Create App Password

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Click **Select app** → Choose **Mail**
3. Click **Select device** → Choose **Other (Custom name)**
4. Enter a name like "Dental Clinic AI"
5. Click **Generate**
6. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
7. **Important**: Save this password - you won't be able to see it again!

### Step 3: Configure Environment Variables

Add the following to your `.env` file in the project root:

```bash
# Gmail SMTP Configuration
GMAIL_ADDRESS=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password-without-spaces
```

**Example:**
```bash
GMAIL_ADDRESS=musaed299@gmail.com
GMAIL_APP_PASSWORD=abcdeffhijklmnop
```

### Step 4: Test the Integration

Run the test script to verify your setup:

```bash
python gmail/test_gmail.py
```

Expected output:
```
Testing Gmail SMTP...
==================================================
Connecting to Gmail SMTP server...
Logging in...
Sending email...
✅ Email sent successfully!
From: your-gmail@gmail.com
To: recipient@gmail.com
Subject: Test Email - Dental Clinic AI Agent
```

## Usage in Your Application

### Basic Example

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body_text, body_html=None):
    """Send an email using Gmail SMTP"""

    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = gmail_address
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach plain text
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

    # Attach HTML if provided
    if body_html:
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))

    # Send via Gmail SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(gmail_address, gmail_password)
        server.send_message(msg)
```

### Appointment Confirmation Example

```python
def send_appointment_confirmation(patient_email, patient_name, appointment_time):
    subject = "Appointment Confirmation - Dental Clinic"

    body_text = f"""
Dear {patient_name},

Your appointment has been confirmed for {appointment_time}.

Please arrive 10 minutes early.

Best regards,
Dental Clinic AI System
    """

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>Appointment Confirmed</h2>
        <p>Dear {patient_name},</p>
        <p>Your appointment has been confirmed for <strong>{appointment_time}</strong>.</p>
        <p>Please arrive 10 minutes early.</p>
        <hr>
        <p style="color: #666;">Best regards,<br>Dental Clinic AI System</p>
      </body>
    </html>
    """

    send_email(patient_email, subject, body_text, body_html)
```

## Technical Details

### SMTP Settings

- **Server**: `smtp.gmail.com`
- **Port**: `587`
- **Encryption**: TLS (STARTTLS)
- **Authentication**: App Password

### Sending Limits

Gmail has the following sending limits:
- **Free Gmail accounts**: ~500 emails/day
- **Google Workspace accounts**: ~2,000 emails/day

For production use with higher volume, consider:
- SendGrid (100 emails/day free, then paid)
- Resend (3,000 emails/month free)
- AWS SES (pay-as-you-go)

### Features Supported

- ✅ Plain text emails
- ✅ HTML emails
- ✅ Attachments
- ✅ UTF-8 encoding (Arabic & English)
- ✅ Custom headers
- ✅ BCC/CC recipients

## Troubleshooting

### Error: "Username and Password not accepted"

**Causes:**
1. App password is incorrect
2. App password was created for a different Gmail account
3. 2-Step Verification is not enabled

**Solution:**
1. Verify you're using the correct Gmail account
2. Delete the old app password and create a new one
3. Ensure `.env` file has the correct credentials without spaces

### Error: "SMTPAuthenticationError"

**Solution:**
1. Check if 2-Step Verification is enabled
2. Regenerate the app password
3. Make sure you're using an app password, not your regular Gmail password

### Email goes to spam

**Solutions:**
1. Ask recipients to mark your emails as "Not Spam"
2. Use a custom domain with SPF/DKIM records (requires Google Workspace)
3. Avoid spam trigger words in subject/body
4. Include an unsubscribe link for marketing emails

## Security Best Practices

1. ✅ **Never commit** `.env` file to version control
2. ✅ **Use app passwords**, not your main Gmail password
3. ✅ **Rotate passwords** regularly
4. ✅ **Limit access** to the `.env` file (use file permissions)
5. ✅ **Monitor usage** in Gmail's sent folder

## Files in This Folder

- `README.md` - This documentation
- `test_gmail.py` - Test script to verify Gmail SMTP setup

## Additional Resources

- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Google App Passwords](https://support.google.com/accounts/answer/185833)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)
- [Email MIME Types](https://docs.python.org/3/library/email.mime.html)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the [Gmail SMTP documentation](https://support.google.com/mail/answer/7126229)
3. Check your Gmail account's [recent security activity](https://myaccount.google.com/notifications)