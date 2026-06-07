-- Схема БД для интернет-магазина виниловых пластинок "VinylVault"

DROP DATABASE IF EXISTS vinyl_store;
CREATE DATABASE vinyl_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vinyl_store;

-- Пользователи
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'manager', 'admin') DEFAULT 'user',
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Категории пластинок
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Производители (лейблы)
CREATE TABLE labels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    founded_year INT,
    logo_url VARCHAR(255)
);

-- Товары (виниловые пластинки)
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    artist VARCHAR(100) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    old_price DECIMAL(10, 2),
    stock_quantity INT DEFAULT 0,
    category_id INT,
    label_id INT,
    release_year INT,
    country VARCHAR(50),
    format VARCHAR(50) DEFAULT 'LP',
    weight_grams INT DEFAULT 180,
    speed_rpm ENUM('33', '45', '78') DEFAULT '33',
    color VARCHAR(50) DEFAULT 'Black',
    is_limited BOOLEAN DEFAULT FALSE,
    is_new BOOLEAN DEFAULT FALSE,
    image_url VARCHAR(255),
    image_gallery JSON,
    rating DECIMAL(3, 2) DEFAULT 0,
    review_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (label_id) REFERENCES labels(id)
);

-- Корзина
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id)
);

-- Заказы
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    payment_method ENUM('card', 'cash', 'online') DEFAULT 'card',
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    shipping_address TEXT NOT NULL,
    shipping_city VARCHAR(100),
    shipping_postal_code VARCHAR(20),
    shipping_country VARCHAR(50) DEFAULT 'Russia',
    customer_phone VARCHAR(20),
    customer_email VARCHAR(100),
    notes TEXT,
    tracking_number VARCHAR(100),
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Позиции заказа
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    artist VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(255),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Отзывы
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(200),
    content TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Избранное
CREATE TABLE wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_wishlist (user_id, product_id)
);

-- История просмотров
CREATE TABLE view_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Промокоды
CREATE TABLE promo_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    discount_type ENUM('percent', 'fixed') DEFAULT 'percent',
    discount_value DECIMAL(10, 2) NOT NULL,
    min_order_amount DECIMAL(10, 2) DEFAULT 0,
    max_uses INT DEFAULT NULL,
    used_count INT DEFAULT 0,
    valid_from DATE,
    valid_until DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для производительности
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_label ON products(label_id);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_rating ON products(rating);
CREATE INDEX idx_products_artist ON products(artist);
CREATE INDEX idx_products_release_year ON products(release_year);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_cart_user ON cart_items(user_id);

-- Демо данные: категории
INSERT INTO categories (name, slug, description) VALUES
('Rock', 'rock', 'Классический и современный рок'),
('Pop', 'pop', 'Популярная музыка всех времён'),
('Jazz', 'jazz', 'Джазовые композиции'),
('Classical', 'classical', 'Классическая музыка'),
('Electronic', 'electronic', 'Электронная музыка'),
('Hip-Hop', 'hip-hop', 'Хип-хоп и рэп'),
('Blues', 'blues', 'Блюз'),
('Soul', 'soul', 'Соул и funk'),
('Metal', 'metal', 'Метал и хард-рок'),
('Indie', 'indie', 'Инди музыка');

-- Демо данные: лейблы
INSERT INTO labels (name, country, founded_year) VALUES
('Columbia Records', 'USA', 1887),
('Capitol Records', 'USA', 1942),
('Atlantic Records', 'USA', 1947),
('Warner Bros. Records', 'USA', 1958),
('EMI', 'UK', 1931),
('Deutsche Grammophon', 'Germany', 1898),
('Blue Note Records', 'USA', 1939),
('Motown Records', 'USA', 1959),
('Sony Music', 'Japan', 1968),
('Universal Music Group', 'France', 1996);

-- Демо данные: товары
INSERT INTO products (title, artist, slug, description, price, old_price, stock_quantity, category_id, label_id, release_year, country, format, weight_grams, speed_rpm, color, is_limited, is_new, rating, image_url) VALUES
('Abbey Road', 'The Beatles', 'abbey-road-beatles', 'Легендарный альбом The Beatles, записанный на знаменитой студии Abbey Road.', 2999.00, 3499.00, 50, 1, 5, 1969, 'UK', 'LP', 180, '33', 'Black', FALSE, FALSE, 4.9, 'https://m.media-amazon.com/images/I/61rU4tGqURL._UF1000,1000_QL80_.jpg'),
('Thriller', 'Michael Jackson', 'thriller-michael-jackson', 'Самый продаваемый альбом всех времён.', 2799.00, NULL, 30, 2, 1, 1982, 'USA', 'LP', 180, '33', 'Black', FALSE, FALSE, 4.8, 'https://m.media-amazon.com/images/I/71nYSSC3tWL._UF1000,1000_QL80_.jpg'),
('Kind of Blue', 'Miles Davis', 'kind-of-blue-miles-davis', 'Величайший джазовый альбом в истории.', 3199.00, NULL, 25, 3, 7, 1959, 'USA', 'LP', 180, '33', 'Black', FALSE, FALSE, 5.0, 'https://m.media-amazon.com/images/I/71SXFqE3SQL._UF1000,1000_QL80_.jpg'),
('Dark Side of the Moon', 'Pink Floyd', 'dark-side-moon-pink-floyd', 'Культовый прогрессив-рок альбом.', 3499.00, 3999.00, 40, 1, 5, 1973, 'UK', 'LP', 180, '33', 'Black', FALSE, FALSE, 4.9, 'https://m.media-amazon.com/images/I/71lA1E+YJUL._UF1000,1000_QL80_.jpg'),
('Back to Black', 'Amy Winehouse', 'back-to-black-amy', 'Последний студийный альбом Эми Уайнхаус.', 2599.00, NULL, 35, 2, 5, 2006, 'UK', 'LP', 180, '33', 'Black', FALSE, FALSE, 4.7, 'https://m.media-amazon.com/images/I/81WYY9g8NFL._UF1000,1000_QL80_.jpg'),
('Random Access Memories', 'Daft Punk', 'random-access-memories-daft-punk', 'Грэмми-альбом электронной музыки.', 3299.00, NULL, 20, 5, 1, 2013, 'France', 'LP', 180, '33', 'Black', FALSE, FALSE, 4.8, 'https://m.media-amazon.com/images/I/81uRqfSdVJL._UF1000,1000_QL80_.jpg'),
('Nevermind', 'Nirvana', 'nevermind-nirvana', 'Альбом, изменивший музыку 90-х.', 2899.00, NULL, 45, 1, 2, 1991, 'USA', 'LP', 180, '33', 'Black', FALSE, FALSE, 4.8, 'https://m.media-amazon.com/images/I/716WjKoJ+WL._UF1000,1000_QL80_.jpg'),
('Good Kid, M.A.A.D City', 'Kendrick Lamar', 'good-kendrick-lamar', 'Дебютный студийный альбом Кендрика Ламара.', 2999.00, NULL, 25, 6, 1, 2012, 'USA', 'LP', 180, '33', 'Black', FALSE, FALSE, 4.7, 'https://m.media-amazon.com/images/I/71cVOgvystL._UF1000,1000_QL80_.jpg'),
('Rumours', 'Fleetwood Mac', 'rumours-fleetwood-mac', 'Классика рок-музыки 70-х.', 2699.00, 3199.00, 30, 1, 5, 1977, 'UK', 'LP', 180, '33', 'Black', FALSE, FALSE, 4.8, 'https://m.media-amazon.com/images/I/81rbJMqA0ZL._UF1000,1000_QL80_.jpg'),
('The Dark Side', 'Ed Sheeran', 'dark-side-ed-sheeran', 'Последний альбом Эда Ширана.', 2499.00, NULL, 50, 2, 1, 2024, 'UK', 'LP', 180, '33', 'Black', FALSE, TRUE, 4.5, 'https://m.media-amazon.com/images/I/71Ml4e8P7WL._UF1000,1000_QL80_.jpg');

-- Демо пользователь (админ)
INSERT INTO users (username, email, password, role, first_name, last_name) VALUES
('admin', 'admin@vinylvault.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.2fM8uM7fZL1K', 'admin', 'Admin', 'User'),
('manager', 'manager@vinylvault.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.2fM8uM7fZL1K', 'manager', 'Manager', 'User'),
('customer', 'customer@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.2fM8uM7fZL1K', 'user', 'John', 'Doe');

-- Промокод
INSERT INTO promo_codes (code, description, discount_type, discount_value, valid_until) VALUES
('VINYL20', 'Скидка 20% на первый заказ', 'percent', 20.00, '2026-12-31'),
('NEW2024', 'Скидка 500₽ на заказы от 5000₽', 'fixed', 500.00, '2026-06-30');
