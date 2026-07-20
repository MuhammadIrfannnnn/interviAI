from fastapi import APIRouter, Depends, File, UploadFile
from app.api.deps import get_current_user
from app.models.user import User
from app.models.resume import Resume
from pathlib import Path
from app.database.dependencies import get_db
from sqlalchemy.orm import Session
from app.services.resume_service import delete_resume, upload_resume
from app.services.resume_service import get_resume,delete_resume
UPLOAD_DIR = Path("backend/uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
router = APIRouter(
    prefix="/resume", tags=["Resume"]
    )

@router.post("/upload")
async def upload_resume_endpoint(file:UploadFile=File(...),current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return upload_resume(file=file, current_user=current_user, db=db)

@router.get("/")
def get_resume_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_resume(
        db=db,
        current_user=current_user,
    )
@router.delete("/delete")
def delete_resume_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_resume(
        db=db,
        current_user=current_user,
    )
