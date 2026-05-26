"""Authentication service — user registration, login, password management."""

from datetime import datetime, timezone

import bcrypt
from app.models import db, AppUser, Staff
from flask_jwt_extended import create_access_token
from sqlalchemy import text


def register_user(username, password, staff_id, role):
    """Create a new app user linked to an existing staff member."""
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
    """Authenticate a user and return a JWT token with role and staff_id claims."""
    if not user:
        return None, None, None, "Invalid credentials"
    if not user.is_active:
        return None, None, None, "Account is disabled"
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None, None, None, "Invalid credentials"
    token = create_access_token(
        identity=str(user.user_id), additional_claims={"role": user.role, "staff_id": user.staff_id}
    )
    user.last_login = datetime.now(timezone.utc)
    try:
        db.session.execute(text("SELECT set_config('app.current_user_id', :uid, true)"), {"uid": str(user.user_id)})
        db.session.execute(text("SELECT set_config('app.current_staff_id', :sid, true)"), {"sid": str(user.staff_id)})
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return token, user.role, user.staff_id, None


def change_password(user_id, old_password, new_password):
    """Verify old password and update to a new one for the current user."""
    if not user:
        return "User not found"
    if not bcrypt.checkpw(old_password.encode(), user.password_hash.encode()):
        return "Current password is incorrect"
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    user.password_hash = hashed
    db.session.commit()
    return None


def admin_set_password(user_id, new_password):
    """Admin forcibly sets a new password for any user (no old password check)."""
    if not user:
        return "User not found"
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    user.password_hash = hashed
    db.session.commit()
    return None


def admin_toggle_active(user_id):
    """Enable or disable a user account."""
    if not user:
        return "User not found", None
    user.is_active = not user.is_active
    db.session.commit()
    return None, user.is_active
