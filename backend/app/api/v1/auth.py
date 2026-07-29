from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.user import ForgotPasswordRequest, ResetPasswordRequest, UserCreate, UserLogin,TokenResponse,RegisterResponse,VerifyOtpRequest,MessageResponse,ResendOtpRequest,GoogleLoginRequest
from app.services.auth_service import forgot_password, register_user,login_user, reset_password,verify_otp,google_login
from app.services.email_service import resend_otp


router=APIRouter(
    prefix="/auth",tags=["Authentication"]
)

@router.post("/register",response_model=RegisterResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db=db, user_data=user_data)

@router.post("/login",response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db=db, user_data=user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post(
    "/verify-otp",
    response_model=TokenResponse,
)
def verify_otp_endpoint(
    request: VerifyOtpRequest,
    db: Session = Depends(get_db),
):
    try:
        return verify_otp(
            db=db,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post(
    "/resend-otp",
    response_model=MessageResponse,
)
def resend_otp_endpoint(
    request: ResendOtpRequest,
    db: Session = Depends(get_db),
):
    try:
        return resend_otp(
            db=db,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post(
    "/forgot-password",
    response_model=MessageResponse,
)
def forgot_password_endpoint(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        return forgot_password(
            db=db,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
        
@router.post(
    "/reset-password",
    response_model=MessageResponse,
)
def reset_password_endpoint(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        return reset_password(
            db=db,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post(
    "/google",
    response_model=TokenResponse,
)
def google_login_endpoint(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return google_login(
            db=db,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )