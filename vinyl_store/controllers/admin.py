"""РљРѕРЅС‚СЂРѕР»Р»РµСЂ Р°РґРјРёРЅ-РїР°РЅРµР»Рё."""

from flask import Blueprint, request, jsonify

from vinyl_store.models.user import UserModel
from vinyl_store.models.product import ProductModel
from vinyl_store.models.order import OrderModel
from vinyl_store.models.category import CategoryModel
from vinyl_store.models.review import ReviewModel
from easyApi import token_required, admin_required, manager_required

admin_bp = Blueprint("admin", __name__)


# === Р”Р°С€Р±РѕСЂРґ ===

@admin_bp.route("/dashboard")
@manager_required
def get_dashboard(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ СЃС‚Р°С‚РёСЃС‚РёРєСѓ РґР»СЏ РґР°С€Р±РѕСЂРґР°."""
    order_stats = OrderModel.get_statistics()

    # РЎС‚Р°С‚РёСЃС‚РёРєР° С‚РѕРІР°СЂРѕРІ
    products_count = len(ProductModel.get_all(limit=1)[1]) if hasattr(ProductModel.get_all(), '__getitem__') else 0
    all_products, total_products = ProductModel.get_all(limit=1)
    low_stock = len([p for p in all_products if p.get("stock_quantity", 0) < 5])

    # РЎС‚Р°С‚РёСЃС‚РёРєР° РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№
    users = UserModel.get_all(limit=1)
    _, total_users = ([], len(users)) if not users else (users, 100)  # РЈРїСЂРѕС‰С‘РЅРЅРѕ

    return jsonify({
        "orders": order_stats,
        "products": {
            "total": total_products,
            "low_stock": low_stock,
        },
        "users": {
            "total": total_users,
        },
    })


# === Р—Р°РєР°Р·С‹ ===

@admin_bp.route("/orders")
@manager_required
def get_all_orders(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµ Р·Р°РєР°Р·С‹ (Р°РґРјРёРЅ/РјРµРЅРµРґР¶РµСЂ)."""
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    status = request.args.get("status")
    payment_status = request.args.get("payment_status")
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "DESC")

    orders, total = OrderModel.get_all(
        status=status,
        payment_status=payment_status,
        limit=per_page,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return jsonify({
        "orders": orders,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    })


@admin_bp.route("/orders/<int:order_id>")
@manager_required
def get_order_admin(current_user, order_id):
    """РџРѕР»СѓС‡РёС‚СЊиЇ¦з»†дїЎжЃЇ Р·Р°РєР°Р·Р° (Р°РґРјРёРЅ/РјРµРЅРµРґР¶РµСЂ)."""
    order = OrderModel.get_full_order(order_id)
    if not order:
        return jsonify({"error": "Р—Р°РєР°Р· РЅРµ РЅР°Р№РґРµРЅ"}), 404

    return jsonify(order)


@admin_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@admin_required
def update_order_status(current_user, order_id):
    """РћР±РЅРѕРІРёС‚СЊ СЃС‚Р°С‚СѓСЃ Р·Р°РєР°Р·Р° (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    data = request.get_json()
    status = data.get("status")

    if not status:
        return jsonify({"error": "status РѕР±СЏР·Р°С‚РµР»РµРЅ"}), 400

    try:
        OrderModel.update_status(order_id, status)
        return jsonify({"message": "РЎС‚Р°С‚СѓСЃ РѕР±РЅРѕРІР»С‘РЅ"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/orders/<int:order_id>", methods=["PUT"])
@admin_required
def update_order(current_user, order_id):
    """РћР±РЅРѕРІРёС‚СЊ РґР°РЅРЅС‹Рµ Р·Р°РєР°Р·Р° (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    data = request.get_json()

    # Р Р°Р·СЂРµС€С‘РЅРЅС‹Рµ РїРѕР»СЏ РґР»СЏ РѕР±РЅРѕРІР»РµРЅРёСЏ
    allowed_fields = [
        "shipping_address", "shipping_city", "shipping_postal_code",
        "shipping_country", "customer_phone", "customer_email",
        "notes", "tracking_number",
    ]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"error": "РќРµС‚ РґРѕРїСѓСЃС‚РёРјС‹С… РїРѕР»РµР№ РґР»СЏ РѕР±РЅРѕРІР»РµРЅРёСЏ"}), 400

    OrderModel.update(order_id, update_data)
    return jsonify({"message": "Р—Р°РєР°Р· РѕР±РЅРѕРІР»С‘РЅ"})


@admin_bp.route("/orders/<int:order_id>", methods=["DELETE"])
@admin_required
def delete_order(current_user, order_id):
    """РЈРґР°Р»РёС‚СЊ Р·Р°РєР°Р· (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({"error": "Р—Р°РєР°Р· РЅРµ РЅР°Р№РґРµРЅ"}), 404

    # РќРµР»СЊР·СЏ СѓРґР°Р»РёС‚СЊ РґРѕСЃС‚Р°РІР»РµРЅРЅС‹Р№ Р·Р°РєР°Р·
    if order["status"] == "delivered":
        return jsonify({"error": "РќРµР»СЊР·СЏ СѓРґР°Р»РёС‚СЊ РґРѕСЃС‚Р°РІР»РµРЅРЅС‹Р№ Р·Р°РєР°Р·"}), 400

    # РЈРґР°Р»СЏРµРј РїРѕР·РёС†РёРё (РєР°СЃРєР°РґРЅРѕ)
    from easyApi import execute_query
    execute_query("DELETE", "order_items", where="order_id = %s", where_params=(order_id,))
    execute_query("DELETE", "orders", where="id = %s", where_params=(order_id,))

    return jsonify({"message": "Р—Р°РєР°Р· СѓРґР°Р»С‘РЅ"})


# === РўРѕРІР°СЂС‹ ===

@admin_bp.route("/products")
@manager_required
def get_all_products(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµ С‚РѕРІР°СЂС‹ (Р°РґРјРёРЅ/РјРµРЅРµРґР¶РµСЂ)."""
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    products, total = ProductModel.get_all(limit=per_page, offset=offset)

    return jsonify({
        "products": products,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    })


@admin_bp.route("/products", methods=["POST"])
@admin_required
def create_product(current_user):
    """РЎРѕР·РґР°С‚СЊ С‚РѕРІР°СЂ (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    data = request.get_json()

    required = ["title", "artist", "price"]
    if not all(k in data for k in required):
        return jsonify({"error": f"РџРѕР»СЏ {required} РѕР±СЏР·Р°С‚РµР»СЊРЅС‹"}), 400

    # Р“РµРЅРµСЂРёСЂСѓРµРј slug
    slug = data.get("slug", data["title"].lower().replace(" ", "-"))

    product_data = {
        "title": data["title"],
        "artist": data["artist"],
        "slug": slug,
        "price": float(data["price"]),
        "description": data.get("description", ""),
        "stock_quantity": int(data.get("stock_quantity", 0)),
        "category_id": data.get("category_id"),
        "label_id": data.get("label_id"),
        "release_year": data.get("release_year"),
        "format": data.get("format", "LP"),
        "image_url": data.get("image_url", ""),
        "is_new": data.get("is_new", False),
        "is_limited": data.get("is_limited", False),
    }

    result = ProductModel.create(product_data)
    return jsonify({
        "message": "РўРѕРІР°СЂ СЃРѕР·РґР°РЅ",
        "product_id": result["insert_id"],
    }), 201


@admin_bp.route("/products/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(current_user, product_id):
    """РћР±РЅРѕРІРёС‚СЊ С‚РѕРІР°СЂ (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    data = request.get_json()

    # Р—Р°С‰РёС‚Р° РѕС‚ РёР·РјРµРЅРµРЅРёСЏ РєСЂРёС‚РёС‡РµСЃРєРёС… РїРѕР»РµР№
    protected = ["id", "slug", "created_at"]
    for field in protected:
        data.pop(field, None)

    ProductModel.update(product_id, data)
    return jsonify({"message": "РўРѕРІР°СЂ РѕР±РЅРѕРІР»С‘РЅ"})


@admin_bp.route("/products/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(current_user, product_id):
    """РЈРґР°Р»РёС‚СЊ С‚РѕРІР°СЂ (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    ProductModel.delete(product_id)
    return jsonify({"message": "РўРѕРІР°СЂ СѓРґР°Р»С‘РЅ"})


# === РџРѕР»СЊР·РѕРІР°С‚РµР»Рё ===

@admin_bp.route("/users")
@admin_required
def get_all_users(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµС… РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№ (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    users = UserModel.get_all()
    return jsonify({"users": users})


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(current_user, user_id):
    """РћР±РЅРѕРІРёС‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    data = request.get_json()

    # РўРѕР»СЊРєРѕ РѕРїСЂРµРґРµР»С‘РЅРЅС‹Рµ РїРѕР»СЏ
    allowed = ["role", "first_name", "last_name", "phone", "address"]
    update_data = {k: v for k, v in data.items() if k in allowed}

    if not update_data:
        return jsonify({"error": "РќРµС‚ РґРѕРїСѓСЃС‚РёРјС‹С… РїРѕР»РµР№"}), 400

    UserModel.update(user_id, update_data)
    return jsonify({"message": "РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РѕР±РЅРѕРІР»С‘РЅ"})


# === РљР°С‚РµРіРѕСЂРёРё ===

@admin_bp.route("/categories")
@manager_required
def get_all_categories(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµ РєР°С‚РµРіРѕСЂРёРё."""
    categories = CategoryModel.get_all()
    return jsonify({"categories": categories})


@admin_bp.route("/categories", methods=["POST"])
@admin_required
def create_category(current_user):
    """РЎРѕР·РґР°С‚СЊ РєР°С‚РµРіРѕСЂРёСЋ."""
    data = request.get_json()

    if not all(k in data for k in ["name", "slug"]):
        return jsonify({"error": "name Рё slug РѕР±СЏР·Р°С‚РµР»СЊРЅС‹"}), 400

    result = CategoryModel.create(data["name"], data["slug"], data.get("description", ""))
    return jsonify({
        "message": "РљР°С‚РµРіРѕСЂРёСЏ СЃРѕР·РґР°РЅР°",
        "category_id": result["insert_id"],
    }), 201


# === РћС‚Р·С‹РІС‹ ===

@admin_bp.route("/reviews/pending")
@manager_required
def get_pending_reviews(current_user):
    """РџРѕР»СѓС‡РёС‚СЊ РѕС‚Р·С‹РІС‹ РЅР° РјРѕРґРµСЂР°С†РёСЋ."""
    reviews = ReviewModel.get_pending(limit=50)
    return jsonify({"reviews": reviews})


@admin_bp.route("/reviews/<int:review_id>/approve", methods=["POST"])
@manager_required
def approve_review(current_user, review_id):
    """РћРґРѕР±СЂРёС‚СЊ РѕС‚Р·С‹РІ."""
    ReviewModel.approve(review_id)
    return jsonify({"message": "РћС‚Р·С‹РІ РѕРґРѕР±СЂРµРЅ"})


@admin_bp.route("/reviews/<int:review_id>/reject", methods=["POST"])
@manager_required
def reject_review(current_user, review_id):
    """РћС‚РєР»РѕРЅРёС‚СЊ РѕС‚Р·С‹РІ."""
    ReviewModel.reject(review_id)
    return jsonify({"message": "РћС‚Р·С‹РІ РѕС‚РєР»РѕРЅС‘РЅ"})


@admin_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@admin_required
def delete_review(current_user, review_id):
    """РЈРґР°Р»РёС‚СЊ РѕС‚Р·С‹РІ (С‚РѕР»СЊРєРѕ Р°РґРјРёРЅ)."""
    ReviewModel.delete(review_id)
    return jsonify({"message": "РћС‚Р·С‹РІ СѓРґР°Р»С‘РЅ"})
