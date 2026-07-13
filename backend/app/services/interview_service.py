from sqlalchemy.orm import Session
from app.models.user import User
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume as ParsedResumeModel
from app.models.interview_session import InterviewSession
from app.models.interview_message import InterviewMessage
from app.services.ai_service import generate_first_question,generate_next_question
from fastapi import HTTPException
from app.schemas.interview import InterviewStart
from app.schemas.interview_message import InterviewAnswer

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

    first_question=generate_first_question(parsed_resume=parsed_resume,role_applied=interview.role_applied,difficulty=interview.difficulty)
    message=InterviewMessage(session_id=session.id,speaker="AI",message=first_question)
    db.add(message)
    db.commit()
    return {
    "message": "Interview started successfully",
    "session_id": session.id,
    "first_question": first_question
    }

def continue_interview(db:Session,current_user:User,interview:InterviewAnswer):
    session=(db.query(InterviewSession).filter(InterviewSession.id==interview.session_id,InterviewSession.user_id==current_user.id).first())
    if not session:
        raise HTTPException(status_code=404,detail="session not found")
    if session.status!="active":
        raise HTTPException(status_code=400,detail="Interview has already ended")
    candidate_message=InterviewMessage(session_id=session.id,speaker="candidate",message=interview.answer)
    db.add(candidate_message)
    db.commit()
    db.refresh(candidate_message)
    resume=(db.query(Resume).filter(Resume.user_id==current_user.id).first())
    if not resume:
        raise HTTPException(status_code=404,detail="resume not found")
    parsed_resume=(db.query(ParsedResumeModel).filter(ParsedResumeModel.resume_id==resume.id).first())
    if not parsed_resume:
        raise HTTPException(status_code=404,detail="parsed resume not found")
    messages=(db.query(InterviewMessage).filter(InterviewMessage.session_id==session.id).order_by(InterviewMessage.created_at.asc()).all())
    conversation=""
    for message in messages:
        conversation+=f"{message.speaker}:{message.message}\n"
    next_question=generate_next_question(parsed_resume=parsed_resume,role_applied=session.role_applied,difficulty=session.difficulty,conversation=conversation)
    ai_message=InterviewMessage(session_id=session.id,speaker="AI",message=next_question)
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    return {
    "session_id": session.id,
    "next_question": next_question
    }