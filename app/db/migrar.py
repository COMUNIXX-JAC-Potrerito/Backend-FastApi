"""Aplica las migraciones pendientes de la base de datos (Alembic).

Se ejecuta al arrancar la app. Una base creada antes de existir las migraciones
(con `create_all`, como la de Neon hasta la v1.2.0) tiene las tablas pero no la
tabla `alembic_version`: se marca como que ya está en la revisión base, sin
tocar nada, y desde ahí se aplican las migraciones siguientes.

Uso manual: `uv run python -m app.db.migrar`
"""

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.db.session import opciones_motor

logger = logging.getLogger(__name__)

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
# Revisión que describe el esquema creado por create_all en la v1.2.0.
REVISION_BASE = "0001"
# Si existe esta tabla, la base ya tenía el esquema anterior a las migraciones.
TABLA_DE_REFERENCIA = "users"


def config_alembic(url: str) -> Config:
    config = Config(str(RAIZ_PROYECTO / "alembic.ini"))
    config.set_main_option("script_location", str(RAIZ_PROYECTO / "migraciones"))
    config.attributes["url"] = url
    return config


def _tablas(url: str) -> set[str]:
    motor = create_engine(url, **opciones_motor(url))
    try:
        return set(inspect(motor).get_table_names())
    finally:
        motor.dispose()


def migrar(url: str | None = None) -> None:
    """Lleva la base a la última revisión (no hace nada si ya está al día)."""
    if url is None:
        from app.core.config import settings  # noqa: PLC0415  (evita leer el .env al importar)

        url = settings.database_url
    config = config_alembic(url)
    tablas = _tablas(url)
    if TABLA_DE_REFERENCIA in tablas and "alembic_version" not in tablas:
        logger.info("Base sin registro de migraciones: se marca en la revisión %s", REVISION_BASE)
        command.stamp(config, REVISION_BASE)
    command.upgrade(config, "head")


if __name__ == "__main__":
    from app.core.logs import configurar_logs  # noqa: PLC0415

    configurar_logs()
    migrar()
