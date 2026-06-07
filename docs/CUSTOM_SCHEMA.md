# Работа с произвольной схемой БД

**easyApi** не требует конкретной схемы базы данных. Библиотека работает с **любыми таблицами и полями**, которые есть у вас.

> 💡 **Важно:** Готовые модели в `easyApi/models/` (users, products, orders) — это **примеры** под демо интернет-магазина. Для своего проекта вы создаёте **свои модели** под **вашу схему**.

---

## Что универсально (работает с любой БД)

| Компонент | Описание |
|-----------|----------|
| `EasyApi` класс | Подключение, конфиг, запуск сервера |
| `kit.model(table)` | CRUD для **любой** таблицы |
| `kit.register_crud(table)` | Авто-роуты для **любой** таблицы |
| `kit.select()`, `kit.insert()`, `kit.update()`, `kit.delete()` | Универсальные SQL-хелперы |
| `kit.generate_token()`, `kit.verify_token()` | JWT (не зависит от БД) |
| `kit.hash_password()`, `kit.check_password()` | Хеширование (не зависит от БД) |
| `@kit.token_required`, `@kit.admin_required` | Декораторы защиты |

---

## Что НЕ универсально (только для демо)

| Компонент | Почему не подходит |
|-----------|-------------------|
| `easyApi/models/*.py` | Заточены под `users`, `products`, `orders`, `cart_items` |
| `easyApi/services/order_service.py` | Логика под корзину и заказы |
| `demo/controllers/*.py` | Конкретная схема интернет-магазина |

**Для своего проекта:** создавайте **свои модели** в **своей папке** проекта.

---

## Пошаговая инструкция: новый проект с нуля

### Шаг 1: Структура проекта

```
my_project/
├── main.py                 # Точка входа
├── config.py               # Настройки
├── models/                 # ТВОИ модели
│   ├── __init__.py
│   ├── post.py
│   ├── comment.py
│   └── user.py
└── controllers/            # ТВОИ контроллеры (опционально)
    ├── __init__.py
    ├── auth.py
    └── api.py
```

---

### Шаг 2: Подключение easyApi

**`main.py`:**
```python
from easyApi import EasyApi

kit = EasyApi(
    config={
        "DB_HOST": "localhost",
        "DB_USER": "root",
        "DB_PASSWORD": "",
        "DB_NAME": "my_database",  # Твоя БД
        "SECRET_KEY": "your-secret-key",
    }
)

# Регистрация роутов
from controllers import auth, api

kit.register_blueprint(auth.bp, url_prefix="/auth")
kit.register_blueprint(api.bp, url_prefix="/api")

# Авто-CRUD для простых таблиц
kit.register_crud("categories")
kit.register_crud("tags")

if __name__ == "__main__":
    kit.run(debug=True)
```

---

### Шаг 3: Создание своих моделей

**`models/post.py`:**
```python
from easyApi import execute_query


def get_all_posts(limit: int = 20, offset: int = 0):
    """Получить список постов с пагинацией."""
    return execute_query(
        "SELECT",
        "posts",
        columns="id, title, slug, content, author_id, created_at, updated_at",
        where="status = %s",
        where_params=("published",),
    )[offset:offset + limit]


def get_post_by_id(post_id: int):
    """Получить пост по ID."""
    rows = execute_query(
        "SELECT",
        "posts",
        where="id = %s",
        where_params=(post_id,),
    )
    return rows[0] if rows else None


def get_post_by_slug(slug: str):
    """Получить пост по slug (URL-friendly название)."""
    rows = execute_query(
        "SELECT",
        "posts",
        where="slug = %s",
        where_params=(slug,),
    )
    return rows[0] if rows else None


def create_post(title: str, slug: str, content: str, author_id: int, status: str = "draft"):
    """Создать новый пост."""
    return execute_query(
        "INSERT",
        "posts",
        {
            "title": title,
            "slug": slug,
            "content": content,
            "author_id": author_id,
            "status": status,
        },
    )


def update_post(post_id: int, data: dict):
    """Обновить пост (частичное обновление)."""
    return execute_query(
        "UPDATE",
        "posts",
        data,
        where="id = %s",
        where_params=(post_id,),
    )


def delete_post(post_id: int):
    """Удалить пост."""
    return execute_query(
        "DELETE",
        "posts",
        where="id = %s",
        where_params=(post_id,),
    )


def get_posts_by_author(author_id: int):
    """Получить все посты автора."""
    return execute_query(
        "SELECT",
        "posts",
        where="author_id = %s",
        where_params=(author_id,),
    )
```

---

**`models/comment.py`:**
```python
from easyApi import execute_query


def get_comments_for_post(post_id: int):
    """Получить все комментарии к посту."""
    return execute_query(
        "SELECT",
        "comments",
        columns="comments.*, users.username",
        join="LEFT JOIN users ON comments.user_id = users.id",
        where="comments.post_id = %s",
        where_params=(post_id,),
    )


def create_comment(post_id: int, user_id: int, content: str):
    """Добавить комментарий."""
    return execute_query(
        "INSERT",
        "comments",
        {
            "post_id": post_id,
            "user_id": user_id,
            "content": content,
        },
    )


def delete_comment(comment_id: int, user_id: int):
    """Удалить комментарий (только свой)."""
    return execute_query(
        "DELETE",
        "comments",
        where="id = %s AND user_id = %s",
        where_params=(comment_id, user_id),
    )
```

---

**`models/user.py`:**
```python
from easyApi import execute_query, hash_password


def create_user(username: str, email: str, password: str, role: str = "user"):
    """Создать пользователя с хешированным паролем."""
    return execute_query(
        "INSERT",
        "users",
        {
            "username": username,
            "email": email,
            "password": hash_password(password),
            "role": role,
        },
    )


def get_user_by_username(username: str):
    """Найти пользователя по username."""
    rows = execute_query(
        "SELECT",
        "users",
        where="username = %s",
        where_params=(username,),
    )
    return rows[0] if rows else None


def get_user_by_email(email: str):
    """Найти пользователя по email."""
    rows = execute_query(
        "SELECT",
        "users",
        where="email = %s",
        where_params=(email,),
    )
    return rows[0] if rows else None


def get_user_by_id(user_id: int):
    """Найти пользователя по ID."""
    rows = execute_query(
        "SELECT",
        "users",
        where="id = %s",
        where_params=(user_id,),
    )
    return rows[0] if rows else None


def update_user(user_id: int, data: dict):
    """Обновить данные пользователя."""
    # Удаляем password из данных, если есть (используй отдельный метод)
    data.pop("password", None)
    return execute_query(
        "UPDATE",
        "users",
        data,
        where="id = %s",
        where_params=(user_id,),
    )


def change_password(user_id: int, new_password: str):
    """Сменить пароль."""
    return execute_query(
        "UPDATE",
        "users",
        {"password": hash_password(new_password)},
        where="id = %s",
        where_params=(user_id,),
    )
```

---

### Шаг 4: Создание контроллеров

**`controllers/auth.py`:**
```python
from flask import Blueprint, request, jsonify
from easyApi import generate_token, check_password
from models import user

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    """Регистрация нового пользователя."""
    data = request.get_json(silent=True) or {}
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    # Валидация
    errors = []
    if len(username) < 3:
        errors.append("username должен быть не менее 3 символов")
    if "@" not in email:
        errors.append("Некорректный email")
    if len(password) < 6:
        errors.append("Пароль должен быть не менее 6 символов")
    
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Проверка на дубликат
    if user.get_user_by_username(username):
        return jsonify({"error": "username уже занят"}), 409
    if user.get_user_by_email(email):
        return jsonify({"error": "email уже зарегистрирован"}), 409
    
    # Создание
    result = user.create_user(username, email, password)
    
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
    }), 201


@bp.route("/login", methods=["POST"])
def login():
    """Вход в систему."""
    data = request.get_json(silent=True) or {}
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"error": "username и password обязательны"}), 400
    
    # Поиск пользователя (по username или email)
    user_data = user.get_user_by_username(username)
    if not user_data:
        user_data = user.get_user_by_email(username)
    
    if not user_data or not check_password(password, user_data["password"]):
        return jsonify({"error": "Неверные учётные данные"}), 401
    
    # Генерация токена
    token = generate_token({
        "id": user_data["id"],
        "username": user_data["username"],
        "role": user_data["role"],
    })
    
    return jsonify({
        "message": "Успешный вход",
        "token": token,
        "user": {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
        },
    }), 200
```

---

**`controllers/api.py`:**
```python
from flask import Blueprint, request, jsonify
from easyApi import token_required
from models import post, comment, user

bp = Blueprint("api", __name__)


# === Посты ===

@bp.route("/posts")
def get_posts():
    """Список всех опубликованных постов."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page
    
    posts = post.get_all_posts(limit=per_page, offset=offset)
    return jsonify({"posts": posts, "page": page, "per_page": per_page})


@bp.route("/posts/<slug>")
def get_post(slug):
    """Один пост по slug."""
    post_data = post.get_post_by_slug(slug)
    if not post_data:
        return jsonify({"error": "Пост не найден"}), 404
    
    # Добавляем комментарии
    post_data["comments"] = comment.get_comments_for_post(post_data["id"])
    
    # Добавляем автора
    author = user.get_user_by_id(post_data["author_id"])
    post_data["author"] = {"username": author["username"]} if author else None
    
    return jsonify(post_data)


@bp.route("/posts", methods=["POST"])
@token_required
def create_post(current_user):
    """Создать новый пост (требует авторизации)."""
    data = request.get_json()
    
    required = ["title", "content"]
    if not all(k in data for k in required):
        return jsonify({"error": "title и content обязательны"}), 400
    
    # Генерируем slug из title (упрощённо)
    slug = data["title"].lower().replace(" ", "-")
    
    result = post.create_post(
        title=data["title"],
        slug=slug,
        content=data["content"],
        author_id=current_user["id"],
        status=data.get("status", "draft"),
    )
    
    return jsonify(result), 201


@bp.route("/posts/<int:post_id>", methods=["PUT"])
@token_required
def update_post(current_user, post_id):
    """Обновить пост (только автор)."""
    post_data = post.get_post_by_id(post_id)
    if not post_data:
        return jsonify({"error": "Пост не найден"}), 404
    
    # Проверка: только автор может редактировать
    if post_data["author_id"] != current_user["id"]:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    data = request.get_json()
    allowed = ["title", "content", "status"]
    update_data = {k: v for k, v in data.items() if k in allowed}
    
    result = post.update_post(post_id, update_data)
    return jsonify(result)


@bp.route("/posts/<int:post_id>", methods=["DELETE"])
@token_required
def delete_post(current_user, post_id):
    """Удалить пост (только автор)."""
    post_data = post.get_post_by_id(post_id)
    if not post_data:
        return jsonify({"error": "Пост не найден"}), 404
    
    if post_data["author_id"] != current_user["id"]:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    result = post.delete_post(post_id)
    return jsonify(result)


# === Комментарии ===

@bp.route("/posts/<int:post_id>/comments", methods=["POST"])
@token_required
def add_comment(current_user, post_id):
    """Добавить комментарий к посту."""
    data = request.get_json()
    content = data.get("content", "").strip()
    
    if not content:
        return jsonify({"error": "content обязателен"}), 400
    
    result = comment.create_comment(
        post_id=post_id,
        user_id=current_user["id"],
        content=content,
    )
    
    return jsonify(result), 201


@bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@token_required
def delete_comment(current_user, comment_id):
    """Удалить свой комментарий."""
    result = comment.delete_comment(comment_id, current_user["id"])
    
    if result["affected_rows"] == 0:
        return jsonify({"error": "Комментарий не найден"}), 404
    
    return jsonify(result)
```

---

## Примеры для разных типов проектов

### 1. Блог / CMS

```python
# main.py
kit = EasyApi(config={"DB_NAME": "blog_db", "SECRET_KEY": "secret"})

kit.register_crud("categories")
kit.register_crud("tags")
kit.register_crud("media")  # изображения, файлы

from controllers import auth, posts, comments

kit.register_blueprint(posts.bp, url_prefix="/api")
kit.register_blueprint(comments.bp, url_prefix="/api")
```

**Таблицы:**
```sql
posts (id, title, slug, content, author_id, status, created_at, updated_at)
comments (id, post_id, user_id, content, created_at)
categories (id, name, slug, parent_id)
tags (id, name, slug)
post_tags (post_id, tag_id)
media (id, filename, url, uploaded_by, created_at)
```

---

### 2. CRM система

```python
# main.py
kit = EasyApi(config={"DB_NAME": "crm_db", "SECRET_KEY": "secret"})

kit.register_crud("companies")
kit.register_crud("contacts")

from controllers import deals, tasks, auth

kit.register_blueprint(deals.bp, url_prefix="/api")
kit.register_blueprint(tasks.bp, url_prefix="/api")
```

**Таблицы:**
```sql
companies (id, name, inn, address, phone, website, created_at)
contacts (id, company_id, name, email, phone, position)
deals (id, company_id, title, amount, stage, owner_id, created_at)
tasks (id, deal_id, assigned_to, title, description, due_date, status)
```

---

### 3. Трекер задач (Task Manager)

```python
# main.py
kit = EasyApi(config={"DB_NAME": "tasks_db", "SECRET_KEY": "secret"})

kit.register_crud("projects")
kit.register_crud("labels")

from controllers import tasks, auth

kit.register_blueprint(tasks.bp, url_prefix="/api")
```

**Таблицы:**
```sql
projects (id, name, description, owner_id, created_at)
tasks (id, project_id, title, description, status, priority, assignee_id, due_date)
labels (id, name, color)
task_labels (task_id, label_id)
```

---

### 4. Образовательная платформа

```python
# main.py
kit = EasyApi(config={"DB_NAME": "edu_db", "SECRET_KEY": "secret"})

kit.register_crud("courses")
kit.register_crud("lessons")

from controllers import enrollments, progress, auth

kit.register_blueprint(enrollments.bp, url_prefix="/api")
kit.register_blueprint(progress.bp, url_prefix="/api")
```

**Таблицы:**
```sql
courses (id, title, description, instructor_id, price, created_at)
lessons (id, course_id, title, content, order, duration)
enrollments (id, user_id, course_id, enrolled_at, completed_at)
progress (id, enrollment_id, lesson_id, completed, completed_at)
```

---

## Советы по организации кода

### ✅ Делай

```python
# models/user.py — только логика БД
def get_user_by_id(user_id):
    rows = execute_query("SELECT", "users", where="id = %s", where_params=(user_id,))
    return rows[0] if rows else None

# controllers/auth.py — только HTTP-логика
@bp.route("/login", methods=["POST"])
def login():
    user_data = user.get_user_by_username(data["username"])
    if not user_data:
        return jsonify({"error": "Not found"}), 404
```

### ❌ Не делай

```python
# НЕ смешивай HTTP и БД в одном месте
@bp.route("/login", methods=["POST"])
def login():
    # Плохо: SQL-запрос прямо в контроллере
    rows = execute_query("SELECT", "users", ...)
```

---

## Чеклист для нового проекта

- [ ] Создать структуру проекта (`main.py`, `models/`, `controllers/`)
- [ ] Настроить подключение к БД (`DB_NAME`, `SECRET_KEY`)
- [ ] Создать **свои модели** под **свою схему**
- [ ] Создать контроллеры (или использовать `register_crud` для простых таблиц)
- [ ] **НЕ использовать** `easyApi/models/*` и `demo/*` из библиотеки
- [ ] Протестировать CRUD для основных таблиц
- [ ] Добавить аутентификацию (если нужна)

---

## FAQ

### Q: Могу ли я использовать готовые модели из `easyApi/models/`?

**A:** Только если ваша схема БД **точно совпадает** с демо-магазином (таблицы `users`, `products`, `orders`, `cart_items`, `reviews`). В 99% случаев — **нет**, создавайте свои.

---

### Q: А что тогда использовать из библиотеки?

**A:** Универсальные компоненты:
- `EasyApi` класс
- `kit.model()`, `kit.select()`, `kit.insert()`, `kit.update()`, `kit.delete()`
- `kit.register_crud()`
- `kit.generate_token()`, `kit.hash_password()`
- `@kit.token_required`, `@kit.admin_required`

---

### Q: Могу ли я изменить префикс переменных окружения (например, `MYAPP_` вместо `EASYAPI_`)?

**A:** Да:
```python
kit = EasyApi(
    config={...},
    use_env=True,
    env_prefix="MYAPP_",  # свой префикс
)
```

---

### Q: Как работать с транзакциями?

**A:** Через прямое подключение:
```python
from easyApi.db.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute("INSERT INTO orders ...")
    cursor.execute("INSERT INTO order_items ...")
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    cursor.close()
    conn.close()
```

---

### Q: Можно ли использовать несколько баз данных?

**A:** Да, но нужно создавать несколько экземпляров `EasyApi` или управлять подключениями вручную:
```python
kit_main = EasyApi(config={"DB_NAME": "main_db", "SECRET_KEY": "key1"})
kit_analytics = EasyApi(config={"DB_NAME": "analytics_db", "SECRET_KEY": "key2"})
```

Или использовать прямые подключения для второй БД.

---

## Заключение

**easyApi** — это **инструмент**, а не готовое решение под конкретную схему.

- ✅ Используйте универсальные API (`model`, `select`, `register_crud`, JWT)
- ✅ Создавайте **свои модели** под **свою схему**
- ❌ Не используйте готовые модели из `easyApi/models/` (это только примеры)

Такой подход даёт гибкость: библиотека работает с **любой** реляционной БД (MySQL, MariaDB, PostgreSQL через адаптер) и **любой** схемой данных.
