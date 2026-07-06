from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin,TokenResponse
from app.services.auth_service import register_user,login_user

router=APIRouter(
    prefix="/auth",tags=["Authentication"]
)

@router.post("/register",response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db=db, user_data=user_data)

@router.post("/login",response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db=db, user_data=user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
