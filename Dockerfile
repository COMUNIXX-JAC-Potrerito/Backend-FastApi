# Imagen del backend FastAPI para desplegar en Koyeb (o cualquier plataforma con Docker).
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_FROZEN=1

# uv gestiona las dependencias (igual que en local).
RUN pip install --no-cache-dir uv

WORKDIR /app

# Primero solo los archivos de dependencias, para aprovechar la caché de Docker.
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# Luego el código de la aplicación.
COPY app ./app

EXPOSE 8000

# Koyeb inyecta el puerto en la variable PORT; si no existe, usa 8000.
CMD ["sh", "-c", ".venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
