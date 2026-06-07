"""РљРѕРЅС‚СЂРѕР»Р»РµСЂ РєР°С‚Р°Р»РѕРіР°."""

from flask import Blueprint, request, jsonify

from vinyl_store.models.product import ProductModel
from vinyl_store.models.category import CategoryModel

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.route("/products")
def get_products():
    """
    РџРѕР»СѓС‡РёС‚СЊ СЃРїРёСЃРѕРє С‚РѕРІР°СЂРѕРІ СЃ С„РёР»СЊС‚СЂР°РјРё, СЃРѕСЂС‚РёСЂРѕРІРєРѕР№ Рё РїР°РіРёРЅР°С†РёРµР№.
    
    Query params:
        - page: РЅРѕРјРµСЂ СЃС‚СЂР°РЅРёС†С‹ (default: 1)
        - per_page: С‚РѕРІР°СЂРѕРІ РЅР° СЃС‚СЂР°РЅРёС†Рµ (default: 12)
        - category: ID РєР°С‚РµРіРѕСЂРёРё
        - label: ID Р»РµР№Р±Р»Р°
        - min_price: РјРёРЅРёРјР°Р»СЊРЅР°СЏ С†РµРЅР°
        - max_price: РјР°РєСЃРёРјР°Р»СЊРЅР°СЏ С†РµРЅР°
        - min_rating: РјРёРЅРёРјР°Р»СЊРЅС‹Р№ СЂРµР№С‚РёРЅРі
        - in_stock: С‚РѕР»СЊРєРѕ РІ РЅР°Р»РёС‡РёРё (1/0)
        - is_new: С‚РѕР»СЊРєРѕ РЅРѕРІРёРЅРєРё (1/0)
        - is_limited: С‚РѕР»СЊРєРѕ Р»РёРјРёС‚РёСЂРѕРІР°РЅРЅС‹Рµ (1/0)
        - search: РїРѕРёСЃРє РїРѕ РЅР°Р·РІР°РЅРёСЋ/Р°СЂС‚РёСЃС‚Сѓ
        - sort: РїРѕР»Рµ СЃРѕСЂС‚РёСЂРѕРІРєРё (price, rating, title, artist, release_year, created_at)
        - order: РїРѕСЂСЏРґРѕРє (asc, desc)
    """
    # РџР°РіРёРЅР°С†РёСЏ
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 12))))
    offset = (page - 1) * per_page

    # Р¤РёР»СЊС‚СЂС‹
    category_id = int(request.args.get("category", 0)) or None
    label_id = int(request.args.get("label", 0)) or None
    min_price = float(request.args.get("min_price", 0)) or None
    max_price = float(request.args.get("max_price", 0)) or None
    min_rating = float(request.args.get("min_rating", 0)) or None
    in_stock = request.args.get("in_stock") == "1"
    is_new = request.args.get("is_new") == "1"
    is_limited = request.args.get("is_limited") == "1"
    search = request.args.get("search", "").strip() or None

    # РЎРѕСЂС‚РёСЂРѕРІРєР°
    sort_by = request.args.get("sort", "created_at")
    sort_order = request.args.get("order", "DESC")

    products, total = ProductModel.get_all(
        limit=per_page,
        offset=offset,
        category_id=category_id,
        label_id=label_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock=in_stock,
        is_new=is_new,
        is_limited=is_limited,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return jsonify({
        "products": products,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
        "filters": {
            "category_id": category_id,
            "label_id": label_id,
            "min_price": min_price,
            "max_price": max_price,
            "min_rating": min_rating,
            "in_stock": in_stock,
            "is_new": is_new,
            "is_limited": is_limited,
            "search": search,
        },
    })


@catalog_bp.route("/products/<int:product_id>")
def get_product(product_id):
    """РџРѕР»СѓС‡РёС‚СЊиЇ¦з»†дїЎжЃЇ С‚РѕРІР°СЂР°."""
    product = ProductModel.get_by_id(product_id)
    if not product:
        return jsonify({"error": "РўРѕРІР°СЂ РЅРµ РЅР°Р№РґРµРЅ"}), 404

    # РџРѕР»СѓС‡Р°РµРј РѕС‚Р·С‹РІС‹
    from vinyl_store.models.review import ReviewModel
    reviews = ReviewModel.get_by_product(product_id, approved_only=True, limit=10)
    review_stats = ReviewModel.get_statistics(product_id)

    product["reviews"] = reviews
    product["review_stats"] = review_stats

    return jsonify(product)


@catalog_bp.route("/products/<slug>")
def get_product_by_slug(slug):
    """РџРѕР»СѓС‡РёС‚СЊ С‚РѕРІР°СЂ РїРѕ slug."""
    product = ProductModel.get_by_slug(slug)
    if not product:
        return jsonify({"error": "РўРѕРІР°СЂ РЅРµ РЅР°Р№РґРµРЅ"}), 404

    return jsonify(product)


@catalog_bp.route("/categories")
def get_categories():
    """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµ РєР°С‚РµРіРѕСЂРёРё."""
    categories = CategoryModel.get_with_counts()
    return jsonify({"categories": categories})


@catalog_bp.route("/categories/<int:category_id>/products")
def get_category_products(category_id):
    """РџРѕР»СѓС‡РёС‚СЊ С‚РѕРІР°СЂС‹ РєР°С‚РµРіРѕСЂРёРё."""
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 12))))
    offset = (page - 1) * per_page

    products, total = ProductModel.get_all(
        limit=per_page,
        offset=offset,
        category_id=category_id,
    )

    category = CategoryModel.get_by_id(category_id)
    if not category:
        return jsonify({"error": "РљР°С‚РµРіРѕСЂРёСЏ РЅРµ РЅР°Р№РґРµРЅР°"}), 404

    return jsonify({
        "category": category,
        "products": products,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    })


@catalog_bp.route("/filters")
def get_filters():
    """РџРѕР»СѓС‡РёС‚СЊ РґРѕСЃС‚СѓРїРЅС‹Рµ С„РёР»СЊС‚СЂС‹."""
    filters = ProductModel.get_filters()
    return jsonify(filters)


@catalog_bp.route("/new")
def get_new_arrivals():
    """РџРѕР»СѓС‡РёС‚СЊ РЅРѕРІС‹Рµ РїРѕСЃС‚СѓРїР»РµРЅРёСЏ."""
    limit = min(20, max(1, int(request.args.get("limit", 8))))
    products = ProductModel.get_new(limit=limit)
    return jsonify({"products": products})


@catalog_bp.route("/bestsellers")
def get_bestsellers():
    """РџРѕР»СѓС‡РёС‚СЊ РїРѕРїСѓР»СЏСЂРЅС‹Рµ С‚РѕРІР°СЂС‹."""
    limit = min(20, max(1, int(request.args.get("limit", 8))))
    products = ProductModel.get_bestsellers(limit=limit)
    return jsonify({"products": products})


@catalog_bp.route("/sale")
def get_on_sale():
    """РџРѕР»СѓС‡РёС‚СЊ С‚РѕРІР°СЂС‹ СЃРѕ СЃРєРёРґРєРѕР№."""
    limit = min(20, max(1, int(request.args.get("limit", 8))))
    products = ProductModel.get_on_sale(limit=limit)
    return jsonify({"products": products})


@catalog_bp.route("/search")
def search_products():
    """РџРѕРёСЃРє С‚РѕРІР°СЂРѕРІ."""
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2:
        return jsonify({"error": "Р’РІРµРґРёС‚Рµ РЅРµ РјРµРЅРµРµ 2 СЃРёРјРІРѕР»РѕРІ РґР»СЏ РїРѕРёСЃРєР°"}), 400

    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 12))))
    offset = (page - 1) * per_page

    products, total = ProductModel.get_all(
        limit=per_page,
        offset=offset,
        search=query,
    )

    return jsonify({
        "query": query,
        "products": products,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    })
