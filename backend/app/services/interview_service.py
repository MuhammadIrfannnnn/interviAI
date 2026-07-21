from sqlalchemy.orm import Session
from app.models.user import User
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume as ParsedResumeModel
from app.models.interview_session import InterviewSession
from app.models.interview_message import InterviewMessage
from app.models.parsed_resume import ParsedResume
from app.services.ai_service import generate_final_report, generate_first_question,generate_next_question,evaluate_answer,plan_next_step,update_interview_state
from fastapi import HTTPException, Path
from app.schemas.interview import InterviewStart
from app.schemas.interview_message import InterviewAnswer
from app.models.interview_evaluation import InterviewEvaluation
from app.schemas.interview_state import InterviewState
from datetime import datetime
from fastapi.responses import FileResponse
from app.models.interview_report import InterviewReport
from app.services.pdf_service import generate_interview_report_pdf

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
    state = InterviewState()
    session.interview_state = state.model_dump()
    db.add(session)
    db.commit()
    db.refresh(session)

    first_question=generate_first_question(parsed_resume=parsed_resume,role_applied=interview.role_applied,difficulty=interview.difficulty)
    message=InterviewMessage(session_id=session.id,speaker="AI",message=first_question)
    db.add(message)
    db.commit()
    db.refresh(message)
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
    evaluation=evaluate_answer(parsed_resume=parsed_resume,role_applied=session.role_applied,difficulty=session.difficulty,conversation=conversation,candidate_answer=interview.answer)
    evaluation_db = InterviewEvaluation(
    message_id=candidate_message.id,
    technical_score=evaluation.technical_score,
    communication_score=evaluation.communication_score,
    confidence_score=evaluation.confidence_score,
    correctness=evaluation.correctness,
    strengths=evaluation.strengths,
    weaknesses=evaluation.weaknesses,
    feedback=evaluation.feedback,
    )
    db.add(evaluation_db)
    db.commit()
    db.refresh(evaluation_db)
    evaluations = (db.query(InterviewEvaluation).join(InterviewMessage).filter(InterviewMessage.session_id == session.id).all())
    evaluation_summary = ""
    for eval_record in evaluations:
        evaluation_summary += f"""
    Technical: {eval_record.technical_score}/10
    Communication: {eval_record.communication_score}/10
    Confidence: {eval_record.confidence_score}/10
    Correctness: {eval_record.correctness}
    Strengths:
    {", ".join(eval_record.strengths)}
    Weaknesses:
    {", ".join(eval_record.weaknesses)}
    Feedback: {eval_record.feedback}
    """
    state = InterviewState(**session.interview_state)
    updated_state=update_interview_state(state=state,evaluation=evaluation_summary,conversation=conversation)
    session.interview_state = updated_state.model_dump()
    db.commit()
    db.refresh(session)
    plan=plan_next_step(parsed_resume=parsed_resume,role_applied=session.role_applied,difficulty=session.difficulty,conversation=conversation,evaluations=evaluation_summary,state=updated_state)
    if plan.action == "end_interview":
    #     session.status = "completed"
    #     session.ended_at = datetime.utcnow()
    #     db.commit()
    #     db.refresh(session)
    # # generate final report
    #     return {
    #          "message": "Interview completed successfully",
    #          "session_id": session.id,
    #          "reason":plan.reason
    #          }
        report = generate_final_report(
        parsed_resume=parsed_resume,
        role_applied=session.role_applied,
        difficulty=session.difficulty,
        conversation=conversation,
        evaluations=evaluation_summary,
        state=updated_state,
        )
        existing_report = (db.query(InterviewReport).filter(InterviewReport.session_id == session.id).first())
        if existing_report:
            raise HTTPException(status_code=400,detail="Interview report already exists.")
        report_db = InterviewReport(
        session_id=session.id,
        report=report.model_dump(),
        )
        db.add(report_db)
        final_message = InterviewMessage(
        session_id=session.id,
        speaker="AI",
        message="Thank you. That concludes the interview. I appreciate your time. Your interview report has been generated.")
        db.add(final_message)

        session.status = "completed"
        session.ended_at = datetime.utcnow()
        session.overall_score = report.overall_score
        db.commit()
        db.refresh(report_db)
        db.refresh(session)
        
        return {
            "message": "Interview completed successfully",
            "session_id": session.id,
            "report": report.model_dump()
        }
    
    # decision = should_end_interview(parsed_resume=parsed_resume,role_applied=session.role_applied,difficulty=session.difficulty,conversation=conversation,evaluations=evaluation_summary)
    # if decision.end_interview:
    #     session.status="completed"
    #     db.commit()
    #     return {
    #     "message": "Interview completed successfully",
    #     "session_id": session.id,
    #     "reason": decision.reason,
    #     "evaluation": evaluation.model_dump()
    #     }
    next_question=generate_next_question(parsed_resume=parsed_resume,role_applied=session.role_applied,difficulty=session.difficulty,conversation=conversation,evaluation=evaluation,plan=plan)
    ai_message=InterviewMessage(session_id=session.id,speaker="AI",message=next_question)
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    return {
    "session_id": session.id,
    "evaluation":evaluation.model_dump(),
    "next_question": next_question
    }


def get_interview_history(db: Session,current_user: User):
    sessions = (db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).order_by(InterviewSession.started_at.desc()).all())
    history = []
    for session in sessions:
        history.append({
            "session_id": session.id,
            "role_applied": session.role_applied,
            "difficulty": session.difficulty,
            "status": session.status,
            "overall_score": session.overall_score,
            "started_at": session.started_at,
            "ended_at": session.ended_at
        })

    return {
        "interviews": history
    }
    
def get_interview_details(
    db: Session,
    current_user: User,
    session_id: int,
):
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    messages = (
        db.query(InterviewMessage)
        .filter(
            InterviewMessage.session_id == session.id,
        )
        .order_by(
            InterviewMessage.created_at.asc(),
        )
        .all()
    )

    evaluations = {
    evaluation.message_id: evaluation
    for evaluation in (
        db.query(InterviewEvaluation)
        .join(InterviewMessage)
        .filter(InterviewMessage.session_id == session.id)
        .all()
        )
    }

    conversation = []

    for message in messages:

        evaluation = evaluations.get(message.id)

        conversation.append(
            {
                "id": message.id,
                "speaker": message.speaker,
                "message": message.message,
                "created_at": message.created_at,
                "evaluation": (
                    {
                        "technical_score": evaluation.technical_score,
                        "communication_score": evaluation.communication_score,
                        "confidence_score": evaluation.confidence_score,
                        "correctness": evaluation.correctness,
                        "strengths": evaluation.strengths,
                        "weaknesses": evaluation.weaknesses,
                        "feedback": evaluation.feedback,
                    }
                    if evaluation
                    else None
                ),
            }
        )

    return {
        "session": {
            "id": session.id,
            "role_applied": session.role_applied,
            "difficulty": session.difficulty,
            "status": session.status,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "overall_score": session.overall_score,
        },
        "messages": conversation,
        "report": (
            session.report.report
            if session.report
            else None
        ),
    }
def get_dashboard(
    db: Session,
    current_user: User,
):
    sessions = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.user_id == current_user.id
        )
        .order_by(
            InterviewSession.started_at.desc()
        )
        .all()
    )

    total_interviews = len(sessions)

    completed_sessions = [
        session
        for session in sessions
        if session.status == "completed"
    ]

    completed_interviews = len(completed_sessions)

    if completed_interviews > 0:
        average_score = round(
            sum(session.overall_score for session in completed_sessions)
            / completed_interviews,
            2,
        )

        best_score = max(
            session.overall_score
            for session in completed_sessions
        )
    else:
        average_score = 0
        best_score = 0

    recent_interviews = []

    for session in sessions[:5]:
        recent_interviews.append(
            {
                "id": session.id,
                "role_applied": session.role_applied,
                "difficulty": session.difficulty,
                "status": session.status,
                "overall_score": session.overall_score,
                "started_at": session.started_at,
                "ended_at": session.ended_at,
            }
        )

    return {
        "total_interviews": total_interviews,
        "completed_interviews": completed_interviews,
        "average_score": average_score,
        "best_score": best_score,
        "recent_interviews": recent_interviews,
    }

def export_interview_report(session_id:int,current_user:User,db:Session):
    session=db.query(InterviewSession).filter(InterviewSession.id==session_id,InterviewSession.user_id==current_user.id).first()
    if not session:
        raise HTTPException(status_code=402,detail="Session Not found")
    report = (db.query(InterviewReport).filter(InterviewReport.session_id == session.id,).first())
    if not report:
        raise HTTPException(status_code=404,detail="Interview report not found")
    pdf_path = generate_interview_report_pdf(session=session,report=report.report)
    return FileResponse(path=str(pdf_path),media_type="application/pdf",filename=f"Interview_Report_{session.id}.pdf")
