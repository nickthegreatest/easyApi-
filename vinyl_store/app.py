"""VinylVault вЂ” РёРЅС‚РµСЂРЅРµС‚-РјР°РіР°Р·РёРЅ РІРёРЅРёР»РѕРІС‹С… РїР»Р°СЃС‚РёРЅРѕРє."""

import os
import sys
from pathlib import Path

# Р”РѕР±Р°РІР»СЏРµРј С‚РµРєСѓС‰СѓСЋ РґРёСЂРµРєС‚РѕСЂРёСЋ РІ РїСѓС‚СЊ РґР»СЏ РёРјРїРѕСЂС‚Р° vinyl_store
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from easyApi import EasyApi

# Р—Р°РіСЂСѓР¶Р°РµРј РїРµСЂРµРјРµРЅРЅС‹Рµ РѕРєСЂСѓР¶РµРЅРёСЏ
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ РёР· ENV
app_config = {
    "DB_HOST": os.getenv("DB_HOST", "localhost"),
    "DB_USER": os.getenv("DB_USER", "root"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD", ""),
    "DB_NAME": os.getenv("DB_NAME", "vinyl_store"),
    "DB_PORT": int(os.getenv("DB_PORT", "3306")),
    "SECRET_KEY": os.getenv("SECRET_KEY", "vinyl-vault-secret-key-change-in-production"),
    "JWT_EXPIRATION_HOURS": int(os.getenv("JWT_EXPIRATION_HOURS", "72")),
}

# РЎРѕР·РґР°С‘Рј РїСЂРёР»РѕР¶РµРЅРёРµ
kit = EasyApi(config=app_config, name="vinyl_store")

# Р РµРіРёСЃС‚СЂРёСЂСѓРµРј РєРѕРЅС‚СЂРѕР»Р»РµСЂС‹
from vinyl_store.controllers import auth_bp, catalog_bp, cart_bp, orders_bp, admin_bp

kit.register_blueprint(auth_bp, url_prefix="/api/auth")
kit.register_blueprint(catalog_bp, url_prefix="/api")
kit.register_blueprint(cart_bp, url_prefix="/api/cart")
kit.register_blueprint(orders_bp, url_prefix="/api/orders")
kit.register_blueprint(admin_bp, url_prefix="/api/admin")


# Р Р°Р·РґР°С‡Р° СЃС‚Р°С‚РёРєРё Рё SPA
@kit.flask.route("/")
def index():
    """Р“Р»Р°РІРЅР°СЏ СЃС‚СЂР°РЅРёС†Р°."""
    return send_from_directory("templates", "index.html")


@kit.flask.route("/<path:path>")
def static_files(path):
    """Р Р°Р·РґР°С‡Р° СЃС‚Р°С‚РёРєРё."""
    if path.startswith("static/"):
        return send_from_directory("static", path)
    return send_from_directory("templates", "index.html")


if __name__ == "__main__":
    print("рџЋµ VinylVault вЂ” РёРЅС‚РµСЂРЅРµС‚-РјР°РіР°Р·РёРЅ РІРёРЅРёР»РѕРІС‹С… РїР»Р°СЃС‚РёРЅРѕРє")
    print("рџ“Ќ http://localhost:5000")
    print("рџ”§ API: http://localhost:5000/api/*")
    kit.run(debug=True, host="0.0.0.0", port=5000)
