# Quickstart: Vintage Vinyl Store

```bash
cd /workspace/easyApi-
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DB_HOST=localhost DB_USER=root DB_PASSWORD=your_password DB_NAME=vinyl_store
python app.py
```

Откройте http://localhost:5000.

Проверка API:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/products
```
