import smtplib
from email.message import EmailMessage
from app.core.config import settings
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User, OtpPurpose
from app.schemas.user import ResendOtpRequest, MessageResponse
from app.utils.otp import (
    generate_otp,
    hash_otp,
    get_otp_expiry,
)
# from app.services.email_service import send_otp_email


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
        
def resend_otp(
    db: Session,
    request: ResendOtpRequest,
) -> MessageResponse:

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise ValueError("User not found.")

    if user.is_verified:
        raise ValueError("Email is already verified.")

    if (
        user.last_otp_sent_at
        and datetime.utcnow() - user.last_otp_sent_at < timedelta(seconds=60)
    ):
        raise ValueError(
            "Please wait 60 seconds before requesting another OTP."
        )

    otp = generate_otp()

    user.otp_hash = hash_otp(otp)
    user.otp_purpose = OtpPurpose.VERIFY_EMAIL
    user.otp_expires_at = get_otp_expiry()
    user.last_otp_sent_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    send_otp_email(
        email=user.email,
        otp=otp,
        purpose=OtpPurpose.VERIFY_EMAIL.value,
    )

    return MessageResponse(
        message="A new verification code has been sent to your email."
    )