from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.interview_service import start_interview
from app.schemas.interview import InterviewStart
router=APIRouter(
    prefix="/interview",
    tags=["interview"]
)

@router.post("/start")
def start_interview_endpoint(interview:InterviewStart,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return start_interview(db=db,current_user=current_user,interview=interview)