"""Aplica las migraciones pendientes de la base de datos (Alembic).

Se ejecuta al arrancar la app. Una base creada antes de existir las migraciones
(con `create_all`, como la de Neon hasta la v1.2.0) tiene las tablas pero no un
registro en `alembic_version`. Si su esquema está completo, se marca como que ya
está en la revisión base, sin tocar nada, y desde ahí se aplican las siguientes.
Si está incompleta, se detiene el arranque: marcarla ocultaría lo que le falta.

Uso manual: `uv run python -m app.db.migrar`
"""

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import Engine, create_engine, inspect

from app import models  # noqa: F401  (registra todas las tablas en Base.metadata)
from app.db.session import Base, opciones_motor

logger = logging.getLogger(__name__)

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
# Revisión que describe el esquema creado por create_all en la v1.2.0.
REVISION_BASE = "0001"


class EsquemaIncompleto(RuntimeError):
    """La base tiene tablas propias, sin registro de migraciones y con partes faltantes."""


def config_alembic(url: str) -> Config:
    config = Config(str(RAIZ_PROYECTO / "alembic.ini"))
    config.set_main_option("script_location", str(RAIZ_PROYECTO / "migraciones"))
    config.attributes["url"] = url
    return config


def _faltantes(motor: Engine, tablas: set[str]) -> list[str]:
    """Tablas y columnas del esquema base que no están en la base.

    Las migraciones posteriores a la base no agregan tablas ni columnas (solo un
    índice), así que el esquema base es el de los modelos actuales.
    """
    inspector = inspect(motor)
    faltan = []
    for nombre, tabla in Base.metadata.tables.items():
        if nombre not in tablas:
            faltan.append(nombre)
            continue
        existentes = {columna["name"] for columna in inspector.get_columns(nombre)}
        faltan.extend(f"{nombre}.{c.name}" for c in tabla.columns if c.name not in existentes)
    return faltan


def _necesita_marca(motor: Engine) -> bool:
    """True si la base ya tiene el esquema base pero ninguna revisión registrada."""
    tablas = set(inspect(motor).get_table_names())
    with motor.connect() as conexion:
        revision = MigrationContext.configure(conexion).get_current_revision()
    propias = tablas & set(Base.metadata.tables)
    if revision is not None or not propias:
        return False  # ya registrada, o base vacía: upgrade normal desde cero
    faltan = _faltantes(motor, tablas)
    if faltan:
        raise EsquemaIncompleto(
            "La base tiene tablas sin registro de migraciones y le faltan: "
            f"{', '.join(faltan)}. Revisa a mano (ver docs/migraciones.md)."
        )
    return True


def migrar(url: str | None = None) -> None:
    """Lleva la base a la última revisión (no hace nada si ya está al día)."""
    if url is None:
        from app.core.config import settings  # noqa: PLC0415

        url = settings.database_url
    config = config_alembic(url)
    motor = create_engine(url, **opciones_motor(url))
    try:
        marcar = _necesita_marca(motor)
    finally:
        motor.dispose()
    if marcar:
        logger.info("Base sin registro de migraciones: se marca en la revisión %s", REVISION_BASE)
        command.stamp(config, REVISION_BASE)
    command.upgrade(config, "head")


if __name__ == "__main__":
    from app.core.logs import configurar_logs  # noqa: PLC0415

    configurar_logs()
    migrar()
