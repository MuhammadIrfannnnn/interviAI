from app.core.security import hash_password, verify_password
password = "mysec"
hashed_password = hash_password(password)
is_valid = verify_password(password, hashed_password)
print(f"Password: {password}")
print(f"Hashed Password: {hashed_password}")
print(f"Is Valid: {is_valid}")