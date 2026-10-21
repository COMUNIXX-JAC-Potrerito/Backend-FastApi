# Este módulo centraliza la conexión a la base de datos y expone la sesión reusable
# para los repositorios y servicios del proyecto.
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# check_same_thread es EXCLUSIVO de SQLite; en PostgreSQL rompe la conexión.
# Solo lo pasamos cuando la BD es SQLite.
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

# Crea el motor SQLAlchemy para conectar la API con la base de datos configurada.
engine = create_engine(settings.database_url, connect_args=connect_args)

# Fabrica de sesiones: genera conexiones transaccionales para cada request o operación.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base que usan todos los modelos SQLAlchemy para mapear tablas a Python.
Base = declarative_base()


# Dependency de FastAPI que abre una sesión por petición y la cierra al terminar.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()