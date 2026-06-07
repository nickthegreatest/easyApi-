# easyApi

**Минималистичная библиотека для RESTful API на Flask + PyMySQL.**

Пишите меньше кода — делайте больше. Вся функциональность через один импорт.

```bash
pip install -e .
```

## Быстрый старт

```python
from easyApi import EasyApi

kit = EasyApi(config={"DB_NAME": "shop_db", "SECRET_KEY": "secret"})

# Авто-CRUD роуты: GET/POST/PUT/DELETE /users/
kit.register_crud("users")

@kit.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    kit.run(debug=True)
```

## Возможности

| Возможность | Код |
|-------------|-----|
| CRUD для таблицы | `kit.register_crud("users")` |
| Работа с моделью | `kit.model("users").all()` |
| JWT токен | `kit.generate_token({...})` |
| Защита роута | `@kit.token_required` |
| Хеш пароля | `kit.hash_password("pwd")` |

## Конфигурация

Через переменные окружения (`EASYAPI_DB_HOST`, `EASYAPI_SECRET_KEY`, ...):

```python
kit = EasyApi()  # автоматически читает EASYAPI_*
```

Или через словарь:

```python
kit = EasyApi(config={"DB_NAME": "shop_db", "SECRET_KEY": "secret"})
```

## Документация

| Документ | Описание |
|----------|----------|
| 📖 [API Reference](docs/API_REFERENCE.md) | Полное описание всех классов и методов |
| 🔧 [Примеры](docs/EXAMPLES.md) | Готовые рецепты (аутентификация, товары, заказы) |
| 🏗️ [Своя схема БД](docs/CUSTOM_SCHEMA.md) | Как использовать easyApi с любой схемой данных |

## Демо

```bash
mysql -u root -p < schema.sql
python -m demo.api
```

После установки достаточно импортировать только `easyApi`.

## Быстрый старт (один импорт)

```python
from easyApi import EasyApi

kit = EasyApi(
    config={
        "DB_HOST": "localhost",
        "DB_USER": "root",
        "DB_PASSWORD": "",
        "DB_NAME": "shop_db",
        "SECRET_KEY": "secret",
    }
)

@kit.route("/health")
def health():
    return {"status": "ok"}

# Простой доступ к таблице через модель
products = kit.model("products")

@kit.route("/products")
def get_products():
    return products.all()

# Автогенерация CRUD-эндпоинтов:
# GET /users/, GET /users/<id>, POST /users/, PUT /users/<id>, DELETE /users/<id>
kit.register_crud("users")

if __name__ == "__main__":
    kit.run(debug=True)
```


## Конфигурация через переменные окружения

Если не передавать `config`, EasyApi автоматически пытается читать переменные окружения с префиксом `EASYAPI_`:

- `EASYAPI_DB_HOST`
- `EASYAPI_DB_USER`
- `EASYAPI_DB_PASSWORD`
- `EASYAPI_DB_NAME`
- `EASYAPI_DB_PORT`
- `EASYAPI_SECRET_KEY`
- `EASYAPI_JWT_EXPIRATION_HOURS`

Пример:

```powershell
$env:EASYAPI_DB_HOST="localhost"
$env:EASYAPI_DB_USER="root"
$env:EASYAPI_DB_NAME="shop_db"
$env:EASYAPI_SECRET_KEY="secret"
```

И затем:


```python
from easyApi import EasyApi

kit = EasyApi()
```

## Демо интернет-магазина

```bash
mysql -u root -p < schema.sql
python -m demo.api
```


