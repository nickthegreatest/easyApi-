const state = {
  token: localStorage.getItem('vv_token'),
  user: JSON.parse(localStorage.getItem('vv_user') || 'null'),
  products: [],
  categories: [],
  cart: { items: [], total_items: 0, subtotal: 0 },
  activeProduct: null,
};

const money = value => `${Number(value || 0).toLocaleString('ru-RU')} ₽`;
const qs = selector => document.querySelector(selector);

async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.success === false) {
    throw new Error(payload.message || `HTTP ${response.status}`);
  }
  return payload.data;
}

function notify(message, type = 'success') {
  const toast = qs('#toast');
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  setTimeout(() => toast.className = 'toast', 3200);
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function setSession(data) {
  state.token = data.token;
  state.user = data.user;
  localStorage.setItem('vv_token', data.token);
  localStorage.setItem('vv_user', JSON.stringify(data.user));
  renderAuth();
}

function logout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem('vv_token');
  localStorage.removeItem('vv_user');
  renderAuth();
  notify('Вы вышли из аккаунта');
  location.hash = '#home';
}

function showPage() {
  const id = (location.hash || '#home').slice(1);
  document.querySelectorAll('.page').forEach(page => page.classList.toggle('active', page.id === id));
  if (id === 'cart') loadCart();
  if (id === 'wishlist') loadWishlist();
  if (id === 'profile') loadProfile();
  if (id === 'admin') loadAdmin();
}

function renderAuth() {
  const actions = qs('#authActions');
  qs('#adminLink').hidden = !state.user || state.user.role !== 'admin';
  if (!state.user) {
    actions.innerHTML = '<a class="button ghost" href="#login">Войти</a>';
    return;
  }
  actions.innerHTML = `<span>${state.user.username}</span><button class="button ghost" id="logoutBtn">Выйти</button>`;
  qs('#logoutBtn').addEventListener('click', logout);
}

async function loadCategories() {
  state.categories = await api('/categories');
  qs('#categorySelect').innerHTML = '<option value="">Все жанры</option>' +
    state.categories.map(category => `<option value="${category.slug}">${category.name}</option>`).join('');
}

async function loadProducts() {
  const params = new URLSearchParams();
  const q = qs('#searchInput').value.trim();
  const genre = qs('#categorySelect').value;
  const sort = qs('#sortSelect').value;
  if (q) params.set('q', q);
  if (genre) params.set('genre', genre);
  if (sort) params.set('sort', sort);
  state.products = await api(`/products?${params}`);
  renderProducts();
}

function renderProducts() {
  qs('#productGrid').innerHTML = state.products.map(product => `
    <article class="product-card">
      <img src="${product.image_url || '/static/images/placeholder.svg'}" alt="${product.title}">
      <div class="content">
        ${product.is_limited ? '<span class="badge">Limited</span>' : ''}
        <h3>${product.title}</h3>
        <p>${product.artist} · ${product.release_year || '—'} · ${product.category_name || 'Vinyl'}</p>
        <div><span class="price">${money(product.price)}</span>${product.old_price ? `<span class="old-price">${money(product.old_price)}</span>` : ''}</div>
        <div>★ ${Number(product.rating || 0).toFixed(1)} · Остаток: ${product.stock_quantity}</div>
        <div class="card-actions">
          <button class="button primary" data-product="${product.id}">Подробнее</button>
          <button class="icon-btn" data-wish="${product.id}" title="В избранное">♡</button>
        </div>
      </div>
    </article>
  `).join('');
  document.querySelectorAll('[data-product]').forEach(btn => btn.addEventListener('click', () => openProduct(btn.dataset.product)));
  document.querySelectorAll('[data-wish]').forEach(btn => btn.addEventListener('click', () => addWishlist(btn.dataset.wish)));
}

async function openProduct(id) {
  const product = await api(`/products/${id}`);
  state.activeProduct = product;
  qs('#productDetails').innerHTML = `
    <img src="${product.image_url || '/static/images/placeholder.svg'}" alt="${product.title}">
    <div class="details-copy">
      <p class="eyebrow">${product.category_name || 'vinyl record'}</p>
      <h2>${product.title}</h2>
      <h3>${product.artist}</h3>
      <p>${product.description || ''}</p>
      <p>Лейбл: ${product.label_name || '—'} · ${product.country || '—'} · ${product.format || 'LP'} · ${product.speed_rpm || 33} RPM</p>
      <p class="price">${money(product.price)}</p>
      <button class="button primary" id="addCartBtn">В корзину</button>
      <button class="button ghost" id="addWishBtn">В избранное</button>
    </div>`;
  qs('#addCartBtn').addEventListener('click', () => addCart(product.id));
  qs('#addWishBtn').addEventListener('click', () => addWishlist(product.id));
  await loadReviews(product.id);
  location.hash = '#product';
}

async function addCart(productId) {
  if (!state.token) return location.hash = '#login';
  state.cart = await api('/cart', { method: 'POST', body: JSON.stringify({ product_id: Number(productId), quantity: 1 }) });
  qs('#cartCount').textContent = state.cart.total_items;
  notify('Пластинка добавлена в корзину');
}

async function loadCart() {
  if (!state.token) { qs('#cartView').innerHTML = 'Войдите, чтобы увидеть корзину.'; return; }
  state.cart = await api('/cart');
  qs('#cartCount').textContent = state.cart.total_items;
  qs('#cartView').innerHTML = state.cart.items.length ? state.cart.items.map(item => `
    <div class="cart-row">
      <img src="${item.image_url || '/static/images/placeholder.svg'}" alt="${item.title}">
      <div><b>${item.title}</b><br>${item.artist}<br>${item.quantity} × ${money(item.price)}</div>
      <button class="icon-btn" data-remove-cart="${item.id}">×</button>
    </div>`).join('') + `<h3>Итого: ${money(state.cart.subtotal)}</h3>` : 'Корзина пуста.';
  document.querySelectorAll('[data-remove-cart]').forEach(btn => btn.addEventListener('click', () => removeCart(btn.dataset.removeCart)));
}

async function removeCart(itemId) {
  state.cart = await api(`/cart/${itemId}`, { method: 'DELETE' });
  notify('Товар удалён');
  loadCart();
}

async function addWishlist(productId) {
  if (!state.token) return location.hash = '#login';
  await api('/wishlist', { method: 'POST', body: JSON.stringify({ product_id: Number(productId) }) });
  notify('Добавлено в избранное');
}

async function loadWishlist() {
  if (!state.token) { qs('#wishlistView').innerHTML = '<div class="panel">Войдите, чтобы увидеть избранное.</div>'; return; }
  const items = await api('/wishlist');
  qs('#wishlistView').innerHTML = items.map(item => `
    <article class="product-card"><img src="${item.image_url || '/static/images/placeholder.svg'}" alt="${item.title}"><div class="content"><h3>${item.title}</h3><p>${item.artist}</p><p class="price">${money(item.price)}</p><button class="button primary" data-product="${item.product_id}">Открыть</button></div></article>
  `).join('') || '<div class="panel">Избранное пусто.</div>';
  document.querySelectorAll('[data-product]').forEach(btn => btn.addEventListener('click', () => openProduct(btn.dataset.product)));
}

async function loadProfile() {
  if (!state.token) { location.hash = '#login'; return; }
  const profile = await api('/profile');
  const orders = await api('/orders');
  qs('#profileView').innerHTML = `<h3>${profile.username}</h3><p>${profile.email}</p><p>Роль: ${profile.role}</p><p>${profile.first_name || ''} ${profile.last_name || ''}</p>`;
  qs('#ordersView').innerHTML = orders.map(order => `<div class="panel order-card"><b>${order.order_number}</b><span>${order.status}</span><span>${money(order.total_amount)}</span><small>${order.created_at}</small></div>`).join('') || '<div class="panel">Заказов пока нет.</div>';
}

async function loadReviews(productId) {
  const reviews = await api(`/reviews/${productId}`);
  qs('#reviewsList').innerHTML = reviews.map(review => `<div class="cart-row"><div>★ ${review.rating}</div><div><b>${review.title || 'Отзыв'}</b><br>${review.content}<br><small>${review.username}</small></div></div>`).join('') || '<p>Отзывов пока нет.</p>';
}

async function loadAdmin() {
  if (!state.user || state.user.role !== 'admin') { location.hash = '#home'; return; }
  const [stats, orders, reviews] = await Promise.all([api('/admin/stats'), api('/admin/orders'), api('/admin/reviews')]);
  qs('#adminStats').innerHTML = `
    <div class="stat"><b>Заказы</b><h3>${stats.sales.totals.orders_count}</h3></div>
    <div class="stat"><b>Выручка</b><h3>${money(stats.sales.totals.revenue)}</h3></div>
    <div class="stat"><b>Средний чек</b><h3>${money(stats.sales.totals.average_order)}</h3></div>`;
  qs('#adminOrders').innerHTML = orders.slice(0, 10).map(order => `<div class="admin-row"><b>${order.order_number}</b><span>${order.username} · ${money(order.total_amount)} · ${order.status}</span></div>`).join('');
  qs('#adminReviews').innerHTML = reviews.slice(0, 10).map(review => `<div class="admin-row"><b>${review.product_title}</b><span>${review.username}: ${review.content}</span><button class="button primary" data-approve="${review.id}">Одобрить</button></div>`).join('');
  document.querySelectorAll('[data-approve]').forEach(btn => btn.addEventListener('click', async () => {
    await api(`/admin/reviews/${btn.dataset.approve}`, { method: 'PUT', body: JSON.stringify({ is_approved: true }) });
    notify('Отзыв одобрен');
    loadAdmin();
  }));
}

qs('#applyFilters').addEventListener('click', loadProducts);
qs('#loginForm').addEventListener('submit', async event => {
  event.preventDefault();
  try { setSession(await api('/login', { method: 'POST', body: JSON.stringify(formData(event.target)) })); notify('Добро пожаловать!'); location.hash = '#catalog'; }
  catch (error) { notify(error.message, 'error'); }
});
qs('#registerForm').addEventListener('submit', async event => {
  event.preventDefault();
  try { setSession(await api('/register', { method: 'POST', body: JSON.stringify(formData(event.target)) })); notify('Аккаунт создан'); location.hash = '#catalog'; }
  catch (error) { notify(error.message, 'error'); }
});
qs('#checkoutForm').addEventListener('submit', async event => {
  event.preventDefault();
  try { await api('/orders', { method: 'POST', body: JSON.stringify(formData(event.target)) }); notify('Заказ оформлен'); event.target.reset(); await loadCart(); location.hash = '#profile'; }
  catch (error) { notify(error.message, 'error'); }
});
qs('#reviewForm').addEventListener('submit', async event => {
  event.preventDefault();
  if (!state.activeProduct) return;
  try { await api('/reviews', { method: 'POST', body: JSON.stringify({ ...formData(event.target), product_id: state.activeProduct.id }) }); notify('Отзыв отправлен на модерацию'); event.target.reset(); }
  catch (error) { notify(error.message, 'error'); }
});
qs('#productForm').addEventListener('submit', async event => {
  event.preventDefault();
  const data = formData(event.target);
  ['price', 'stock_quantity', 'category_id', 'label_id', 'release_year'].forEach(key => { if (data[key] === '') delete data[key]; else data[key] = Number(data[key]); });
  try { await api('/admin/products', { method: 'POST', body: JSON.stringify(data) }); notify('Товар добавлен'); event.target.reset(); loadProducts(); }
  catch (error) { notify(error.message, 'error'); }
});

window.addEventListener('hashchange', showPage);
renderAuth();
loadCategories().then(loadProducts).catch(error => notify(error.message, 'error'));
if (state.token) loadCart().catch(() => {});
showPage();
