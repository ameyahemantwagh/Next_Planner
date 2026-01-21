import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")


def send_email(to: str, subject: str, body: str) -> bool:
    """Send email via SMTP if configured, otherwise return False."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print(f"[DEV] Email not configured. To: {to} Subject: {subject}\n{body}")
        return False

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[DEV] Failed to send email: {e}")
        print(f"[DEV] Fallback: To: {to} Subject: {subject}\n{body}")
        return False
