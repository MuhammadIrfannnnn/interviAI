from sqlalchemy.orm import Session
from app.models.user import User
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume as ParsedResumeModel
from app.models.interview_session import InterviewSession
from app.models.interview_message import InterviewMessage
from app.services.ai_service import generate_first_question
from fastapi import HTTPException
from app.schemas.interview import InterviewStart
from app.services.ai_service import generate_first_question
def start_interview(db:Session,current_user:User,interview:InterviewStart):
    resume=(db.query(Resume).filter(Resume.user_id==current_user.id).first())
    if not resume:
        raise HTTPException(status_code=404,detail="resume not found")
    parsed_resume=(db.query(ParsedResumeModel).filter(ParsedResumeModel.resume_id==resume.id).first())
    if not parsed_resume:
        raise HTTPException(status_code=404,detail="parsed resume not found")
    session=InterviewSession(
        user_id=current_user.id,
        resume_id=resume.id,
        role_applied=interview.role_applied,
        difficulty=interview.difficulty,
        status="active"
    )  
    db.add(session)
    db.commit()
    db.refresh(session)

    g