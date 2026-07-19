from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.interview_service import start_interview,continue_interview,get_interview_history
from app.schemas.interview import InterviewStart
from app.schemas.interview_message import InterviewAnswer

router=APIRouter(
    prefix="/interview",
    tags=["interview"]
)

@router.post("/start")
def start_interview_endpoint(interview:InterviewStart,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return start_interview(db=db,current_user=current_user,interview=interview)

@router.post("/message")
def interview_message_endpoint(interview:InterviewAnswer,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return continue_interview(db=db,current_user=current_user,interview=interview)

@router.get("/history")
def interview_history(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    return get_interview_history(db=db,current_user=current_user)