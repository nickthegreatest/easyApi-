/**
 * VinylVault — Фронтенд приложение
 */

// === Состояние ===
const state = {
    user: null,
    token: localStorage.getItem('vinyl_token'),
    cart: [],
    currentPage: 'home',
};

// === API ===
const API_BASE = '/api';

async function api(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(state.token ? { 'x-access-token': state.token } : {}),
        ...options.headers,
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'Ошибка запроса');
    }

    // Сохраняем токен при авторизации
    if (data.token) {
        state.token = data.token;
        localStorage.setItem('vinyl_token', data.token);
    }

    return data;
}

// === Авторизация ===
async function login(username, password) {
    const data = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });
    state.user = data.user;
    updateAuthUI();
    notify('Успешный вход!', 'success');
    return data;
}

async function register(username, email, password, firstName = '', lastName = '') {
    const data = await api('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, email, password, first_name: firstName, last_name: lastName }),
    });
    state.user = data.user;
    updateAuthUI();
    notify('Регистрация успешна!', 'success');
    return data;
}

function logout() {
    state.user = null;
    state.token = null;
    localStorage.removeItem('vinyl_token');
    updateAuthUI();
    notify('Вы вышли из системы', 'success');
    navigate('home');
}

async function loadCurrentUser() {
    if (!state.token) return;
    try {
        const user = await api('/auth/me');
        state.user = user;
        updateAuthUI();
    } catch (e) {
        state.token = null;
        localStorage.removeItem('vinyl_token');
    }
}

function updateAuthUI() {
    const authSection = document.getElementById('authSection');
    if (state.user) {
        const roleBadge = state.user.role !== 'user' 
            ? `<span class="badge badge-${state.user.role === 'admin' ? 'sale' : 'limited'}">${state.user.role}</span>` 
            : '';
        authSection.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="color: white;">${state.user.username} ${roleBadge}</span>
                ${state.user.role === 'admin' || state.user.role === 'manager' 
                    ? `<a href="/admin" class="btn-outline" style="padding: 8px 15px; font-size: 0.9rem;">Админ</a>` 
                    : ''}
                <a href="/orders" class="btn-outline" style="padding: 8px 15px; font-size: 0.9rem;">Заказы</a>
                <button onclick="logout()" class="btn-outline" style="padding: 8px 15px; font-size: 0.9rem;">Выйти</button>
            </div>
        `;
    } else {
        authSection.innerHTML = '<button onclick="showLoginModal()" class="btn-outline">Войти</button>';
    }
}

// === Корзина ===
async function loadCart() {
    if (!state.user) {
        document.getElementById('cartCount').textContent = '0';
        return;
    }
    try {
        const cart = await api('/cart/');
        state.cart = cart;
        updateCartCount();
    } catch (e) {
        state.cart = { items: [], total_items: 0, subtotal: 0 };
    }
}

function updateCartCount() {
    const count = state.cart.total_items || 0;
    document.getElementById('cartCount').textContent = count;
}

async function addToCart(productId, quantity = 1) {
    if (!state.user) {
        showLoginModal();
        notify('Войдите чтобы добавлять в корзину', 'error');
        return;
    }
    try {
        const data = await api('/cart/add', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity }),
        });
        state.cart = data.cart;
        updateCartCount();
        renderCartItems();
        notify('Товар добавлен в корзину', 'success');
    } catch (e) {
        notify(e.message, 'error');
    }
}

async function updateCartQuantity(productId, quantity) {
    try {
        const data = await api('/cart/update', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity }),
        });
        state.cart = data.cart;
        updateCartCount();
        renderCartItems();
    } catch (e) {
        notify(e.message, 'error');
    }
}

async function removeFromCart(productId) {
    try {
        const data = await api('/cart/remove', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId }),
        });
        state.cart = data.cart;
        updateCartCount();
        renderCartItems();
        notify('Товар удалён', 'success');
    } catch (e) {
        notify(e.message, 'error');
    }
}

function toggleCart() {
    document.getElementById('cartSidebar').classList.toggle('open');
    if (document.getElementById('cartSidebar').classList.contains('open')) {
        renderCartItems();
    }
}

function renderCartItems() {
    const container = document.getElementById('cartItems');
    const items = state.cart.items || [];
    
    if (items.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">Корзина пуста</p>';
        document.getElementById('cartTotal').innerHTML = '';
        return;
    }

    container.innerHTML = items.map(item => `
        <div class="cart-item">
            <img src="${item.image_url || 'https://via.placeholder.com/80'}" alt="${item.title}" class="cart-item-image">
            <div class="cart-item-info">
                <div class="cart-item-title">${item.title}</div>
                <div class="cart-item-artist">${item.artist}</div>
                <div class="cart-item-controls">
                    <div class="cart-quantity">
                        <button onclick="updateCartQuantity(${item.product_id}, ${item.quantity - 1})">−</button>
                        <span>${item.quantity}</span>
                        <button onclick="updateCartQuantity(${item.product_id}, ${item.quantity + 1})">+</button>
                    </div>
                    <span class="cart-item-price">${(item.price * item.quantity).toLocaleString()} ₽</span>
                    <button onclick="removeFromCart(${item.product_id})" style="margin-left: auto; background: none; border: none; cursor: pointer; color: #dc3545;">✕</button>
                </div>
            </div>
        </div>
    `).join('');

    const subtotal = state.cart.subtotal || 0;
    const shipping = subtotal >= 5000 ? 0 : 300;
    const total = subtotal + shipping;

    document.getElementById('cartTotal').innerHTML = `
        <div class="cart-total-row">
            <span>Подытог:</span>
            <span>${subtotal.toLocaleString()} ₽</span>
        </div>
        <div class="cart-total-row">
            <span>Доставка:</span>
            <span>${shipping === 0 ? 'Бесплатно' : shipping + ' ₽'}</span>
        </div>
        <div class="cart-total-row total">
            <span>Итого:</span>
            <span>${total.toLocaleString()} ₽</span>
        </div>
        <button onclick="checkout()" class="btn-checkout">Оформить заказ</button>
    `;
}

// === Оформление заказа ===
async function checkout() {
    if (!state.user) {
        showLoginModal();
        return;
    }
    if (!state.cart.items || state.cart.items.length === 0) {
        notify('Корзина пуста', 'error');
        return;
    }

    const address = prompt('Введите адрес доставки:');
    if (!address) return;
    
    const city = prompt('Город:');
    if (!city) return;

    const postalCode = prompt('Почтовый индекс:') || '';
    const phone = prompt('Телефон:', state.user.phone || '') || state.user.phone;
    const notes = prompt('Комментарий к заказу (необязательно):') || '';

    try {
        const order = await api('/orders/create', {
            method: 'POST',
            body: JSON.stringify({
                address,
                city,
                postal_code: postalCode,
                phone,
                notes,
                payment_method: 'card',
            }),
        });

        toggleCart();
        notify('Заказ создан!', 'success');
        
        // Оплата
        const payConfirm = confirm(`Заказ ${order.order.order_number} создан. Перейти к оплате?`);
        if (payConfirm) {
            await payOrder(order.order.order_id);
        }
        
        navigate('order-success', { orderNumber: order.order.order_number });
    } catch (e) {
        notify(e.message, 'error');
    }
}

async function payOrder(orderId) {
    try {
        const result = await api(`/orders/${orderId}/pay`, { method: 'POST' });
        notify(result.message || 'Оплата успешна!', 'success');
    } catch (e) {
        notify(e.message || 'Ошибка оплаты', 'error');
    }
}

// === Уведомления ===
function notify(message, type = 'info') {
    const container = document.getElementById('notifications');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// === Модальные окна ===
function showLoginModal() {
    document.getElementById('authModal').classList.add('open');
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('open');
}

// === Роутинг ===
async function navigate(page, params = {}) {
    state.currentPage = page;
    window.scrollTo(0, 0);

    const main = document.getElementById('mainContent');
    main.innerHTML = '<div class="loader"></div>';

    try {
        switch (page) {
            case 'home':
                await renderHome(main);
                break;
            case 'catalog':
                await renderCatalog(main, params);
                break;
            case 'product':
                await renderProduct(main, params.id);
                break;
            case 'orders':
                await renderOrders(main);
                break;
            case 'order-success':
                renderOrderSuccess(main, params.orderNumber);
                break;
            case 'admin':
                await renderAdmin(main);
                break;
            case 'new':
                await renderNewArrivals(main);
                break;
            case 'sale':
                await renderSale(main);
                break;
            default:
                await renderHome(main);
        }
    } catch (e) {
        main.innerHTML = `<div class="container"><div class="error" style="text-align: center; padding: 60px;">
            <h2>Ошибка</h2><p>${e.message}</p>
            <button onclick="navigate('home')" class="btn-primary" style="margin-top: 20px;">На главную</button>
        </div></div>`;
    }
}

// === Рендеринг страниц ===
async function renderHome(container) {
    const [categories, newProducts, bestsellers, saleProducts] = await Promise.all([
        api('/categories').catch(() => ({ categories: [] })),
        api('/new?limit=8').catch(() => ({ products: [] })),
        api('/bestsellers?limit=8').catch(() => ({ products: [] })),
        api('/sale?limit=8').catch(() => ({ products: [] })),
    ]);

    // Заполняем футер категориями
    const footerCategories = document.getElementById('footerCategories');
    if (footerCategories && categories.categories) {
        footerCategories.innerHTML = categories.categories.slice(0, 6).map(c => 
            `<li><a href="#" onclick="navigate('catalog', {category: ${c.id}}); return false;">${c.name}</a></li>`
        ).join('');
    }

    container.innerHTML = `
        <section class="hero">
            <div class="container">
                <h1>🎵 VinylVault</h1>
                <p>Лучшие виниловые пластинки с доставкой по всей России</p>
                <button onclick="navigate('catalog')" class="btn-primary" style="font-size: 1.1rem; padding: 15px 40px;">Перейти в каталог</button>
            </div>
        </section>

        ${newProducts.products.length > 0 ? `
        <section class="section">
            <div class="container">
                <h2 class="section-title">Новинки</h2>
                <div class="products-grid">
                    ${newProducts.products.map(p => renderProductCard(p)).join('')}
                </div>
            </div>
        </section>
        ` : ''}

        ${bestsellers.products.length > 0 ? `
        <section class="section">
            <div class="container">
                <h2 class="section-title">Популярное</h2>
                <div class="products-grid">
                    ${bestsellers.products.map(p => renderProductCard(p)).join('')}
                </div>
            </div>
        </section>
        ` : ''}

        ${saleProducts.products.length > 0 ? `
        <section class="section">
            <div class="container">
                <h2 class="section-title">Со скидкой</h2>
                <div class="products-grid">
                    ${saleProducts.products.map(p => renderProductCard(p)).join('')}
                </div>
            </div>
        </section>
        ` : ''}
    `;
}

async function renderCatalog(container, filters = {}) {
    const [filtersData, productsData] = await Promise.all([
        api('/filters').catch(() => ({ categories: [], labels: [], price_range: { min_price: 0, max_price: 10000 } })),
        api(`/products?${buildQueryString(filters)}`).catch(() => ({ products: [], pagination: {} })),
    ]);

    container.innerHTML = `
        <div class="container">
            <h1 class="section-title">Каталог</h1>
            
            <div class="filters-section">
                <div class="filters-grid">
                    <div class="filter-group">
                        <label>Категория</label>
                        <select id="filterCategory" onchange="applyFilters()">
                            <option value="">Все категории</option>
                            ${filtersData.categories.map(c => `<option value="${c.id}" ${filters.category == c.id ? 'selected' : ''}>${c.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Цена от</label>
                        <input type="number" id="filterMinPrice" value="${filters.min_price || ''}" placeholder="Мин" onchange="applyFilters()">
                    </div>
                    <div class="filter-group">
                        <label>Цена до</label>
                        <input type="number" id="filterMaxPrice" value="${filters.max_price || ''}" placeholder="Макс" onchange="applyFilters()">
                    </div>
                    <div class="filter-group">
                        <label>Сортировка</label>
                        <select id="filterSort" onchange="applyFilters()">
                            <option value="created_at:DESC" ${filters.sort === 'created_at:DESC' ? 'selected' : ''}>По дате</option>
                            <option value="price:ASC" ${filters.sort === 'price:ASC' ? 'selected' : ''}>Цена: по возрастанию</option>
                            <option value="price:DESC" ${filters.sort === 'price:DESC' ? 'selected' : ''}>Цена: по убыванию</option>
                            <option value="rating:DESC" ${filters.sort === 'rating:DESC' ? 'selected' : ''}>По рейтингу</option>
                            <option value="artist:ASC" ${filters.sort === 'artist:ASC' ? 'selected' : ''}>По артисту</option>
                        </select>
                    </div>
                    <div class="filter-group" style="display: flex; align-items: flex-end;">
                        <label style="display: flex; align-items: center; gap: 8px;">
                            <input type="checkbox" id="filterInStock" ${filters.in_stock ? 'checked' : ''} onchange="applyFilters()">
                            Только в наличии
                        </label>
                    </div>
                </div>
            </div>

            <div class="products-grid">
                ${productsData.products.length > 0 
                    ? productsData.products.map(p => renderProductCard(p)).join('')
                    : '<p style="grid-column: 1/-1; text-align: center; padding: 60px; color: #666;">Товары не найдены</p>'
                }
            </div>

            ${productsData.pagination && productsData.pagination.pages > 1 ? `
            <div class="pagination">
                ${Array.from({ length: productsData.pagination.pages }, (_, i) => i + 1)
                    .map(page => `<button ${page === productsData.pagination.page ? 'class="active"' : ''} onclick="applyFilters(${page})">${page}</button>`)
                    .join('')}
            </div>
            ` : ''}
        </div>
    `;
}

async function renderProduct(container, productId) {
    const product = await api(`/products/${productId}`);
    
    container.innerHTML = `
        <div class="container" style="padding: 40px 20px;">
            <button onclick="window.history.back()" class="btn-secondary" style="margin-bottom: 30px;">← Назад</button>
            
            <div class="product-detail">
                <img src="${product.image_url || 'https://via.placeholder.com/500'}" alt="${product.title}" class="product-detail-image">
                
                <div class="product-detail-info">
                    ${product.is_new ? '<span class="badge badge-new">Новинка</span>' : ''}
                    ${product.is_limited ? '<span class="badge badge-limited">Лимитированное</span>' : ''}
                    ${product.old_price ? '<span class="badge badge-sale">Скидка</span>' : ''}
                    
                    <h1>${product.title}</h1>
                    <p class="product-detail-artist">${product.artist}</p>
                    
                    <div class="product-detail-price">
                        ${product.price.toLocaleString()} ₽
                        ${product.old_price ? `<span class="product-old-price">${product.old_price.toLocaleString()} ₽</span>` : ''}
                    </div>
                    
                    <p class="product-detail-description">${product.description || 'Описание отсутствует'}</p>
                    
                    <div class="product-detail-specs">
                        ${product.release_year ? `<div class="spec-item"><span class="spec-label">Год выпуска</span><span class="spec-value">${product.release_year}</span></div>` : ''}
                        ${product.country ? `<div class="spec-item"><span class="spec-label">Страна</span><span class="spec-value">${product.country}</span></div>` : ''}
                        ${product.format ? `<div class="spec-item"><span class="spec-label">Формат</span><span class="spec-value">${product.format}</span></div>` : ''}
                        ${product.weight_grams ? `<div class="spec-item"><span class="spec-label">Вес</span><span class="spec-value">${product.weight_grams}g</span></div>` : ''}
                        ${product.speed_rpm ? `<div class="spec-item"><span class="spec-label">Скорость</span><span class="spec-value">${product.speed_rpm} RPM</span></div>` : ''}
                        ${product.color ? `<div class="spec-item"><span class="spec-label">Цвет</span><span class="spec-value">${product.color}</span></div>` : ''}
                    </div>
                    
                    <div style="display: flex; gap: 15px;">
                        <button onclick="addToCart(${product.id})" class="btn-primary" style="flex: 1; padding: 15px;">
                            ${product.stock_quantity > 0 ? 'Добавить в корзину' : 'Нет в наличии'}
                        </button>
                    </div>
                    
                    ${product.stock_quantity > 0 
                        ? `<p style="color: var(--success); margin-top: 15px;">✓ В наличии: ${product.stock_quantity} шт.</p>`
                        : `<p style="color: var(--danger); margin-top: 15px;">✕ Нет в наличии</p>`
                    }
                </div>
            </div>

            ${product.reviews && product.reviews.length > 0 ? `
            <div style="margin-top: 60px;">
                <h2 class="section-title">Отзывы (${product.review_stats?.total || 0})</h2>
                ${product.reviews.map(r => `
                    <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: var(--shadow);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <strong>${r.username || r.first_name || 'Аноним'}</strong>
                            <span>${'★'.repeat(r.rating)}${'☆'.repeat(5-r.rating)}</span>
                        </div>
                        ${r.title ? `<h4 style="margin-bottom: 10px;">${r.title}</h4>` : ''}
                        <p style="color: #666;">${r.content}</p>
                        <small style="color: #999;">${new Date(r.created_at).toLocaleDateString('ru-RU')}</small>
                    </div>
                `).join('')}
            </div>
            ` : ''}
        </div>
    `;
}

async function renderOrders(container) {
    if (!state.user) {
        navigate('home');
        return;
    }

    const orders = await api('/orders/');
    
    container.innerHTML = `
        <div class="container" style="padding: 40px 20px;">
            <h1 class="section-title">Мои заказы</h1>
            
            ${orders.orders && orders.orders.length > 0 
                ? `<div class="data-table" style="margin-top: 30px;">
                    <table>
                        <thead>
                            <tr>
                                <th>№ заказа</th>
                                <th>Дата</th>
                                <th>Сумма</th>
                                <th>Статус</th>
                                <th>Оплата</th>
                                <th>Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${orders.orders.map(o => `
                                <tr>
                                    <td><strong>${o.order_number}</strong></td>
                                    <td>${new Date(o.created_at).toLocaleDateString('ru-RU')}</td>
                                    <td>${o.total_amount.toLocaleString()} ₽</td>
                                    <td><span class="status-badge status-${o.status}">${translateStatus(o.status)}</span></td>
                                    <td><span class="status-badge status-${o.payment_status === 'paid' ? 'confirmed' : o.payment_status}">${translateStatus(o.payment_status)}</span></td>
                                    <td class="actions">
                                        <button onclick="viewOrder(${o.id})" class="btn-small btn-edit">Подробнее</button>
                                        ${o.status === 'pending' || o.status === 'confirmed' 
                                            ? `<button onclick="cancelOrder(${o.id})" class="btn-small btn-delete">Отменить</button>` 
                                            : ''}
                                        ${o.payment_status === 'pending' && o.status !== 'cancelled'
                                            ? `<button onclick="payOrder(${o.id})" class="btn-small btn-primary">Оплатить</button>`
                                            : ''}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>`
                : `<div style="text-align: center; padding: 60px; color: #666;">
                    <h3>У вас пока нет заказов</h3>
                    <button onclick="navigate('catalog')" class="btn-primary" style="margin-top: 20px;">Перейти в каталог</button>
                </div>`
            }
        </div>
    `;
}

function renderOrderSuccess(container, orderNumber) {
    container.innerHTML = `
        <div class="container">
            <div class="order-success">
                <div class="order-success-icon">🎉</div>
                <h1>Заказ оформлен!</h1>
                <p class="order-number">${orderNumber}</p>
                <p style="color: #666; margin-bottom: 30px;">Спасибо за покупку! Мы свяжемся с вами для подтверждения.</p>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button onclick="navigate('orders')" class="btn-primary">Мои заказы</button>
                    <button onclick="navigate('catalog')" class="btn-secondary">Продолжить покупки</button>
                </div>
            </div>
        </div>
    `;
}

async function renderAdmin(container) {
    if (!state.user || (state.user.role !== 'admin' && state.user.role !== 'manager')) {
        notify('Доступ запрещён', 'error');
        navigate('home');
        return;
    }

    const [dashboard, orders] = await Promise.all([
        api('/admin/dashboard').catch(() => ({})),
        api('/admin/orders?per_page=10').catch(() => ({ orders: [] })),
    ]);

    container.innerHTML = `
        <div class="container" style="padding: 40px 20px;">
            <h1 class="section-title">Админ-панель</h1>
            <p style="text-align: center; color: #666; margin-bottom: 40px;">
                ${state.user.username} (${state.user.role})
            </p>

            <div class="admin-dashboard">
                <div class="stat-card">
                    <h3>Всего заказов</h3>
                    <div class="value">${dashboard.orders?.total_orders || 0}</div>
                </div>
                <div class="stat-card">
                    <h3>Выручка</h3>
                    <div class="value">${(dashboard.orders?.total_revenue || 0).toLocaleString()} ₽</div>
                </div>
                <div class="stat-card">
                    <h3>Средний чек</h3>
                    <div class="value">${(dashboard.orders?.avg_order_value || 0).toLocaleString()} ₽</div>
                </div>
                <div class="stat-card">
                    <h3>В ожидании</h3>
                    <div class="value">${dashboard.orders?.pending_count || 0}</div>
                </div>
            </div>

            <h2 style="margin-bottom: 20px;">Последние заказы</h2>
            <div class="data-table">
                <table>
                    <thead>
                        <tr>
                            <th>№ заказа</th>
                            <th>Клиент</th>
                            <th>Сумма</th>
                            <th>Статус</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${orders.orders && orders.orders.length > 0 
                            ? orders.orders.map(o => `
                                <tr>
                                    <td>${o.order_number}</td>
                                    <td>${o.customer_email || 'N/A'}</td>
                                    <td>${o.total_amount.toLocaleString()} ₽</td>
                                    <td><span class="status-badge status-${o.status}">${translateStatus(o.status)}</span></td>
                                    <td class="actions">
                                        <button onclick="adminViewOrder(${o.id})" class="btn-small btn-edit">Просмотр</button>
                                    </td>
                                </tr>
                            `).join('')
                            : '<tr><td colspan="5" style="text-align: center; padding: 40px;">Заказов нет</td></tr>'
                        }
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

async function renderNewArrivals(container) {
    const data = await api('/new?limit=20');
    renderProductsPage(container, 'Новинки', data.products);
}

async function renderSale(container) {
    const data = await api('/sale?limit=20');
    renderProductsPage(container, 'Со скидкой', data.products);
}

function renderProductsPage(container, title, products) {
    container.innerHTML = `
        <div class="container">
            <h1 class="section-title">${title}</h1>
            <div class="products-grid">
                ${products && products.length > 0 
                    ? products.map(p => renderProductCard(p)).join('')
                    : '<p style="grid-column: 1/-1; text-align: center; padding: 60px; color: #666;">Товары не найдены</p>'
                }
            </div>
        </div>
    `;
}

function renderProductCard(product) {
    const badges = [];
    if (product.is_new) badges.push('<span class="badge badge-new">New</span>');
    if (product.is_limited) badges.push('<span class="badge badge-limited">Limited</span>');
    if (product.old_price) badges.push('<span class="badge badge-sale">Sale</span>');

    return `
        <div class="product-card" onclick="navigate('product', {id: ${product.id}})">
            <img src="${product.image_url || 'https://via.placeholder.com/300'}" alt="${product.title}" class="product-image" loading="lazy">
            <div class="product-info">
                ${badges.length > 0 ? `<div style="margin-bottom: 10px;">${badges.join(' ')}</div>` : ''}
                <h3 class="product-title">${product.title}</h3>
                <p class="product-artist">${product.artist}</p>
                <div class="product-footer">
                    <div>
                        <span class="product-price">${product.price.toLocaleString()} ₽</span>
                        ${product.old_price ? `<span class="product-old-price">${product.old_price.toLocaleString()} ₽</span>` : ''}
                    </div>
                    <button onclick="event.stopPropagation(); addToCart(${product.id})" class="btn-add-cart">В корзину</button>
                </div>
            </div>
        </div>
    `;
}

// === Утилиты ===
function buildQueryString(filters) {
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.in_stock) params.append('in_stock', '1');
    if (filters.sort) {
        const [sortBy, sortOrder] = filters.sort.split(':');
        params.append('sort', sortBy);
        params.append('order', sortOrder);
    }
    if (filters.page) params.append('page', filters.page);
    if (filters.search) params.append('search', filters.search);
    return params.toString();
}

function applyFilters(page = 1) {
    const filters = {
        category: document.getElementById('filterCategory')?.value || null,
        min_price: document.getElementById('filterMinPrice')?.value || null,
        max_price: document.getElementById('filterMaxPrice')?.value || null,
        in_stock: document.getElementById('filterInStock')?.checked || false,
        sort: document.getElementById('filterSort')?.value || 'created_at:DESC',
        page: page,
    };
    navigate('catalog', filters);
}

function search() {
    const query = document.getElementById('searchInput').value.trim();
    if (query.length >= 2) {
        navigate('catalog', { search: query });
    }
}

function translateStatus(status) {
    const statuses = {
        pending: 'В ожидании',
        confirmed: 'Подтверждён',
        processing: 'В обработке',
        shipped: 'Отправлен',
        delivered: 'Доставлен',
        cancelled: 'Отменён',
        refunded: 'Возвращён',
        paid: 'Оплачен',
        failed: 'Не оплачен',
    };
    return statuses[status] || status;
}

async function viewOrder(orderId) {
    // TODO: реализовать просмотр деталей заказа
    notify('Функция в разработке', 'info');
}

async function cancelOrder(orderId) {
    if (!confirm('Отменить заказ?')) return;
    try {
        await api(`/orders/${orderId}/cancel`, { method: 'POST' });
        notify('Заказ отменён', 'success');
        navigate('orders');
    } catch (e) {
        notify(e.message, 'error');
    }
}

async function adminViewOrder(orderId) {
    notify('Функция в разработке', 'info');
}

// === Инициализация ===
document.addEventListener('DOMContentLoaded', async () => {
    await loadCurrentUser();
    await loadCart();
    
    // Обработчики форм
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        try {
            await login(username, password);
            closeAuthModal();
        } catch (e) {
            document.getElementById('loginError').textContent = e.message;
        }
    });

    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const firstName = document.getElementById('regFirstName').value;
        const lastName = document.getElementById('regLastName').value;
        try {
            await register(username, email, password, firstName, lastName);
            closeAuthModal();
        } catch (e) {
            document.getElementById('registerError').textContent = e.message;
        }
    });

    // Переключение табов авторизации
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const tabName = tab.dataset.tab;
            document.getElementById('loginForm').classList.toggle('hidden', tabName !== 'login');
            document.getElementById('registerForm').classList.toggle('hidden', tabName !== 'register');
        });
    });

    // Поиск по Enter
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') search();
    });

    // Роутинг
    navigate('home');
});
