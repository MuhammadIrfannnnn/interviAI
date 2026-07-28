import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_otp_email(
    email: str,
    otp: str,
    purpose: str,
):
    if purpose == "verify_email":
        subject = "Verify your InterviAI account"

        body = f"""
Welcome to InterviAI!

Your verification code is:

{otp}

This code expires in 10 minutes.

If you didn't create this account, simply ignore this email.

Regards,
InterviAI
"""

    else:
        subject = "Reset your InterviAI password"

        body = f"""
We received a request to reset your password.

Your reset code is:

{otp}

This code expires in 10 minutes.

If you didn't request this, ignore this email.

Regards,
InterviAI
"""

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = settings.SMTP_EMAIL
    message["To"] = email

    message.set_content(body)

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
    ) as smtp:

        smtp.starttls()

        smtp.login(
            settings.SMTP_EMAIL,
            settings.SMTP_PASSWORD,
        )

        smtp.send_message(message)