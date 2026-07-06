from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta,UTC
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(UTC)+timedelta(minutes=60)
    to_encode.update({"exp":expire})
    jwt_encode=jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return jwt_encode
