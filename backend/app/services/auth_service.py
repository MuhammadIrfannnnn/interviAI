from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import UserCreate

def register_user(db:Session,user_data:UserCreate):
    existing_user=db.query(User).filter(User.email==user_data.email).first()
    if existing_user:
        raise ValueError("User with this email already exists")
    hashed_password=hash_password(user_data.password)
    new_user=User(
        full_name=user_data.full_name,  
        email=user_data.email,
        hashed_password=hashed_password
    )
  
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


