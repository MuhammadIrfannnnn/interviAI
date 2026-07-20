import fitz
from app.models.user import User
import uuid
from pathlib import Path
import shutil
from app.models.resume import Resume
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.utils.pdf import extract_text_from_pdf
from app.utils.text import clean_resume_text
from app.services.ai_service import parse_resume
from app.models.parsed_resume import ParsedResume
from app.services.parsed_resume_service import save_parsed_resume
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def upload_resume(file: UploadFile, current_user: User, db: Session) -> Resume:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    existing_resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if existing_resume:
        raise HTTPException(status_code=400, detail="User already has a resume uploaded")
    filename = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    text = extract_text_from_pdf(file_path=str(file_path))
    text=clean_resume_text(text)
    parse_text=parse_resume(text)
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=str(file_path),
        extracted_text=text
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    save_parsed_resume(db=db,resume_id=resume.id,parsed_data=parse_text)
    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "pages": len(fitz.open(file_path)),
        "characters": len(text),
        "Parsed_resume":parse_text.model_dump()
    }
def get_resume(
    db: Session,
    current_user: User,
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    parsed_resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.resume_id == resume.id
        )
        .first()
    )

    return {
        "resume": {
            "id": resume.id,
            "file_name": resume.file_name,
            "uploaded_at": resume.uploaded_at,
            "file_path": resume.file_path,
        },
        "parsed_resume": (
            {
                "name": parsed_resume.name,
                "email": parsed_resume.email,
                "skills": parsed_resume.skills,
                "projects": parsed_resume.projects,
                "experience": parsed_resume.experience,
                "education": parsed_resume.education
            }
            if parsed_resume
            else None
        ),
    }
    
def delete_resume(
    db: Session,
    current_user: User,
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    parsed_resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.resume_id == resume.id
        )
        .first()
    )

    if parsed_resume:
        db.delete(parsed_resume)

    file_path = Path(resume.file_path)

    if file_path.exists():
        file_path.unlink()

    db.delete(resume)

    db.commit()

    return {
        "message": "Resume deleted successfully"
    }