import os

def fix_file(filepath):
    try:
        # Читаем как binary
        with open(filepath, 'rb') as f:
            raw = f.read()
        
        # Пробуем разные кодировки
        for encoding in ['utf-8', 'cp1251', 'latin-1']:
            try:
                text = raw.decode(encoding)
                if encoding != 'utf-8':
                    # Сохраняем как UTF-8
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f'Fixed {filepath} from {encoding}')
                else:
                    print(f'OK {filepath}')
                return
            except:
                continue
        print(f'SKIP {filepath}')
    except Exception as e:
        print(f'ERROR {filepath}: {e}')

# Находим все файлы
root = 'C:/Users/nickg/rest-api-lib/vinyl_store'
for dirpath, dirs, files in os.walk(root):
    for file in files:
        if file.endswith(('.py', '.html', '.js', '.css')):
            fix_file(os.path.join(dirpath, file))

