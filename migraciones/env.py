"""Entorno de Alembic: a qué base conectarse y qué modelos comparar.

La URL sale de `config.attributes["url"]` cuando las migraciones se lanzan desde
la app (app/db/migrar.py) y, si no, de DATABASE_URL (comando `alembic`). No se
pasa por `alembic.ini` porque allí un "%" de la contraseña rompería la lectura.
"""

from alembic import context
from sqlalchemy import create_engine, pool

from app import models  # noqa: F401  (registra todas las tablas en Base.metadata)
from app.db.session import Base

config = context.config
objetivo = Base.metadata


def _url() -> str:
    url = config.attributes.get("url")
    if url:
        return url
    from app.core.config import settings  # noqa: PLC0415  (solo si se usa el comando `alembic`)

    return settings.database_url


def _opciones(url: str) -> dict:
    # SQLite no tiene ALTER TABLE completo: el modo "batch" recrea la tabla.
    return {"render_as_batch": url.startswith("sqlite"), "compare_type": True}


def migrar_sin_conexion() -> None:
    """Modo `--sql`: escribe el SQL en pantalla en vez de ejecutarlo."""
    url = _url()
    context.configure(url=url, target_metadata=objetivo, literal_binds=True, **_opciones(url))
    with context.begin_transaction():
        context.run_migrations()


def migrar_con_conexion() -> None:
    url = _url()
    motor = create_engine(url, poolclass=pool.NullPool)
    with motor.connect() as conexion:
        context.configure(connection=conexion, target_metadata=objetivo, **_opciones(url))
        with context.begin_transaction():
            context.run_migrations()
    motor.dispose()


if context.is_offline_mode():
    migrar_sin_conexion()
else:
    migrar_con_conexion()
