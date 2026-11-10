# Imagen del backend FastAPI (se despliega en Render; sirve en cualquier plataforma con Docker).
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_FROZEN=1

# uv gestiona las dependencias (igual que en local).
# Versión fija: la misma imagen se construye igual hoy y dentro de un año.
RUN pip install --no-cache-dir uv==0.12.5

WORKDIR /app

# Primero solo los archivos de dependencias, para aprovechar la caché de Docker.
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# Luego el código de la aplicación y las migraciones (se aplican solas al arrancar).
COPY app ./app
COPY alembic.ini ./
COPY migraciones ./migraciones

# La aplicación no necesita privilegios de administrador dentro del contenedor.
RUN useradd --system --no-create-home --uid 10001 comunix
USER comunix

EXPOSE 8000

# Render inyecta el puerto en la variable PORT; si no existe, usa 8000.
CMD ["sh", "-c", ".venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
