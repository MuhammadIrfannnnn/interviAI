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
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=str(file_path),
        extracted_text=text
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "pages": len(fitz.open(file_path)),
        "characters": len(text)
    }