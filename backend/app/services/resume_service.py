from datetime import datetime
import logging

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
from app.services.resume_summary import generate_resume_summary

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

_RESUME_KEYWORDS = [
    "experience", "education", "skills", "work", "project",
    "employment", "university", "college", "degree", "technology",
    "certification", "objective", "summary", "career", "professional",
    "internship", "qualification", "resume", "curriculum", "vitae",
]


def _looks_like_resume(text: str) -> bool:
    """Lightweight keyword check to reject obvious non-resume PDFs."""
    if len(text) < 50:
        return False
    lower = text.lower()
    return sum(1 for kw in _RESUME_KEYWORDS if kw in lower) >= 2


def upload_resume(file: UploadFile, current_user: User, db: Session) -> Resume:
    # ── 1. Validate file type ──────────────────────────────────────────────
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # ── 2. Validate file size ──────────────────────────────────────────────
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File is too large. Maximum size is 5 MB.",
        )

    # ── 3. Save file to disk ───────────────────────────────────────────────
    filename = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ── 4. Extract text from PDF ───────────────────────────────────────────
    try:
        text = extract_text_from_pdf(file_path=str(file_path))
    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="Could not read the PDF. The file may be corrupted or password-protected.",
        )

    text = clean_resume_text(text)

    # ── 5. Validate extracted text is not empty ────────────────────────────
    if not text or len(text.strip()) < 50:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF appears to be empty or unreadable.",
        )

    # ── 6. Lightweight resume sanity check (before expensive AI call) ──────
    if not _looks_like_resume(text):
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF does not appear to be a valid resume.",
        )

    # ── 7. Parse resume via Gemini ─────────────────────────────────────────
    try:
        parsed_data = parse_resume(text)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="Could not process the resume. Please upload a valid PDF resume.",
        )

    # ── 8. Generate summary (used by the interview engine) ─────────────────
    summary = generate_resume_summary(parsed_data)

    # ── 9. Handle replacement vs new upload ────────────────────────────────
    existing_resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()

    if existing_resume:
        # Delete old file only after new file has been fully validated
        old_file = Path(existing_resume.file_path)
        if old_file.exists():
            old_file.unlink()

        existing_resume.file_name = file.filename
        existing_resume.file_path = str(file_path)
        existing_resume.extracted_text = text
        existing_resume.updated_at = datetime.utcnow()

        parsed_resume = (
            db.query(ParsedResume)
            .filter(ParsedResume.resume_id == existing_resume.id)
            .first()
        )
        if parsed_resume:
            parsed_resume.name = parsed_data.name
            parsed_resume.email = parsed_data.email
            parsed_resume.skills = parsed_data.skills
            parsed_resume.projects = parsed_data.projects
            parsed_resume.experience = parsed_data.experience
            parsed_resume.education = parsed_data.education
            parsed_resume.summary = summary
        else:
            save_parsed_resume(
                db=db,
                resume_id=existing_resume.id,
                parsed_data=parsed_data,
            )

        db.commit()
        db.refresh(existing_resume)

        return {
            "message": "Resume replaced successfully",
            "resume_id": existing_resume.id,
            "pages": len(fitz.open(file_path)),
            "characters": len(text),
            "parsed_resume": parsed_data.model_dump(),
        }

    # New resume
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=str(file_path),
        extracted_text=text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    save_parsed_resume(db=db, resume_id=resume.id, parsed_data=parsed_data)

    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "pages": len(fitz.open(file_path)),
        "characters": len(text),
        "Parsed_resume": parsed_data.model_dump(),
    }


def get_resume(db: Session, current_user: User):
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
            "updated_at": resume.updated_at,
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
