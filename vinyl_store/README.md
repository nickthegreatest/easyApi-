# Vintage Vinyl Store

Полноценный дипломный проект интернет-магазина виниловых пластинок, построенный на собственной библиотеке **EasyApi** — обёртке над Flask и PyMySQL для быстрой разработки REST API.

## Цель проекта

Проект демонстрирует возможности библиотеки без Django, FastAPI, SQLAlchemy, Peewee и других ORM:

- автоматизированное подключение к MySQL через EasyApi и PyMySQL;
- CRUD-операции через SQL-запросы и helper-функции библиотеки;
- маршрутизацию через Flask/EasyApi-декораторы;
- JWT-аутентификацию через PyJWT;
- хеширование паролей через Werkzeug;
- централизованную обработку ошибок;
- стандартизированные JSON-ответы формата `{ success, message, data }`.

## Анализ существующей БД

Приложение построено вокруг уже существующих таблиц и не требует создания новой структуры БД. Используются таблицы:

| Таблица | Назначение |
| --- | --- |
| `users` | пользователи, роли `user`, `manager`, `admin`, профиль и пароль |
| `products` | виниловые пластинки, цена, остатки, жанр, лейбл, рейтинг |
| `categories` | жанры и фильтрация каталога |
| `labels` | музыкальные лейблы |
| `cart_items` | корзина пользователя |
| `orders` | заказы, доставка, оплата, скидки |
| `order_items` | снимок состава заказа |
| `reviews` | отзывы с модерацией |
| `wishlist` | избранные товары |
| `promo_codes` | процентные и фиксированные промокоды |
| `view_history` | история просмотра карточек товаров |

Файл `schema.sql` оставлен как справочная демонстрационная схема/seed для локальной проверки. Если ваша база уже создана, импортировать его не нужно.

## Структура

```text
vinyl-store/
├── app.py
├── config.py
├── vinyl_store/
│   ├── app.py
│   ├── config.py
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── middleware/
│   ├── validators/
│   └── routes/
├── templates/            # внутри vinyl_store/templates
├── static/               # внутри vinyl_store/static
│   ├── css/
│   ├── js/
│   └── images/
└── uploads/
```

### Слои приложения

- **Controllers** — только HTTP: читают request, вызывают validators/services, возвращают JSON.
- **Services** — бизнес-логика: регистрация, корзина, checkout, промокоды, модерация.
- **Repositories** — только SQL через EasyApi/PyMySQL, без ORM-моделей.
- **Middleware** — JWT, единые ошибки, логирование, стандартные JSON-ответы.
- **Validators** — проверка всех входящих JSON-полей.
- **Routes** — регистрация blueprint-ов.

## REST API

Все ответы имеют формат:

```json
{
  "success": true,
  "message": "OK",
  "data": {}
}
```

Для защищённых endpoint-ов передавайте JWT:

```http
Authorization: Bearer <token>
```

### Гость

```http
POST   /register
POST   /login
GET    /products?q=beatles&genre=rock&sort=rating
GET    /products/1
GET    /categories
GET    /reviews/1
```

### Пользователь

```http
GET    /profile
POST   /cart
GET    /cart
PUT    /cart/{product_id}
DELETE /cart/{cart_item_id}
POST   /wishlist
GET    /wishlist
DELETE /wishlist/{product_id}
POST   /orders
GET    /orders
POST   /reviews
```

### Администратор

```http
GET    /admin/stats
GET    /admin/users
GET    /admin/orders
PUT    /admin/orders/{id}
POST   /admin/products
PUT    /admin/products/{id}
DELETE /admin/products/{id}
POST   /admin/categories
PUT    /admin/categories/{id}
DELETE /admin/categories/{id}
GET    /admin/reviews
PUT    /admin/reviews/{id}
DELETE /admin/reviews/{id}
```

## Примеры API-запросов

### Регистрация

```bash
curl -X POST http://localhost:5000/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"collector","email":"collector@example.com","password":"secret123"}'
```

### Вход

```bash
curl -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"identity":"collector","password":"secret123"}'
```

### Поиск пластинок

```bash
curl 'http://localhost:5000/products?q=pink&genre=rock&sort=rating'
```

### Добавление в корзину

```bash
curl -X POST http://localhost:5000/cart \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <JWT>' \
  -d '{"product_id":1,"quantity":2}'
```

### Оформление заказа с промокодом

```bash
curl -X POST http://localhost:5000/orders \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <JWT>' \
  -d '{"shipping_address":"Nevsky Prospect, 1","shipping_city":"Saint Petersburg","customer_phone":"+79990000000","promo_code":"VINYL20"}'
```

### Создание товара администратором

```bash
curl -X POST http://localhost:5000/admin/products \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <ADMIN_JWT>' \
  -d '{"title":"Blue Train","artist":"John Coltrane","slug":"blue-train-coltrane","price":3190,"stock_quantity":7,"category_id":3,"label_id":7}'
```

## Запуск

### 1. Установить зависимости

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Настроить подключение к существующей MySQL БД

Можно использовать переменные окружения:

```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=vinyl_store
export DB_PORT=3306
export SECRET_KEY='replace-me'
```

### 3. Запустить

```bash
python app.py
```

Откройте http://localhost:5000.

## Frontend

Клиентская часть написана без React/Vue/Angular:

- HTML5 шаблон `templates/index.html`;
- CSS3 с адаптивной сеткой, ретро-шрифтами, тёмным деревом, бежевыми тонами и золотыми акцентами;
- JavaScript ES6 modules + Fetch API;
- страницы: главная, каталог, карточка товара, корзина, избранное, профиль, история заказов, вход, регистрация, админ-панель.

## Безопасность

- SQL-инъекции предотвращаются параметризованными запросами `%s` PyMySQL.
- Пароли хешируются Werkzeug `generate_password_hash`.
- JWT проверяется middleware перед защищёнными маршрутами.
- Все входящие payload-ы проходят validators.
- Исключения приводятся к единому JSON-формату middleware-обработчиком.
