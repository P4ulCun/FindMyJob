# ───────────────────────── base (dependențe comune) ─────────────────────────
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-db.sh /scripts/wait-for-db.sh
RUN chmod +x /scripts/wait-for-db.sh

# ───────────────────────── dev ─────────────────────────
# Codul vine prin volume mount; comanda (runserver) e în docker-compose.yml
FROM base AS dev

COPY requirements-dev.txt /app/
RUN pip install --no-cache-dir -r requirements-dev.txt

# ───────────────────────── prod ─────────────────────────
FROM base AS prod

# Copiem efectiv codul aplicației în imagine
COPY app/ /app/

# Colectăm fișierele statice (admin etc.) la build — nu necesită DB
RUN python manage.py collectstatic --noinput

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]