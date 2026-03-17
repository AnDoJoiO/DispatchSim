# ── Build frontend ────────────────────────────────────────
FROM node:20-alpine AS frontend
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
# Vite output → /build/app/static/ (outDir: '../app/static')

# ── Python runtime ────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# Built frontend assets from stage 1
COPY --from=frontend /build/app/static/ app/static/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
