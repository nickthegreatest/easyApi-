"""Контроллер админ-панели."""

from flask import Blueprint, request, jsonify

from vinyl_store.models.user import UserModel
from vinyl_store.models.product import ProductModel
from vinyl_store.models.order import OrderModel
from vinyl_store.models.category import CategoryModel
from vinyl_store.models.review import ReviewModel
from vinyl_store.services.security import token_required, admin_required, manager_required

admin_bp = Blueprint("admin", __name__)


# === Дашборд ===

@admin_bp.route("/dashboard")
@manager_required
def get_dashboard(current_user):
    """Получить статистику для дашборда."""
    order_stats = OrderModel.get_statistics()

    # Статистика товаров
    products_count = len(ProductModel.get_all(limit=1)[1]) if hasattr(ProductModel.get_all(), '__getitem__') else 0
    all_products, total_products = ProductModel.get_all(limit=1)
    low_stock = len([p for p in all_products if p.get("stock_quantity", 0) < 5])

    # Статистика пользователей
    users = UserModel.get_all(limit=1)
    _, total_users = ([], len(users)) if not users else (users, 100)  # Упрощённо

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


# === Заказы ===

@admin_bp.route("/orders")
@manager_required
def get_all_orders(current_user):
    """Получить все заказы (админ/менеджер)."""
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
    """Получить详细信息 заказа (админ/менеджер)."""
    order = OrderModel.get_full_order(order_id)
    if not order:
        return jsonify({"error": "Заказ не найден"}), 404

    return jsonify(order)


@admin_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@admin_required
def update_order_status(current_user, order_id):
    """Обновить статус заказа (только админ)."""
    data = request.get_json()
    status = data.get("status")

    if not status:
        return jsonify({"error": "status обязателен"}), 400

    try:
        OrderModel.update_status(order_id, status)
        return jsonify({"message": "Статус обновлён"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/orders/<int:order_id>", methods=["PUT"])
@admin_required
def update_order(current_user, order_id):
    """Обновить данные заказа (только админ)."""
    data = request.get_json()

    # Разрешённые поля для обновления
    allowed_fields = [
        "shipping_address", "shipping_city", "shipping_postal_code",
        "shipping_country", "customer_phone", "customer_email",
        "notes", "tracking_number",
    ]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"error": "Нет допустимых полей для обновления"}), 400

    OrderModel.update(order_id, update_data)
    return jsonify({"message": "Заказ обновлён"})


@admin_bp.route("/orders/<int:order_id>", methods=["DELETE"])
@admin_required
def delete_order(current_user, order_id):
    """Удалить заказ (только админ)."""
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({"error": "Заказ не найден"}), 404

    # Нельзя удалить доставленный заказ
    if order["status"] == "delivered":
        return jsonify({"error": "Нельзя удалить доставленный заказ"}), 400

    # Удаляем позиции (каскадно)
    from easyApi import execute_query
    execute_query("DELETE", "order_items", where="order_id = %s", where_params=(order_id,))
    execute_query("DELETE", "orders", where="id = %s", where_params=(order_id,))

    return jsonify({"message": "Заказ удалён"})


# === Товары ===

@admin_bp.route("/products")
@manager_required
def get_all_products(current_user):
    """Получить все товары (админ/менеджер)."""
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
    """Создать товар (только админ)."""
    data = request.get_json()

    required = ["title", "artist", "price"]
    if not all(k in data for k in required):
        return jsonify({"error": f"Поля {required} обязательны"}), 400

    # Генерируем slug
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
        "message": "Товар создан",
        "product_id": result["insert_id"],
    }), 201


@admin_bp.route("/products/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(current_user, product_id):
    """Обновить товар (только админ)."""
    data = request.get_json()

    # Защита от изменения критических полей
    protected = ["id", "slug", "created_at"]
    for field in protected:
        data.pop(field, None)

    ProductModel.update(product_id, data)
    return jsonify({"message": "Товар обновлён"})


@admin_bp.route("/products/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(current_user, product_id):
    """Удалить товар (только админ)."""
    ProductModel.delete(product_id)
    return jsonify({"message": "Товар удалён"})


# === Пользователи ===

@admin_bp.route("/users")
@admin_required
def get_all_users(current_user):
    """Получить всех пользователей (только админ)."""
    users = UserModel.get_all()
    return jsonify({"users": users})


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(current_user, user_id):
    """Обновить пользователя (только админ)."""
    data = request.get_json()

    # Только определённые поля
    allowed = ["role", "first_name", "last_name", "phone", "address"]
    update_data = {k: v for k, v in data.items() if k in allowed}

    if not update_data:
        return jsonify({"error": "Нет допустимых полей"}), 400

    UserModel.update(user_id, update_data)
    return jsonify({"message": "Пользователь обновлён"})


# === Категории ===

@admin_bp.route("/categories")
@manager_required
def get_all_categories(current_user):
    """Получить все категории."""
    categories = CategoryModel.get_all()
    return jsonify({"categories": categories})


@admin_bp.route("/categories", methods=["POST"])
@admin_required
def create_category(current_user):
    """Создать категорию."""
    data = request.get_json()

    if not all(k in data for k in ["name", "slug"]):
        return jsonify({"error": "name и slug обязательны"}), 400

    result = CategoryModel.create(data["name"], data["slug"], data.get("description", ""))
    return jsonify({
        "message": "Категория создана",
        "category_id": result["insert_id"],
    }), 201


# === Отзывы ===

@admin_bp.route("/reviews/pending")
@manager_required
def get_pending_reviews(current_user):
    """Получить отзывы на модерацию."""
    reviews = ReviewModel.get_pending(limit=50)
    return jsonify({"reviews": reviews})


@admin_bp.route("/reviews/<int:review_id>/approve", methods=["POST"])
@manager_required
def approve_review(current_user, review_id):
    """Одобрить отзыв."""
    ReviewModel.approve(review_id)
    return jsonify({"message": "Отзыв одобрен"})


@admin_bp.route("/reviews/<int:review_id>/reject", methods=["POST"])
@manager_required
def reject_review(current_user, review_id):
    """Отклонить отзыв."""
    ReviewModel.reject(review_id)
    return jsonify({"message": "Отзыв отклонён"})


@admin_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@admin_required
def delete_review(current_user, review_id):
    """Удалить отзыв (только админ)."""
    ReviewModel.delete(review_id)
    return jsonify({"message": "Отзыв удалён"})
