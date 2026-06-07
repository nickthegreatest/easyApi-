# easyApi

**easyApi** — минималистичная Python-библиотека для быстрой разработки RESTful API на Flask + PyMySQL с акцентом на минимальное количество кода.

## Особенности

- ✅ **Один импорт** — всё через `EasyApi`
- ✅ **Авто-CRUD** — генерация роутов одной строкой
- ✅ **Модели** — простой доступ к таблицам БД
- ✅ **JWT из коробки** — токены, декораторы защиты
- ✅ **Конфиг из ENV** — переменные окружения `EASYAPI_*`
- ✅ **Единый обработчик ошибок** — JSON-ответы для всех исключений

---

## Установка

```bash
pip install -e .
```

**Зависимости (устанавливаются автоматически):**
- Flask >= 3.0.0
- PyMySQL >= 1.1.0
- PyJWT >= 2.8.0
- Werkzeug >= 3.0.0

---

## Быстрый старт

### Минимальное приложение (5 строк)

```python
from easyApi import EasyApi

kit = EasyApi(config={"DB_NAME": "shop_db", "SECRET_KEY": "secret"})

@kit.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    kit.run(debug=True)
```

### С авто-CRUD для таблицы

```python
from easyApi import EasyApi

kit = EasyApi(config={"DB_NAME": "shop_db", "SECRET_KEY": "secret"})

# Автоматически создаёт роуты:
# GET /users/, GET /users/<id>, POST /users/, PUT /users/<id>, DELETE /users/<id>
kit.register_crud("users")

if __name__ == "__main__":
    kit.run(debug=True)
```

### Через переменные окружения

```python
from easyApi import EasyApi

# Конфигурация считывается из EASYAPI_* переменных автоматически
kit = EasyApi()

@kit.route("/products")
def products():
    return kit.select("products")

if __name__ == "__main__":
    kit.run(debug=True)
```

---

## Конфигурация

### Через переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `EASYAPI_DB_HOST` | Хост базы данных | `localhost` |
| `EASYAPI_DB_USER` | Пользователь БД | `root` |
| `EASYAPI_DB_PASSWORD` | Пароль БД | `""` |
| `EASYAPI_DB_NAME` | Имя базы данных | `shop_db` |
| `EASYAPI_DB_PORT` | Порт БД | `3306` |
| `EASYAPI_SECRET_KEY` | Секретный ключ для JWT | `change-me-in-production` |
| `EASYAPI_JWT_EXPIRATION_HOURS` | Время жизни токена (часы) | `1` |

Пример установки (PowerShell):
```powershell
$env:EASYAPI_DB_HOST="localhost"
$env:EASYAPI_DB_USER="root"
$env:EASYAPI_DB_PASSWORD="mypassword"
$env:EASYAPI_DB_NAME="shop_db"
$env:EASYAPI_SECRET_KEY="super-secret-key"
```

### Через словарь

```python
from easyApi import EasyApi

kit = EasyApi(
    config={
        "DB_HOST": "localhost",
        "DB_USER": "root",
        "DB_PASSWORD": "mypassword",
        "DB_NAME": "shop_db",
        "DB_PORT": 3306,
        "SECRET_KEY": "super-secret-key",
        "JWT_EXPIRATION_HOURS": 24,
    }
)
```

---

## API Reference

### Класс `EasyApi`

Основной класс библиотеки. Объединяет все возможности в одном интерфейсе.

#### Конструктор

```python
kit = EasyApi(
    config: dict | Config | None = None,
    blueprints: list[Blueprint] | None = None,
    name: str | None = None,
    use_env: bool = True,
    env_prefix: str = "EASYAPI_",
)
```

| Параметр | Описание |
|----------|----------|
| `config` | Словарь настроек или объект `Config` |
| `blueprints` | Список Flask Blueprint для регистрации |
| `name` | Имя приложения (по умолчанию `__name__`) |
| `use_env` | Читать ли переменные окружения (по умолчанию `True`) |
| `env_prefix` | Префикс переменных окружения (по умолчанию `"EASYAPI_"`) |

---

### Работа с базой данных

#### `kit.model(table: str) -> SimpleModel`

Возвращает CRUD-модель для работы с таблицей.

```python
users = kit.model("users")

# Получить все записи
all_users = users.all()

# Получить одну запись по ID
user = users.get(1)

# Создать запись
result = users.create({"username": "john", "email": "john@example.com"})

# Обновить запись
users.update(1, {"email": "new@example.com"})

# Удалить запись
users.delete(1)
```

**Методы `SimpleModel`:**

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `all(where, where_params, columns, join)` | Получить все записи | `list[dict]` |
| `get(entity_id, id_column)` | Получить запись по ID | `dict \| None` |
| `create(data)` | Создать запись | `dict` (insert_id) |
| `update(entity_id, data, id_column)` | Обновить запись | `dict` (affected_rows) |
| `delete(entity_id, id_column)` | Удалить запись | `dict` (affected_rows) |

---

#### `kit.select(table, where, where_params, columns, join) -> list[dict]`

Короткий хелпер для SELECT-запросов.

```python
# Все товары
products = kit.select("products")

# Товары с условием
active_users = kit.select(
    "users",
    where="status = %s",
    where_params=("active",),
)

# С JOIN
orders_with_items = kit.select(
    "orders",
    columns="orders.*, order_items.product_id",
    join="LEFT JOIN order_items ON orders.id = order_items.order_id",
)
```

---

#### `kit.insert(table, params) -> dict`

INSERT-запрос.

```python
result = kit.insert("users", {
    "username": "john",
    "email": "john@example.com",
    "password": "hashed_password",
})
print(result["insert_id"])  # ID новой записи
```

---

#### `kit.update(table, params, where, where_params) -> dict`

UPDATE-запрос.

```python
result = kit.update(
    "users",
    {"email": "new@example.com"},
    where="id = %s",
    where_params=(1,),
)
print(result["affected_rows"])  # Количество обновлённых строк
```

---

#### `kit.delete(table, where, where_params) -> dict`

DELETE-запрос.

```python
result = kit.delete(
    "users",
    where="id = %s",
    where_params=(1,),
)
print(result["affected_rows"])  # Количество удалённых строк
```

---

#### `kit.query(operation, table, ...) -> Any`

Универсальный CRUD-запрос.

```python
# SELECT
users = kit.query("SELECT", "users", where="status = %s", where_params=("active",))

# INSERT
result = kit.query("INSERT", "users", params={"username": "john"})

# UPDATE
result = kit.query("UPDATE", "users", params={"email": "new@mail.com"}, where="id = %s", where_params=(1,))

# DELETE
result = kit.query("DELETE", "users", where="id = %s", where_params=(1,))
```

---

### Автогенерация CRUD-роутов

#### `kit.register_crud(table, url_prefix, id_column, methods) -> Blueprint`

Автоматически регистрирует REST-роуты для таблицы.

```python
# Полный CRUD
kit.register_crud("users")

# С кастомным префиксом
kit.register_crud("products", url_prefix="/api/products")

# Только GET (read-only)
kit.register_crud("categories", methods=("GET",))

# С кастомным полем ID
kit.register_crud("orders", id_column="order_id")
```

**Создаваемые роуты:**

| Метод | Роут | Описание |
|-------|------|----------|
| `GET` | `/{table}/` | Список всех записей |
| `GET` | `/{table}/<id>` | Одна запись по ID |
| `POST` | `/{table}/` | Создать запись |
| `PUT` | `/{table}/<id>` | Обновить запись |
| `DELETE` | `/{table}/<id>` | Удалить запись |

---

### Работа с маршрутами

#### `kit.route(rule, **options) -> decorator`

Декоратор для объявления маршрутов (аналог `@app.route`).

```python
@kit.route("/hello")
def hello():
    return {"message": "Hello, World!"}

@kit.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = kit.model("users").get(user_id)
    return user if user else {"error": "Not found"}, 404
```

---

### JWT и безопасность

#### `kit.generate_token(user_data) -> str`

Генерирует JWT-токен.

```python
token = kit.generate_token({
    "id": 1,
    "username": "john",
    "role": "user",
})
```

---

#### `kit.verify_token(token) -> dict`

Проверяет и декодирует токен.

```python
try:
    payload = kit.verify_token(token)
    print(payload["username"])
except Exception as e:
    print(f"Токен невалиден: {e}")
```

---

#### `kit.hash_password(password) -> str`

Хеширует пароль.

```python
hashed = kit.hash_password("mypassword")
```

---

#### `kit.check_password(password, hashed) -> bool`

Проверяет пароль против хеша.

```python
if kit.check_password("mypassword", hashed):
    print("Пароль верный")
```

---

#### `kit.token_required` (декоратор)

Требует валидный JWT в заголовке `x-access-token`.

```python
@kit.route("/protected")
@kit.token_required
def protected(current_user):
    return {"user": current_user}
```

---

#### `kit.admin_required` (декоратор)

Требует роль `admin`.

```python
@kit.route("/admin/users")
@kit.admin_required
def admin_users(current_user):
    return kit.select("users")
```

---

### Flask-интеграция

#### `kit.flask -> Flask`

Доступ к внутреннему Flask-приложению.

```python
app = kit.flask
```

---

#### `kit.register_blueprint(blueprint, **options)`

Регистрация Flask Blueprint.

```python
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    return {"token": "xxx"}

kit.register_blueprint(auth_bp, url_prefix="/auth")
```

---

#### `kit.run(*args, **kwargs)`

Запуск встроенного сервера разработки.

```python
kit.run(debug=True, host="0.0.0.0", port=5000)
```

---

## Примеры использования

### Регистрация и логин пользователя

```python
from easyApi import EasyApi
from flask import request

kit = EasyApi(config={"DB_NAME": "shop_db", "SECRET_KEY": "secret"})

users = kit.model("users")


@kit.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not all([username, email, password]):
        return {"error": "username, email и password обязательны"}, 400
    
    # Проверка на существование
    existing = users.all(where="username = %s OR email = %s", where_params=(username, email))
    if existing:
        return {"error": "Пользователь уже существует"}, 409
    
    # Создание пользователя
    result = users.create({
        "username": username,
        "email": email,
        "password": kit.hash_password(password),
        "role": "user",
    })
    
    # Генерация токена
    token = kit.generate_token({
        "id": result["insert_id"],
        "username": username,
        "role": "user",
    })
    
    return {"user_id": result["insert_id"], "token": token}, 201


@kit.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not all([username, password]):
        return {"error": "username и password обязательны"}, 400
    
    # Поиск пользователя
    rows = users.all(where="username = %s", where_params=(username,))
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
        "user": {"id": user["id"], "username": user["username"], "role": user["role"]},
    }, 200


@kit.route("/me")
@kit.token_required
def me(current_user):
    return {"user": current_user}


if __name__ == "__main__":
    kit.run(debug=True)
```

---

### Интернет-магазин: товары и заказы

```python
from easyApi import EasyApi
from flask import request

kit = EasyApi(config={"DB_NAME": "shop_db", "SECRET_KEY": "secret"})

products = kit.model("products")
orders = kit.model("orders")


# Авто-CRUD для товаров (админка)
@kit.route("/admin/products", methods=["POST"])
@kit.admin_required
def create_product(current_user):
    data = request.get_json()
    result = products.create(data)
    return result, 201


# Публичный каталог
@kit.route("/catalog")
def catalog():
    return products.all()


@kit.route("/catalog/<int:product_id>")
def product_detail(product_id):
    product = products.get(product_id)
    if not product:
        return {"error": "Товар не найден"}, 404
    return product


# Создание заказа
@kit.route("/orders", methods=["POST"])
@kit.token_required
def create_order(current_user):
    data = request.get_json()
    order_data = {
        "user_id": current_user["id"],
        "total_price": data.get("total_price", 0),
        "status": "pending",
    }
    result = orders.create(order_data)
    return result, 201


# Мои заказы
@kit.route("/my-orders")
@kit.token_required
def my_orders(current_user):
    user_orders = orders.all(
        where="user_id = %s",
        where_params=(current_user["id"],),
    )
    return user_orders


if __name__ == "__main__":
    kit.run(debug=True)
```

---

## Обработка ошибок

Библиотека автоматически перехватывает исключения и возвращает JSON:

| Исключение | Код | Ответ |
|------------|-----|-------|
| `TokenExpiredError` | 401 | `{"error": "Срок действия токена истёк", "code": 401}` |
| `TokenInvalidError` | 403 | `{"error": "Недействительный токен", "code": 403}` |
| `DatabaseError` | 500 | `{"error": "...", "code": 500}` |
| Другие исключения | 500 | `{"error": "...", "code": 500}` |

---

## Структура проекта

```
easyApi/
├── __init__.py          # Публичный API
├── app.py               # Класс EasyApi, SimpleModel
├── config.py            # Конфигурация, ENV
├── db/
│   ├── connection.py    # Подключение к БД, execute_query
│   └── exceptions.py    # Исключения
├── models/              # Готовые модели (users, products, ...)
└── services/
    ├── jwt_service.py   # Генерация/проверка токенов
    └── security.py      # Хеш паролей, декораторы
```

---

## Совместимость

- Python >= 3.10
- Flask >= 3.0.0
- MySQL / MariaDB (через PyMySQL)

---

## Лицензия

MIT
