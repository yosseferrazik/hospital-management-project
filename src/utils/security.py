import hashlib
import base64
import os

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with a random salt"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return base64.b64encode(salt + key).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    try:
        data = base64.b64decode(hashed.encode())
        salt = data[:32]
        stored_key = data[32:]
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key == stored_key
    except:
        return False