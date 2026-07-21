from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.interview_service import get_dashboard, start_interview,continue_interview,get_interview_history,get_interview_details,export_interview_report
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

@router.get("/dashboard")
def get_dashboard_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_dashboard(
        db=db,
        current_user=current_user,
    )
    
@router.get("/{session_id}")
def get_interview_details_endpoint(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_interview_details(
        db=db,
        current_user=current_user,
        session_id=session_id,
    )
@router.get("/{session_id}/export")
def export_interview_report_endpoint(session_id: int,current_user: User = Depends(get_current_user),db: Session = Depends(get_db),):
    return export_interview_report(db=db,current_user=current_user,session_id=session_id)