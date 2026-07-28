from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin,TokenResponse,RegisterResponse,VerifyOtpRequest
from app.services.auth_service import register_user,login_user,verify_otp


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
