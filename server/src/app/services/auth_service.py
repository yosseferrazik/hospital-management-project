from datetime import datetime, timezone

import bcrypt
from app.models import db, AppUser, Staff
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
    return user, None


def login_user(username, password):
    user = AppUser.query.filter_by(username=username).first()
    if not user:
        return None, "Invalid credentials"
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None, "Invalid credentials"
    token = create_access_token(
        identity=str(user.user_id), additional_claims={"role": user.role}
    )
    user.last_login = datetime.now(timezone.utc)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return token, None
