from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    user, error = register_user(
        data["username"], data["password"], data["staff_id"], data["role"]
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "User registered", "user_id": user.user_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    token, error = login_user(data["username"], data["password"])
    if error:
        return jsonify({"error": error}), 401
    return jsonify({"access_token": token}), 200
