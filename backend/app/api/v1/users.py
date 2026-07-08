from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router=APIRouter(
    prefix="/users",tags=["Users"]
)

@router.get("/me",response_model=UserResponse)
def get_current_user_info(current_user:User=Depends(get_current_user)):
    return current_user