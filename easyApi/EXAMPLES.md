# Примеры использования easyApi

Сборник готовых рецептов для типовых задач.

---

## 🔐 Аутентификация

### Регистрация пользователя

```python
from easyApi import EasyApi
from flask import request

kit = EasyApi()
users = kit.model("users")


@kit.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    # Валидация
    if len(username) < 3:
        return {"error": "username должен быть не менее 3 символов"}, 400
    if "@" not in email:
        return {"error": "Некорректный email"}, 400
    if len(password) < 6:
        return {"error": "Пароль должен быть не менее 6 символов"}, 400
    
    # Проверка на дубликат
    existing = users.all(
        where="username = %s OR email = %s",
        where_params=(username, email),
    )
    if existing:
        return {"error": "Пользователь уже существует"}, 409
    
    # Создание
    result = users.create({
        "username": username,
        "email": email,
        "password": kit.hash_password(password),
        "role": "user",
    })
    
    token = kit.generate_token({
        "id": result["insert_id"],
        "username": username,
        "role": "user",
    })
    
    return {"user_id": result["insert_id"], "token": token}, 201
```

---

### Логин

```python
@kit.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return {"error": "username и password обязательны"}, 400
    
    # Поиск по username или email
    rows = users.all(
        where="username = %s OR email = %s",
        where_params=(username, username),
    )
    
    if not rows or not kit.check_password(password, rows[0]["password"]):
        return {"error": "Неверные учётные данные"}, 401
    
    user = rows[0]
    token = kit.generate_token({
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
    })
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        },
    }, 200
```

---

### Профиль текущего пользователя

```python
@kit.route("/me")
@kit.token_required
def me(current_user):
    user = users.get(current_user["id"])
    if not user:
        return {"error": "Пользователь не найден"}, 404
    
    # Не возвращаем хеш пароля
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    }
```

---

### Обновление профиля

```python
@kit.route("/me", methods=["PUT"])
@kit.token_required
def update_profile(current_user):
    data = request.get_json(silent=True) or {}
    
    # Разрешаем обновлять только определённые поля
    allowed_fields = ["email", "avatar_url"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return {"error": "Нет данных для обновления"}, 400
    
    users.update(current_user["id"], update_data)
    return {"message": "Профиль обновлён"}
```

---

### Смена пароля

```python
@kit.route("/auth/change-password", methods=["POST"])
@kit.token_required
def change_password(current_user):
    data = request.get_json(silent=True) or {}
    
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    
    if not old_password or not new_password:
        return {"error": "old_password и new_password обязательны"}, 400
    
    user = users.get(current_user["id"])
    if not kit.check_password(old_password, user["password"]):
        return {"error": "Неверный текущий пароль"}, 401
    
    if len(new_password) < 6:
        return {"error": "Новый пароль должен быть не менее 6 символов"}, 400
    
    users.update(current_user["id"], {
        "password": kit.hash_password(new_password),
    })
    
    return {"message": "Пароль изменён"}
```

---

## 📦 Товары и каталог

### Каталог с пагинацией

```python
@kit.route("/products")
def products_catalog():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset = (page - 1) * per_page
    
    # Общее количество
    total_rows = kit.select("products", columns="COUNT(*) as count")[0]["count"]
    
    # Товары с пагинацией
    items = kit.select(
        "products",
        columns="id, name, price, url, description",
        where="status = %s",
        where_params=("active",),
    )
    
    return {
        "items": items[offset:offset + per_page],
        "total": total_rows,
        "page": page,
        "per_page": per_page,
    }
```

---

### Поиск товаров

```python
@kit.route("/products/search")
def search_products():
    query = request.args.get("q", "").strip()
    
    if not query:
        return {"items": []}
    
    items = kit.select(
        "products",
        where="name LIKE %s OR description LIKE %s",
        where_params=(f"%{query}%", f"%{query}%"),
    )
    
    return {"items": items, "query": query}
```

---

### CRUD товаров (админка)

```python
@kit.route("/admin/products", methods=["POST"])
@kit.admin_required
def create_product(current_user):
    data = request.get_json()
    
    required = ["name", "price"]
    if not all(k in data for k in required):
        return {"error": f"Поля {required} обязательны"}, 400
    
    result = kit.insert("products", {
        "name": data["name"],
        "price": data["price"],
        "url": data.get("url", ""),
        "description": data.get("description", ""),
        "status": data.get("status", "active"),
    })
    
    return result, 201


@kit.route("/admin/products/<int:product_id>", methods=["PUT"])
@kit.admin_required
def update_product(current_user, product_id):
    data = request.get_json()
    
    allowed = ["name", "price", "url", "description", "status"]
    update_data = {k: v for k, v in data.items() if k in allowed}
    
    result = kit.update("products", update_data, where="id = %s", where_params=(product_id,))
    
    if result["affected_rows"] == 0:
        return {"error": "Товар не найден"}, 404
    
    return result


@kit.route("/admin/products/<int:product_id>", methods=["DELETE"])
@kit.admin_required
def delete_product(current_user, product_id):
    result = kit.delete("products", where="id = %s", where_params=(product_id,))
    
    if result["affected_rows"] == 0:
        return {"error": "Товар не найден"}, 404
    
    return result
```

---

## 🛒 Корзина

### Добавить в корзину

```python
@kit.route("/cart/add", methods=["POST"])
@kit.token_required
def add_to_cart(current_user):
    data = request.get_json()
    
    user_id = current_user["id"]
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    
    if not product_id or quantity < 1:
        return {"error": "product_id и quantity обязательны"}, 400
    
    # Получаем цену товара
    product = kit.model("products").get(product_id)
    if not product:
        return {"error": "Товар не найден"}, 404
    
    # Проверяем, есть ли уже в корзине
    existing = kit.select(
        "cart_items",
        where="user_id = %s AND product_id = %s",
        where_params=(user_id, product_id),
    )
    
    if existing:
        # Увеличиваем количество
        new_qty = existing[0]["quantity"] + quantity
        kit.update(
            "cart_items",
            {"quantity": new_qty, "price": product["price"]},
            where="user_id = %s AND product_id = %s",
            where_params=(user_id, product_id),
        )
    else:
        # Добавляем новую запись
        kit.insert("cart_items", {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": product["price"],
        })
    
    return {"message": "Товар добавлен в корзину"}
```

---

### Корзина пользователя

```python
@kit.route("/cart")
@kit.token_required
def get_cart(current_user):
    items = kit.select(
        "cart_items",
        columns="cart_items.*, products.name, products.url",
        join="LEFT JOIN products ON cart_items.product_id = products.id",
        where="cart_items.user_id = %s",
        where_params=(current_user["id"],),
    )
    
    total = sum(item["price"] * item["quantity"] for item in items)
    
    return {"items": items, "total": total}
```

---

### Очистить корзину

```python
@kit.route("/cart/clear", methods=["POST"])
@kit.token_required
def clear_cart(current_user):
    kit.delete("cart_items", where="user_id = %s", where_params=(current_user["id"],))
    return {"message": "Корзина очищена"}
```

---

## 📦 Заказы

### Создание заказа

```python
@kit.route("/orders", methods=["POST"])
@kit.token_required
def create_order(current_user):
    user_id = current_user["id"]
    
    # Получаем товары из корзины
    cart_items = kit.select(
        "cart_items",
        where="user_id = %s",
        where_params=(user_id,),
    )
    
    if not cart_items:
        return {"error": "Корзина пуста"}, 400
    
    # Считаем сумму
    total = sum(item["price"] * item["quantity"] for item in cart_items)
    
    # Используем транзакцию
    conn = None
    cursor = None
    
    try:
        from easyApi.db.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        # Создаём заказ
        cursor.execute(
            "INSERT INTO orders (user_id, total_price, status) VALUES (%s, %s, %s)",
            (user_id, total, "pending"),
        )
        order_id = cursor.lastrowid
        
        # Добавляем позиции заказа
        for item in cart_items:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, item["product_id"], item["quantity"], item["price"]),
            )
        
        # Очищаем корзину
        cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (user_id,))
        
        conn.commit()
        
        return {"order_id": order_id, "total": total}, 201
    
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

---

### История заказов

```python
@kit.route("/orders")
@kit.token_required
def my_orders(current_user):
    orders = kit.select(
        "orders",
        where="user_id = %s",
        where_params=(current_user["id"],),
    )
    
    # Добавляем позиции к каждому заказу
    for order in orders:
        items = kit.select(
            "order_items",
            columns="order_items.*, products.name",
            join="LEFT JOIN products ON order_items.product_id = products.id",
            where="order_id = %s",
            where_params=(order["id"],),
        )
        order["items"] = items
    
    return orders
```

---

### Детали заказа

```python
@kit.route("/orders/<int:order_id>")
@kit.token_required
def order_detail(current_user, order_id):
    order = kit.model("orders").get(order_id)
    
    if not order:
        return {"error": "Заказ не найден"}, 404
    
    # Проверка: заказ принадлежит пользователю или пользователь — админ
    if order["user_id"] != current_user["id"] and current_user["role"] != "admin":
        return {"error": "Доступ запрещён"}, 403
    
    items = kit.select(
        "order_items",
        columns="order_items.*, products.name, products.url",
        join="LEFT JOIN products ON order_items.product_id = products.id",
        where="order_id = %s",
        where_params=(order_id,),
    )
    
    order["items"] = items
    return order
```

---

## ⭐ Отзывы

### Добавить отзыв

```python
@kit.route("/reviews", methods=["POST"])
@kit.token_required
def add_review(current_user):
    data = request.get_json()
    
    product_id = data.get("product_id")
    text = data.get("text", "").strip()
    rating = data.get("rating")
    
    if not product_id or not text or not rating:
        return {"error": "product_id, text и rating обязательны"}, 400
    
    if not (1 <= rating <= 5):
        return {"error": "rating должен быть от 1 до 5"}, 400
    
    result = kit.insert("reviews", {
        "user_id": current_user["id"],
        "product_id": product_id,
        "text": text,
        "rating": rating,
    })
    
    return result, 201
```

---

### Отзывы к товару

```python
@kit.route("/products/<int:product_id>/reviews")
def product_reviews(product_id):
    reviews = kit.select(
        "reviews",
        columns="reviews.*, users.username",
        join="LEFT JOIN users ON reviews.user_id = users.id",
        where="reviews.product_id = %s",
        where_params=(product_id,),
    )
    
    # Считаем средний рейтинг
    if reviews:
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    return {
        "reviews": reviews,
        "avg_rating": round(avg_rating, 2),
        "count": len(reviews),
    }
```

---

## 🔧 Утилиты

### Кастомная обработка ошибок

```python
from flask import jsonify

@kit.flask.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Ресурс не найден", "code": 404}), 404


@kit.flask.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Внутренняя ошибка сервера", "code": 500}), 500
```

---

### Middleware (до обработки запроса)

```python
@kit.flask.before_request
def log_request():
    from flask import request
    print(f"[{request.method}] {request.path}")
```

---

### Кастомный декоратор

```python
from functools import wraps
from flask import request

def ip_required(f):
    """Требует наличие IP в заголовке."""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.headers.get("x-client-ip")
        if not ip:
            return {"error": "IP обязателен"}, 400
        return f(ip, *args, **kwargs)
    return decorated


@kit.route("/tracked")
@ip_required
def tracked(client_ip):
    return {"your_ip": client_ip}
```

---

## 📊 Админ-панель

### Статистика

```python
@kit.route("/admin/stats")
@kit.admin_required
def admin_stats(current_user):
    users_count = kit.select("users", columns="COUNT(*) as count")[0]["count"]
    products_count = kit.select("products", columns="COUNT(*) as count")[0]["count"]
    orders_count = kit.select("orders", columns="COUNT(*) as count")[0]["count"]
    
    # Общая выручка
    revenue = kit.select("orders", columns="SUM(total_price) as revenue")[0]["revenue"] or 0
    
    return {
        "users": users_count,
        "products": products_count,
        "orders": orders_count,
        "revenue": float(revenue),
    }
```

---

### Управление пользователями (админ)

```python
@kit.route("/admin/users")
@kit.admin_required
def admin_users(current_user):
    users = kit.select("users", columns="id, username, email, role, created_at")
    return users


@kit.route("/admin/users/<int:user_id>/role", methods=["PUT"])
@kit.admin_required
def update_user_role(current_user, user_id):
    data = request.get_json()
    role = data.get("role")
    
    if role not in ["user", "admin", "moderator"]:
        return {"error": "Недопустимая роль"}, 400
    
    kit.update("users", {"role": role}, where="id = %s", where_params=(user_id,))
    return {"message": "Роль обновлена"}
```
