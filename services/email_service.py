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

— AI-Blockchain Integrated E-Democracy System Team
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

def send_vote_receipt_email(to_email, election_name, constituency_name, receipt_hash):
    sender_email = os.getenv("MAIL_USERNAME")
    sender_password = os.getenv("MAIL_PASSWORD")
    smtp_host = os.getenv("MAIL_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("MAIL_PORT", 587))

    if not sender_email or not sender_password:
        raise Exception("Email service not configured")

    subject = "Your Voting Receipt"

    body = f"""
Dear Voter,

Your vote has been successfully recorded.

Election: {election_name}
Constituency: {constituency_name}
Receipt Hash: {receipt_hash}

This receipt confirms that your vote was securely recorded.
Your ballot remains anonymous.

Thank you for participating in the democratic process.

— AI-Blockchain Integrated E-Democracy System
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
    except Exception:
        raise Exception("Failed to send receipt email")