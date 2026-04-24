import bcrypt
from app.models import db, AppUser, Staff
from app.utils.encryption import save_credentials_to_file, verify_credentials_from_file
from flask_jwt_extended import create_access_token


def register_user(username, password, staff_id, role):
    if AppUser.query.filter_by(username=username).first():
        return None, "Username already exists"
    staff = Staff.query.get(staff_id)
    if not staff:
        return None, "Staff not found"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = AppUser(
        username=username, password_hash=hashed, staff_id=staff_id, role=role
    )
    db.session.add(user)
    db.session.commit()
    save_credentials_to_file(username, hashed)
    return user, None


def login_user(username, password):
    user = AppUser.query.filter_by(username=username).first()
    if not user:
        return None, "Invalid credentials"
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None, "Invalid credentials"
    if not verify_credentials_from_file(username, user.password_hash):
        return None, "File verification failed"
    token = create_access_token(
        identity=str(user.user_id), additional_claims={"role": user.role}
    )
    user.last_login = db.func.now()
    db.session.commit()
    return token, None
