"""Authentication routes — register, login, password management, user admin."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.services.auth_service import register_user, login_user, change_password, admin_set_password, admin_toggle_active
from app.models import AppUser

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# --- POST /api/auth/register — create a new app user ---
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    username = data.get("username")
    password = data.get("password")
    staff_id = data.get("staff_id")
    role = data.get("role")
    if not username or not password or not staff_id or not role:
        return jsonify({"error": "Missing required fields"}), 400
    try:
        user, error = register_user(username, password, staff_id, role)
        if error:
            return jsonify({"error": error}), 400
        return jsonify({"message": "User registered", "user_id": user.user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --- GET /api/auth/users — list all registered users (admin) ---
@auth_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    users = AppUser.query.order_by(AppUser.user_id).all()
    return jsonify({
        "users": [
            {
                "user_id": u.user_id,
                "username": u.username,
                "role": u.role,
                "staff_id": u.staff_id,
                "is_active": u.is_active,
            }
            for u in users
        ]
    }), 200


# --- POST /api/auth/login — authenticate and return JWT ---
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    try:
        token, role, staff_id, error = login_user(username, password)
        if error:
            return jsonify({"error": error}), 401
        return jsonify({"access_token": token, "role": role, "staff_id": staff_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --- PUT /api/auth/change-password — current user changes own password ---
@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def self_change_password():
    claims = get_jwt()
    user_id = int(claims.get("sub", 0))
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    old = data.get("old_password")
    new = data.get("new_password")
    if not old or not new:
        return jsonify({"error": "old_password and new_password are required"}), 400
    error = change_password(user_id, old, new)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Password changed successfully"}), 200


# --- PUT /api/auth/users/<id>/password — admin resets another user's password ---
@auth_bp.route("/users/<int:user_id>/password", methods=["PUT"])
@jwt_required()
def admin_reset_password(user_id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"error": "Admin access required"}), 403
    data = request.get_json()
    if not data or not data.get("new_password"):
        return jsonify({"error": "new_password is required"}), 400
    error = admin_set_password(user_id, data["new_password"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Password updated"}), 200


# --- PUT /api/auth/users/<id>/toggle-active — enable or disable a user ---
@auth_bp.route("/users/<int:user_id>/toggle-active", methods=["PUT"])
@jwt_required()
def toggle_active(user_id):
    claims = get_jwt()
    if claims.get("role") != "ADMIN":
        return jsonify({"error": "Admin access required"}), 403
    error, is_active = admin_toggle_active(user_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Account status toggled", "is_active": is_active}), 200
