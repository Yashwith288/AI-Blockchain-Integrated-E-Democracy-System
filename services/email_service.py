# services/email_service.py

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



def send_otp_email(to_email, otp):
    print(f"[OTP SENT] {to_email} -> {otp}")
    sender_email = os.getenv("MAIL_USERNAME")
    sender_password = os.getenv("MAIL_PASSWORD")
    smtp_host = os.getenv("MAIL_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("MAIL_PORT", 587))

    if not sender_email or not sender_password:
        raise Exception("Email service not configured")

    subject = "Your Voting OTP"
    body = f"""
Dear Voter,

Your One-Time Password (OTP) for voting is:

{otp}

This OTP is valid for 5 minutes.
Please do not share it with anyone.

— eVote System
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        raise Exception("Failed to send OTP email")
