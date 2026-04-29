from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


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

    user, error = register_user(username, password, staff_id, role)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User registered", "user_id": user.user_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    token, error = login_user(username, password)

    if error:
        return jsonify({"error": error}), 401

    return jsonify({"access_token": token}), 200
