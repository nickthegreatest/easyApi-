-- Быстрая инициализация базы данных VinylVault
-- Запуск: mysql -u root -p < setup_db.sql

-- Создаём базу данных
CREATE DATABASE IF NOT EXISTS vinyl_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Используем базу данных
USE vinyl_store;

-- Импортируем схему и данные
SOURCE schema.sql;

-- Выводим сообщение
SELECT '✅ База данных VinylVault успешно создана!' AS message;
SELECT '📊 Таблицы:' AS info;
SHOW TABLES;
