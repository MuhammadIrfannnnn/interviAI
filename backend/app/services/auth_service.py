from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password,verify_password,create_access_token
from app.schemas.user import UserCreate,UserLogin

def register_user(db:Session,user_data:UserCreate)->User:
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

def login_user(db:Session,user_data:UserLogin)->dict:
    user=db.query(User).filter(User.email==user_data.email).first()
    if not user:
        raise ValueError("Invalid email or password")
    if not verify_password(user_data.password,user.hashed_password):
        raise ValueError("Invalid email or password")
    data={
    "sub": str(user.id),
    "email": user.email,
    "role": user.role
    }
    token=create_access_token(data=data)
    return {"access_token":token,"token_type":"bearer"}



