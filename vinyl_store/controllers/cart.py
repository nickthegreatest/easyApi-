"""РљРѕРЅС‚СЂРѕР»Р»РµСЂ РєРѕСЂР·РёРЅС‹."""

from flask import Blueprint, request, jsonify

from vinyl_store.models.cart import CartModel
from vinyl_store.models.product import ProductModel
from easyApi import token_required

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/")
@token_required
def get_cart(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ РєРѕСЂР·РёРЅСѓ С‚РµРєСѓС‰РµРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
    cart = CartModel.get_full_cart(current_user["id"])
    return jsonify(cart)


@cart_bp.route("/add", methods=["POST"])
@token_required
def add_to_cart(current_user):
    """Р”РѕР±Р°РІРёС‚СЊ С‚РѕРІР°СЂ РІ РєРѕСЂР·РёРЅСѓ."""
    data = request.get_json()

    product_id = data.get("product_id")
    quantity = max(1, int(data.get("quantity", 1)))

    if not product_id:
        return jsonify({"error": "product_id РѕР±СЏР·Р°С‚РµР»РµРЅ"}), 400

    # РџСЂРѕРІРµСЂСЏРµРј С‚РѕРІР°СЂ
    product = ProductModel.get_by_id(product_id)
    if not product:
        return jsonify({"error": "РўРѕРІР°СЂ РЅРµ РЅР°Р№РґРµРЅ"}), 404

    # РџСЂРѕРІРµСЂСЏРµРј РЅР°Р»РёС‡РёРµ
    if product["stock_quantity"] < quantity:
        return jsonify({"error": "РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ С‚РѕРІР°СЂР° РЅР° СЃРєР»Р°РґРµ"}), 400

    # Р”РѕР±Р°РІР»СЏРµРј РІ РєРѕСЂР·РёРЅСѓ
    result = CartModel.add_item(current_user["id"], product_id, quantity)

    cart = CartModel.get_full_cart(current_user["id"])
    return jsonify({
        "message": "РўРѕРІР°СЂ РґРѕР±Р°РІР»РµРЅ РІ РєРѕСЂР·РёРЅСѓ",
        "cart": cart,
    })


@cart_bp.route("/update", methods=["POST"])
@token_required
def update_cart(current_user):
    """РћР±РЅРѕРІРёС‚СЊ РєРѕР»РёС‡РµСЃС‚РІРѕ С‚РѕРІР°СЂР° РІ РєРѕСЂР·РёРЅРµ."""
    data = request.get_json()

    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id:
        return jsonify({"error": "product_id РѕР±СЏР·Р°С‚РµР»РµРЅ"}), 400

    if quantity < 0:
        return jsonify({"error": "quantity РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ >= 0"}), 400

    # РџСЂРѕРІРµСЂСЏРµРј С‚РѕРІР°СЂ
    product = ProductModel.get_by_id(product_id)
    if not product:
        return jsonify({"error": "РўРѕРІР°СЂ РЅРµ РЅР°Р№РґРµРЅ"}), 404

    # РџСЂРѕРІРµСЂСЏРµРј РЅР°Р»РёС‡РёРµ
    if quantity > 0 and product["stock_quantity"] < quantity:
        return jsonify({"error": "РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ С‚РѕРІР°СЂР° РЅР° СЃРєР»Р°РґРµ"}), 400

    CartModel.update_quantity(current_user["id"], product_id, quantity)

    cart = CartModel.get_full_cart(current_user["id"])
    return jsonify({
        "message": "РљРѕСЂР·РёРЅР° РѕР±РЅРѕРІР»РµРЅР°",
        "cart": cart,
    })


@cart_bp.route("/remove", methods=["POST"])
@token_required
def remove_from_cart(current_user):
    """РЈРґР°Р»РёС‚СЊ С‚РѕРІР°СЂ РёР· РєРѕСЂР·РёРЅС‹."""
    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "product_id РѕР±СЏР·Р°С‚РµР»РµРЅ"}), 400

    CartModel.remove_item(current_user["id"], product_id)

    cart = CartModel.get_full_cart(current_user["id"])
    return jsonify({
        "message": "РўРѕРІР°СЂ СѓРґР°Р»С‘РЅ РёР· РєРѕСЂР·РёРЅС‹",
        "cart": cart,
    })


@cart_bp.route("/clear", methods=["POST"])
@token_required
def clear_cart(current_user):
    """РћС‡РёСЃС‚РёС‚СЊ РєРѕСЂР·РёРЅСѓ."""
    CartModel.clear(current_user["id"])
    return jsonify({"message": "РљРѕСЂР·РёРЅР° РѕС‡РёС‰РµРЅР°"})


@cart_bp.route("/count")
@token_required
def get_cart_count(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ РєРѕР»РёС‡РµСЃС‚РІРѕ С‚РѕРІР°СЂРѕРІ РІ РєРѕСЂР·РёРЅРµ."""
    total = CartModel.get_total(current_user["id"])
    return jsonify({
        "total_items": total["total_items"],
        "subtotal": total["subtotal"],
    })
