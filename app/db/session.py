"""Conexión a la base de datos y sesión por petición."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def opciones_motor(database_url: str) -> dict:
    """Opciones del motor según la base de datos.

    - SQLite: `check_same_thread` es exclusivo de SQLite (en PostgreSQL falla).
    - PostgreSQL (Neon): Neon cierra conexiones inactivas; `pool_pre_ping` descarta
      las muertas antes de usarlas y `pool_recycle` las renueva cada 5 minutos.
    """
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True, "pool_recycle": 300}


engine = create_engine(settings.database_url, **opciones_motor(settings.database_url))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base de todos los modelos."""


def get_db() -> Iterator[Session]:
    """Dependencia de FastAPI: abre una sesión por petición y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
