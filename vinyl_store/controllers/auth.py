"""РљРѕРЅС‚СЂРѕР»Р»РµСЂ Р°СѓС‚РµРЅС‚РёС„РёРєР°С†РёРё."""

from flask import Blueprint, request, jsonify, session

from easyApi import generate_token
from vinyl_store.models.user import UserModel
from easyApi import token_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Р РµРіРёСЃС‚СЂР°С†РёСЏ РЅРѕРІРѕРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()

    # Р’Р°Р»РёРґР°С†РёСЏ
    errors = []
    if len(username) < 3:
        errors.append("username РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РЅРµ РјРµРЅРµРµ 3 СЃРёРјРІРѕР»РѕРІ")
    if len(username) > 50:
        errors.append("username РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РЅРµ Р±РѕР»РµРµ 50 СЃРёРјРІРѕР»РѕРІ")
    if "@" not in email or len(email) > 100:
        errors.append("РќРµРєРѕСЂСЂРµРєС‚РЅС‹Р№ email")
    if len(password) < 6:
        errors.append("РџР°СЂРѕР»СЊ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РЅРµ РјРµРЅРµРµ 6 СЃРёРјРІРѕР»РѕРІ")

    if errors:
        return jsonify({"errors": errors}), 400

    # РџСЂРѕРІРµСЂРєР° РЅР° РґСѓР±Р»РёРєР°С‚
    if UserModel.get_by_username(username):
        return jsonify({"error": "username СѓР¶Рµ Р·Р°РЅСЏС‚"}), 409
    if UserModel.get_by_email(email):
        return jsonify({"error": "email СѓР¶Рµ Р·Р°СЂРµРіРёСЃС‚СЂРёСЂРѕРІР°РЅ"}), 409

    # РЎРѕР·РґР°РЅРёРµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
    result = UserModel.create(username, email, password, first_name, last_name)

    # Р“РµРЅРµСЂР°С†РёСЏ С‚РѕРєРµРЅР°
    token = generate_token({
        "id": result["insert_id"],
        "username": username,
        "role": "user",
    })

    return jsonify({
        "message": "РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ Р·Р°СЂРµРіРёСЃС‚СЂРёСЂРѕРІР°РЅ",
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
    """Р’С…РѕРґ РІ СЃРёСЃС‚РµРјСѓ."""
    data = request.get_json(silent=True) or {}

    username_or_email = data.get("username", "").strip()
    password = data.get("password", "")

    if not username_or_email or not password:
        return jsonify({"error": "username/email Рё РїР°СЂРѕР»СЊ РѕР±СЏР·Р°С‚РµР»СЊРЅС‹"}), 400

    # РџРѕРёСЃРє РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
    user = UserModel.get_by_username(username_or_email)
    if not user:
        user = UserModel.get_by_email(username_or_email)

    if not user or not UserModel.check_password(user["id"], password):
        return jsonify({"error": "РќРµРІРµСЂРЅС‹Рµ СѓС‡С‘С‚РЅС‹Рµ РґР°РЅРЅС‹Рµ"}), 401

    # Р“РµРЅРµСЂР°С†РёСЏ С‚РѕРєРµРЅР°
    token = generate_token({
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
    })

    return jsonify({
        "message": "РЈСЃРїРµС€РЅС‹Р№ РІС…РѕРґ",
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
    """РџРѕР»СѓС‡РёС‚СЊ РґР°РЅРЅС‹Рµ С‚РµРєСѓС‰РµРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
    user = UserModel.get_by_id(current_user["id"])
    if not user:
        return jsonify({"error": "РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ"}), 404

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
    """РћР±РЅРѕРІРёС‚СЊ РїСЂРѕС„РёР»СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
    data = request.get_json()

    allowed_fields = ["first_name", "last_name", "phone", "address"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"error": "РќРµС‚ РґР°РЅРЅС‹С… РґР»СЏ РѕР±РЅРѕРІР»РµРЅРёСЏ"}), 400

    UserModel.update(current_user["id"], update_data)

    return jsonify({"message": "РџСЂРѕС„РёР»СЊ РѕР±РЅРѕРІР»С‘РЅ"})


@auth_bp.route("/change-password", methods=["POST"])
@token_required
def change_password(current_user):
    """РЎРјРµРЅРёС‚СЊ РїР°СЂРѕР»СЊ."""
    data = request.get_json()

    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"error": "old_password Рё new_password РѕР±СЏР·Р°С‚РµР»СЊРЅС‹"}), 400

    if not UserModel.check_password(current_user["id"], old_password):
        return jsonify({"error": "РќРµРІРµСЂРЅС‹Р№ С‚РµРєСѓС‰РёР№ РїР°СЂРѕР»СЊ"}), 401

    if len(new_password) < 6:
        return jsonify({"error": "РќРѕРІС‹Р№ РїР°СЂРѕР»СЊ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РЅРµ РјРµРЅРµРµ 6 СЃРёРјРІРѕР»РѕРІ"}), 400

    UserModel.change_password(current_user["id"], new_password)

    return jsonify({"message": "РџР°СЂРѕР»СЊ РёР·РјРµРЅС‘РЅ"})
