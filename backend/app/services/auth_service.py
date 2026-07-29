from sqlalchemy.orm import Session
from app.models.user import AuthProvider, User
from app.core.security import hash_password,verify_password,create_access_token
from app.schemas.user import ForgotPasswordRequest, MessageResponse, ResendOtpRequest, ResetPasswordRequest, UserCreate,UserLogin,RegisterResponse,TokenResponse,VerifyOtpRequest,GoogleLoginRequest
from datetime import datetime, timedelta
from app.utils.otp import generate_otp,hash_otp,get_otp_expiry,verify_otp_hash
from app.services.email_service import send_otp_email
from app.models.user import OtpPurpose
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings

def register_user(db:Session,user_data:UserCreate)->RegisterResponse:
    existing_user=db.query(User).filter(User.email==user_data.email).first()
    if existing_user:
        raise ValueError("User with this email already exists")
    hashed_password=hash_password(user_data.password)
    otp=generate_otp()
    otp_hash=hash_otp(otp)
    new_user=User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        is_verified=False,
        otp_hash=otp_hash,
        otp_purpose=OtpPurpose.VERIFY_EMAIL,
        otp_expires_at=get_otp_expiry(),
        last_otp_sent_at=datetime.utcnow()
    )
  
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    try:
        send_otp_email(
            email=new_user.email,
            otp=otp,
            purpose=OtpPurpose.VERIFY_EMAIL.value,
        )
    except Exception:
        db.delete(new_user)
        db.commit()
        raise ValueError("Failed to send verification email.")
    return RegisterResponse(
    message="Verification code sent successfully.",
    email=new_user.email,
)

def login_user(db:Session,user_data:UserLogin)->TokenResponse:
    user=db.query(User).filter(User.email==user_data.email).first()
    if not user:
        raise ValueError("Invalid email or password")
    if not user.is_verified:
        raise ValueError("Please verify your email before logging in.")
    if not verify_password(user_data.password,user.hashed_password):
        raise ValueError("Invalid email or password")
    data={
    "sub": str(user.id),
    "email": user.email,
    "role": user.role.value
    }
    token=create_access_token(data=data)
    return TokenResponse(access_token=token,token_type="bearer")


def verify_otp(db: Session,request: VerifyOtpRequest)-> TokenResponse:
    user = (db.query(User).filter(User.email == request.email).first())
    if not user:
        raise ValueError("Invalid verification code.")
    if user.is_verified:
        raise ValueError("Email is already verified.")
    if (
        user.otp_hash is None
        or user.otp_purpose is None
        or user.otp_expires_at is None
    ):
        raise ValueError("Verification code not found.")

    if user.otp_purpose != OtpPurpose.VERIFY_EMAIL:
        raise ValueError("Invalid verification code.")

    if datetime.utcnow() > user.otp_expires_at:
        raise ValueError("Verification code has expired.")

    if not verify_otp_hash(request.otp,user.otp_hash):
        raise ValueError("Invalid verification code.")
    user.is_verified = True

    user.otp_hash = None
    user.otp_purpose = None
    user.otp_expires_at = None
    user.last_otp_sent_at = None

    db.commit()
    db.refresh(user)

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
    }
    token = create_access_token(payload)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )
    
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
    
def forgot_password(
    db: Session,
    request: ForgotPasswordRequest,
) -> MessageResponse:

    generic_response = MessageResponse(
        message="If an account exists for this email, a reset code has been sent."
    )

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    # Don't reveal whether the email exists
    if not user:
        return generic_response

    # Google accounts don't have local passwords
    if user.auth_provider == AuthProvider.GOOGLE:
        return generic_response

    if (
        user.last_otp_sent_at
        and datetime.utcnow() - user.last_otp_sent_at < timedelta(seconds=60)
    ):
        raise ValueError(
            "Please wait 60 seconds before requesting another reset code."
        )

    otp = generate_otp()

    user.otp_hash = hash_otp(otp)
    user.otp_purpose = OtpPurpose.RESET_PASSWORD
    user.otp_expires_at = get_otp_expiry()
    user.last_otp_sent_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    send_otp_email(
        email=user.email,
        otp=otp,
        purpose=OtpPurpose.RESET_PASSWORD.value,
    )

    return generic_response

def reset_password(
    db: Session,
    request: ResetPasswordRequest,
) -> MessageResponse:

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise ValueError("Invalid reset request.")

    if (
        user.otp_hash is None
        or user.otp_purpose is None
        or user.otp_expires_at is None
    ):
        raise ValueError("Reset code not found.")

    if user.otp_purpose != OtpPurpose.RESET_PASSWORD:
        raise ValueError("Invalid reset code.")

    if datetime.utcnow() > user.otp_expires_at:
        raise ValueError("Reset code has expired.")

    if not verify_otp_hash(
        request.otp,
        user.otp_hash,
    ):
        raise ValueError("Invalid reset code.")

    user.hashed_password = hash_password(
        request.new_password
    )

    user.otp_hash = None
    user.otp_purpose = None
    user.otp_expires_at = None
    user.last_otp_sent_at = None

    db.commit()

    return MessageResponse(
        message="Password reset successfully."
    )

def google_login(db: Session,request:GoogleLoginRequest)->TokenResponse:
    try:
        id_info = id_token.verify_oauth2_token(
            request.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise ValueError("Invalid Google token.")
    email = id_info["email"]
    full_name = id_info.get("name", "")
    email_verified = id_info.get("email_verified", False)
    if not email_verified:
        raise ValueError("Google account is not verified.")
    user = (db.query(User).filter(User.email == email).first())
    if user is None:
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=None,
            auth_provider=AuthProvider.GOOGLE,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if user.auth_provider == AuthProvider.LOCAL:
            user.auth_provider = AuthProvider.GOOGLE
            user.is_verified = True
            db.commit()
            db.refresh(user)
        elif user.auth_provider==AuthProvider.GOOGLE:
            pass
    payload = {
    "sub": str(user.id),
    "email": user.email,
    "role": user.role.value,
}

    token = create_access_token(payload)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


