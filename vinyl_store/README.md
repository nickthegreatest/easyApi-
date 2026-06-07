# 🎵 VinylVault

Интернет-магазин виниловых пластинок на базе библиотеки **easyApi**.

## 🚀 Возможности

### Для покупателей:
- ✅ Просмотр каталога с фильтрами и сортировками (в реальном времени)
- ✅ Поиск по названию и артисту
- ✅ Регистрация и авторизация (JWT)
- ✅ Корзина товаров
- ✅ Оформление заказа с доставкой
- ✅ Фейковая оплата (95% успех)
- ✅ Просмотр истории заказов
- ✅ Отмена заказов

### Для гостей:
- ✅ Просмотр каталога
- ✅ Фильтры и сортировки
- ✅ Поиск товаров

### Для администраторов и менеджеров:
- ✅ Дашборд со статистикой
- ✅ Просмотр всех заказов
- ✅ Управление статусами заказов (админ)
- ✅ Редактирование заказов (админ)
- ✅ Удаление заказов (админ)
- ✅ Управление товарами (админ)
- ✅ Модерация отзывов (менеджер+)

## 📁 Структура проекта

```
vinyl-store/
├── app.py                 # Точка входа (Flask приложение)
├── config.py              # Конфигурация (ENV переменные)
├── schema.sql             # SQL схема БД с демо данными
├── requirements.txt       # Python зависимости
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── user.py           # Модель пользователя
│   ├── category.py       # Категории
│   ├── product.py        # Товары с фильтрами
│   ├── cart.py           # Корзина
│   ├── order.py          # Заказы
│   └── review.py         # Отзывы
├── controllers/
│   ├── __init__.py
│   ├── auth.py           # Авторизация/регистрация
│   ├── catalog.py        # Каталог товаров
│   ├── cart.py           # Корзина
│   ├── orders.py         # Заказы и оплата
│   └── admin.py          # Админ-панель
├── services/
│   └── __init__.py       # Безопасность
├── templates/
│   └── index.html        # SPA шаблон
└── static/
    ├── css/
    │   └── style.css     # Винтажный дизайн
    └── js/
        └── app.js        # Фронтенд логика
```

## 🛠 Установка

### 1. Клонирование и подготовка

```bash
cd vinyl-store
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Создание базы данных

```bash
# Войдите в MySQL
mysql -u root -p

# Создайте базу данных
CREATE DATABASE vinyl_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vinyl_store;

# Импортируйте схему с демо данными
source schema.sql;
```

### 4. Конфигурация

Скопируйте `.env.example` в `.env` и настройте:

```bash
cp .env.example .env
```

Откройте `.env` и укажите ваши параметры (особенно пароль БД):

```bash
# База данных
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=vinyl_store
```

## 🏃 Запуск

```bash
python app.py
```

Приложение будет доступно по адресу: **http://localhost:5000**

## 🔑 Тестовые учётные данные

После импорта `schema.sql` доступны:

| Роль | Username | Email | Пароль |
|------|----------|-------|--------|
| Admin | `admin` | admin@vinylvault.ru | `admin123` |
| Manager | `manager` | manager@vinylvault.ru | `manager123` |
| User | `john_doe` | john@example.com | `password123` |

## 📡 API Endpoints

### Авторизация
- `POST /api/auth/register` — Регистрация
- `POST /api/auth/login` — Вход
- `GET /api/auth/me` — Текущий пользователь
- `PUT /api/auth/profile` — Обновление профиля
- `POST /api/auth/change-password` — Смена пароля

### Каталог
- `GET /api/products` — Список товаров (с фильтрами)
- `GET /api/products/:id` — Детали товара
- `GET /api/categories` — Категории
- `GET /api/filters` — Доступные фильтры
- `GET /api/new` — Новинки
- `GET /api/bestsellers` — Популярное
- `GET /api/sale` — Со скидкой
- `GET /api/search?q=` — Поиск

### Корзина (требуется авторизация)
- `GET /api/cart/` — Получить корзину
- `POST /api/cart/add` — Добавить товар
- `POST /api/cart/update` — Обновить количество
- `POST /api/cart/remove` — Удалить товар
- `POST /api/cart/clear` — Очистить корзину

### Заказы (требуется авторизация)
- `GET /api/orders/` — Мои заказы
- `GET /api/orders/:id` — Детали заказа
- `POST /api/orders/create` — Создать заказ
- `POST /api/orders/:id/pay` — Оплатить заказ
- `POST /api/orders/:id/cancel` — Отменить заказ
- `GET /api/orders/:id/invoice` — Счёт заказа

### Админ-панель (требуется роль admin/manager)
- `GET /api/admin/dashboard` — Дашборд
- `GET /api/admin/orders` — Все заказы
- `PUT /api/admin/orders/:id/status` — Статус заказа (admin)
- `PUT /api/admin/orders/:id` — Редактировать заказ (admin)
- `DELETE /api/admin/orders/:id` — Удалить заказ (admin)
- `GET /api/admin/products` — Все товары
- `POST /api/admin/products` — Создать товар (admin)
- `PUT /api/admin/products/:id` — Обновить товар (admin)
- `DELETE /api/admin/products/:id` — Удалить товар (admin)
- `GET /api/admin/users` — Все пользователи (admin)
- `GET /api/admin/reviews/pending` — Отзывы на модерации
- `POST /api/admin/reviews/:id/approve` — Одобрить отзыв
- `POST /api/admin/reviews/:id/reject` — Отклонить отзыв

## 🎨 Дизайн

Винтажный стиль с тёплой цветовой палитрой:
- 🎨 Коричневые и бежевые тона
- 📀 Акцент на изображения пластинок
- 🎯 Интуитивная навигация
- 📱 Адаптивный дизайн (mobile-friendly)

## 📦 Используемые технологии

- **Backend:** Python 3.10+, Flask, easyApi
- **Database:** MySQL 8.0+
- **Frontend:** Vanilla JavaScript, CSS3
- **Authentication:** JWT
- **Security:** Password hashing (Werkzeug)

## 🔒 Безопасность

- ✅ Хеширование паролей
- ✅ JWT аутентификация
- ✅ Ролевая модель (user/manager/admin)
- ✅ Защита API endpoints
- ✅ Валидация входных данных
- ✅ Транзакции для заказов

## 📝 Примечания

- Оплата **фейковая** (симуляция с 95% вероятностью успеха)
- Все изображения товаров используют placeholder (замените на реальные)
- Демо данные включают 10 товаров, 3 пользователей, 2 промокода

## 🤝 Вклад в развитие

1. Fork проекта
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

## 📄 Лицензия

MIT License — свободное использование.

---

**VinylVault** © 2024. Создано с 🎵 для любителей винила.
