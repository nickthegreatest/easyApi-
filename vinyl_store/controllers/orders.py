"""РљРѕРЅС‚СЂРѕР»Р»РµСЂ Р·Р°РєР°Р·РѕРІ."""

import random
from datetime import datetime

from flask import Blueprint, request, jsonify

from vinyl_store.models.cart import CartModel
from vinyl_store.models.order import OrderModel
from vinyl_store.models.product import ProductModel
from easyApi import token_required

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/")
@token_required
def get_orders(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ Р·Р°РєР°Р·С‹ С‚РµРєСѓС‰РµРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    orders = OrderModel.get_by_user(current_user["id"], limit=per_page, offset=offset)

    # Р”РѕР±Р°РІР»СЏРµРј РєРѕР»РёС‡РµСЃС‚РІРѕ С‚РѕРІР°СЂРѕРІ РІ РєР°Р¶РґС‹Р№ Р·Р°РєР°Р·
    for order in orders:
        items = OrderModel.get_items(order["id"])
        order["items_count"] = sum(item["quantity"] for item in items)

    return jsonify({
        "orders": orders,
        "pagination": {
            "page": page,
            "per_page": per_page,
        },
    })


@orders_bp.route("/<int:order_id>")
@token_required
def get_order(current_user, order_id):
    """РџРѕР»СѓС‡РёС‚СЊиЇ¦з»†дїЎжЃЇ Р·Р°РєР°Р·Р°."""
    order = OrderModel.get_full_order(order_id)
    if not order:
        return jsonify({"error": "Р—Р°РєР°Р· РЅРµ РЅР°Р№РґРµРЅ"}), 404

    # РџСЂРѕРІРµСЂРєР° РґРѕСЃС‚СѓРїР°
    if order["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ"}), 403

    return jsonify(order)


@orders_bp.route("/create", methods=["POST"])
@token_required
def create_order(current_user):
    """РЎРѕР·РґР°С‚СЊ Р·Р°РєР°Р· РёР· РєРѕСЂР·РёРЅС‹."""
    data = request.get_json() or {}

    # РџРѕР»СѓС‡Р°РµРј РєРѕСЂР·РёРЅСѓ
    cart_items = CartModel.get_items(current_user["id"])
    if not cart_items:
        return jsonify({"error": "РљРѕСЂР·РёРЅР° РїСѓСЃС‚Р°"}), 400

    # РџСЂРѕРІРµСЂСЏРµРј РЅР°Р»РёС‡РёРµ РІСЃРµС… С‚РѕРІР°СЂРѕРІ
    for item in cart_items:
        if item["stock_quantity"] < item["quantity"]:
            return jsonify({
                "error": f"РўРѕРІР°СЂ '{item['title']}' РЅРµРґРѕСЃС‚СѓРїРµРЅ РІ РЅСѓР¶РЅРѕРј РєРѕР»РёС‡РµСЃС‚РІРµ",
            }), 400

    # Р”Р°РЅРЅС‹Рµ РґРѕСЃС‚Р°РІРєРё
    shipping_data = {
        "address": data.get("address", "") or current_user.get("address", ""),
        "city": data.get("city", ""),
        "postal_code": data.get("postal_code", ""),
        "country": data.get("country", "Russia"),
        "phone": data.get("phone", "") or current_user.get("phone", ""),
        "email": data.get("email", "") or current_user.get("email", ""),
        "notes": data.get("notes", ""),
    }

    # Р’Р°Р»РёРґР°С†РёСЏ РѕР±СЏР·Р°С‚РµР»СЊРЅС‹С… РїРѕР»РµР№
    if not shipping_data["address"]:
        return jsonify({"error": "РђРґСЂРµСЃ РґРѕСЃС‚Р°РІРєРё РѕР±СЏР·Р°С‚РµР»РµРЅ"}), 400
    if not shipping_data["city"]:
        return jsonify({"error": "Р“РѕСЂРѕРґ РѕР±СЏР·Р°С‚РµР»РµРЅ"}), 400
    if not shipping_data["phone"]:
        return jsonify({"error": "РўРµР»РµС„РѕРЅ РѕР±СЏР·Р°С‚РµР»РµРЅ"}), 400

    payment_method = data.get("payment_method", "card")
    if payment_method not in ["card", "cash", "online"]:
        payment_method = "card"

    try:
        # РЎРѕР·РґР°С‘Рј Р·Р°РєР°Р· СЃ С‚СЂР°РЅР·Р°РєС†РёРµР№
        result = OrderModel.create_order_with_items(
            user_id=current_user["id"],
            cart_items=cart_items,
            shipping_data=shipping_data,
            payment_method=payment_method,
        )

        # РћС‡РёС‰Р°РµРј РєРѕСЂР·РёРЅСѓ
        CartModel.clear(current_user["id"])

        return jsonify({
            "message": "Р—Р°РєР°Р· СѓСЃРїРµС€РЅРѕ СЃРѕР·РґР°РЅ",
            "order": result,
        }), 201

    except Exception as e:
        return jsonify({"error": f"РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ Р·Р°РєР°Р·Р°: {str(e)}"}), 500


@orders_bp.route("/<int:order_id>/pay", methods=["POST"])
@token_required
def pay_order(current_user, order_id):
    """
    РћРїР»Р°С‚РёС‚СЊ Р·Р°РєР°Р· (С„РµР№РєРѕРІР°СЏ РѕРїР»Р°С‚Р°).
    РЎРёРјСѓР»РёСЂСѓРµС‚ РїСЂРѕС†РµСЃСЃ РѕРїР»Р°С‚С‹ СЃ РІРµСЂРѕСЏС‚РЅРѕСЃС‚СЊСЋ СѓСЃРїРµС…Р° 95%.
    """
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({"error": "Р—Р°РєР°Р· РЅРµ РЅР°Р№РґРµРЅ"}), 404

    # РџСЂРѕРІРµСЂРєР° РґРѕСЃС‚СѓРїР°
    if order["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ"}), 403

    # РџСЂРѕРІРµСЂРєР° СЃС‚Р°С‚СѓСЃР°
    if order["payment_status"] == "paid":
        return jsonify({"error": "Р—Р°РєР°Р· СѓР¶Рµ РѕРїР»Р°С‡РµРЅ"}), 400
    if order["status"] in ["cancelled", "delivered"]:
        return jsonify({"error": "РќРµР»СЊР·СЏ РѕРїР»Р°С‚РёС‚СЊ СЌС‚РѕС‚ Р·Р°РєР°Р·"}), 400

    # Р¤РµР№РєРѕРІР°СЏ РѕРїР»Р°С‚Р°
    payment_success = random.random() < 0.95  # 95% СѓСЃРїРµС…Р°

    if payment_success:
        OrderModel.update_payment_status(order_id, "paid")
        OrderModel.update_status(order_id, "confirmed")

        return jsonify({
            "message": "РћРїР»Р°С‚Р° СѓСЃРїРµС€РЅР°",
            "payment_status": "paid",
            "order_status": "confirmed",
        })
    else:
        OrderModel.update_payment_status(order_id, "failed")
        return jsonify({
            "error": "РџР»Р°С‚С‘Р¶ РЅРµ РїСЂРѕС€С‘Р». РџРѕРїСЂРѕР±СѓР№С‚Рµ РµС‰С‘ СЂР°Р·.",
            "payment_status": "failed",
        }), 400


@orders_bp.route("/<int:order_id>/cancel", methods=["POST"])
@token_required
def cancel_order(current_user, order_id):
    """РћС‚РјРµРЅРёС‚СЊ Р·Р°РєР°Р·."""
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({"error": "Р—Р°РєР°Р· РЅРµ РЅР°Р№РґРµРЅ"}), 404

    # РџСЂРѕРІРµСЂРєР° РґРѕСЃС‚СѓРїР°
    if order["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ"}), 403

    # РњРѕР¶РЅРѕ РѕС‚РјРµРЅРёС‚СЊ С‚РѕР»СЊРєРѕ pending/confirmed
    if order["status"] not in ["pending", "confirmed"]:
        return jsonify({"error": "РќРµР»СЊР·СЏ РѕС‚РјРµРЅРёС‚СЊ СЌС‚РѕС‚ Р·Р°РєР°Р·"}), 400

    OrderModel.cancel(order_id)

    return jsonify({"message": "Р—Р°РєР°Р· РѕС‚РјРµРЅС‘РЅ"})


@orders_bp.route("/<int:order_id>/invoice")
@token_required
def get_invoice(current_user, order_id):
    """РџРѕР»СѓС‡РёС‚СЊ СЃС‡С‘С‚/С‡РµРє Р·Р°РєР°Р·Р°."""
    order = OrderModel.get_full_order(order_id)
    if not order:
        return jsonify({"error": "Р—Р°РєР°Р· РЅРµ РЅР°Р№РґРµРЅ"}), 404

    # РџСЂРѕРІРµСЂРєР° РґРѕСЃС‚СѓРїР°
    if order["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ"}), 403

    return jsonify({
        "invoice": {
            "order_number": order["order_number"],
            "created_at": str(order["created_at"]),
            "customer": {
                "name": f"{order.get('customer_email', '')}",
                "email": order.get("customer_email", ""),
                "phone": order.get("customer_phone", ""),
            },
            "shipping": {
                "address": order["shipping_address"],
                "city": order["shipping_city"],
                "postal_code": order["shipping_postal_code"],
                "country": order["shipping_country"],
            },
            "items": order["items"],
            "totals": {
                "subtotal": sum(item["subtotal"] for item in order["items"]),
                "discount": order.get("discount_amount", 0),
                "shipping": order.get("shipping_cost", 0),
                "total": order["total_amount"],
            },
            "payment": {
                "method": order["payment_method"],
                "status": order["payment_status"],
            },
        },
    })
