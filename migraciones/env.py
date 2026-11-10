"""Entorno de Alembic: a qué base conectarse y qué modelos comparar.

La URL sale de `config.attributes["url"]` cuando las migraciones se lanzan desde
la app (app/db/migrar.py) y, si no, de DATABASE_URL (comando `alembic`). No se
pasa por `alembic.ini` porque allí un "%" de la contraseña rompería la lectura.
"""

import logging

from alembic import context
from sqlalchemy import create_engine, pool, text

from app import models  # noqa: F401  (registra todas las tablas en Base.metadata)
from app.db.session import Base

config = context.config
objetivo = Base.metadata

# Número fijo para el bloqueo de PostgreSQL: dos instancias no migran a la vez.
BLOQUEO_MIGRACIONES = 728_119_001
# Si una tabla está bloqueada por otra conexión, fallar pronto en vez de colgar el despliegue.
ESPERA_MAXIMA_BLOQUEO = "15s"

# El comando `alembic` no configura logs; sin esto no mostraría qué migración aplica.
if not logging.getLogger().handlers:
    from app.core.logs import configurar_logs  # noqa: PLC0415

    configurar_logs()


def _url() -> str:
    url = config.attributes.get("url")
    if url:
        return url
    from app.core.config import settings  # noqa: PLC0415  (solo si se usa el comando `alembic`)

    return settings.database_url


def _opciones(url: str) -> dict:
    # SQLite no tiene ALTER TABLE completo: el modo "batch" recrea la tabla.
    return {"render_as_batch": url.startswith("sqlite")}


def migrar_sin_conexion() -> None:
    """Modo `--sql`: escribe el SQL en pantalla en vez de ejecutarlo."""
    url = _url()
    context.configure(url=url, target_metadata=objetivo, literal_binds=True, **_opciones(url))
    with context.begin_transaction():
        context.run_migrations()


def migrar_con_conexion() -> None:
    url = _url()
    motor = create_engine(url, poolclass=pool.NullPool)
    try:
        with motor.connect() as conexion:
            context.configure(connection=conexion, target_metadata=objetivo, **_opciones(url))
            with context.begin_transaction():
                if conexion.dialect.name == "postgresql":
                    # Ambos duran solo esta transacción (compatibles con el pooler de Neon).
                    conexion.execute(text(f"SET LOCAL lock_timeout = '{ESPERA_MAXIMA_BLOQUEO}'"))
                    conexion.execute(
                        text("SELECT pg_advisory_xact_lock(:clave)"), {"clave": BLOQUEO_MIGRACIONES}
                    )
                context.run_migrations()
    finally:
        motor.dispose()


if context.is_offline_mode():
    migrar_sin_conexion()
else:
    migrar_con_conexion()
