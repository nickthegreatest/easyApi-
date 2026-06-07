"""Контроллер аутентификации."""

from flask import Blueprint, request, jsonify, session

from easyApi import generate_token
from vinyl_store.models.user import UserModel
from vinyl_store.services.security import token_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Регистрация нового пользователя."""
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()

    # Валидация
    errors = []
    if len(username) < 3:
        errors.append("username должен быть не менее 3 символов")
    if len(username) > 50:
        errors.append("username должен быть не более 50 символов")
    if "@" not in email or len(email) > 100:
        errors.append("Некорректный email")
    if len(password) < 6:
        errors.append("Пароль должен быть не менее 6 символов")

    if errors:
        return jsonify({"errors": errors}), 400

    # Проверка на дубликат
    if UserModel.get_by_username(username):
        return jsonify({"error": "username уже занят"}), 409
    if UserModel.get_by_email(email):
        return jsonify({"error": "email уже зарегистрирован"}), 409

    # Создание пользователя
    result = UserModel.create(username, email, password, first_name, last_name)

    # Генерация токена
    token = generate_token({
        "id": result["insert_id"],
        "username": username,
        "role": "user",
    })

    return jsonify({
        "message": "Пользователь зарегистрирован",
        "user_id": result["insert_id"],
        "token": token,
        "user": {
            "id": result["insert_id"],
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        },
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Вход в систему."""
    data = request.get_json(silent=True) or {}

    username_or_email = data.get("username", "").strip()
    password = data.get("password", "")

    if not username_or_email or not password:
        return jsonify({"error": "username/email и пароль обязательны"}), 400

    # Поиск пользователя
    user = UserModel.get_by_username(username_or_email)
    if not user:
        user = UserModel.get_by_email(username_or_email)

    if not user or not UserModel.check_password(user["id"], password):
        return jsonify({"error": "Неверные учётные данные"}), 401

    # Генерация токена
    token = generate_token({
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
    })

    return jsonify({
        "message": "Успешный вход",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
        },
    }), 200


@auth_bp.route("/me")
@token_required
def get_current_user(current_user):
    """Получить данные текущего пользователя."""
    user = UserModel.get_by_id(current_user["id"])
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "phone": user.get("phone", ""),
        "address": user.get("address", ""),
        "created_at": str(user.get("created_at", "")),
    })


@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Обновить профиль пользователя."""
    data = request.get_json()

    allowed_fields = ["first_name", "last_name", "phone", "address"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"error": "Нет данных для обновления"}), 400

    UserModel.update(current_user["id"], update_data)

    return jsonify({"message": "Профиль обновлён"})


@auth_bp.route("/change-password", methods=["POST"])
@token_required
def change_password(current_user):
    """Сменить пароль."""
    data = request.get_json()

    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"error": "old_password и new_password обязательны"}), 400

    if not UserModel.check_password(current_user["id"], old_password):
        return jsonify({"error": "Неверный текущий пароль"}), 401

    if len(new_password) < 6:
        return jsonify({"error": "Новый пароль должен быть не менее 6 символов"}), 400

    UserModel.change_password(current_user["id"], new_password)

    return jsonify({"message": "Пароль изменён"})
