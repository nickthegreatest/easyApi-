"""HTTP controllers for authentication and profile endpoints."""

from __future__ import annotations

from flask import Blueprint, g, request

from vinyl_store.middleware import jwt_required, success
from vinyl_store.services import auth_service
from vinyl_store.validators.auth import validate_login, validate_register

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    payload = validate_register(request.get_json(silent=True))
    return success(auth_service.register_user(payload), message="User registered", status=201)


@auth_bp.post("/login")
def login():
    payload = validate_login(request.get_json(silent=True))
    return success(auth_service.login_user(payload), message="Login successful")


@auth_bp.get("/profile")
@jwt_required
def profile():
    return success(auth_service.get_profile(g.current_user["id"]))
