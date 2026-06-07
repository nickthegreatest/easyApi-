content = open('static/js/app.js', 'r', encoding='utf-8').read()

# 1-2. Добавляем localStorage в login и register
content = content.replace(
    'state.user = data.user;\n    updateAuthUI();',
    'state.user = data.user;\n    localStorage.setItem(\"vinyl_user\", JSON.stringify(data.user));\n    updateAuthUI();'
)

# 3. Показываем пользователя сразу при загрузке
content = content.replace(
    "document.addEventListener('DOMContentLoaded', async () => {\n    await loadCurrentUser();",
    "document.addEventListener('DOMContentLoaded', async () => {\n    if (state.user) updateAuthUI();\n    await loadCurrentUser();"
)

# 4. Исправляем href на navigate
content = content.replace('href=\"/admin\"', 'href=\"#\" onclick=\"navigate(''admin''); return false\"')
content = content.replace('href=\"/orders\"', 'href=\"#\" onclick=\"navigate(''orders''); return false\"')

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed app.js')
