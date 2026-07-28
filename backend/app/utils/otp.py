import random
import hashlib
from datetime import datetime, timedelta

OTP_EXPIRY_MINUTES = 10

def generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"

def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()

def verify_otp_hash(otp: str, otp_hash: str) -> bool:
    return hash_otp(otp) == otp_hash

def get_otp_expiry():
    return datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

def can_send_new_otp(last_sent_at):
    if last_sent_at is None:
        return True
    elapsed = (datetime.utcnow() - last_sent_at).total_seconds()
    return elapsed >= 60