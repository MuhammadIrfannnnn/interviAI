from sqlalchemy.orm import Session
from app.models.parsed_resume import ParsedResume
from app.services.resume_summary import generate_resume_summary

def save_parsed_resume(db:Session,resume_id:int,parsed_data:ParsedResume)->ParsedResume:
    parsed_resume = ParsedResume(
        resume_id=resume_id,
        name=parsed_data.name,
        email=parsed_data.email,
        skills=parsed_data.skills,
        education=parsed_data.education,
        experience=parsed_data.experience,
        projects=parsed_data.projects,
        summary=summary
    )
    db.add(parsed_resume)
    db.flush()
    
    summary = generate_resume_summary(parsed_resume)
    parsed_resume.summary = summary
    db.commit()
    db.refresh(parsed_resume)

    return parsed_resume