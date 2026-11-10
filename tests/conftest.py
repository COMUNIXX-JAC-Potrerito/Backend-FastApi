"""Fixtures compartidas de la suite.

Las variables de entorno se fijan ANTES de importar la app: así la configuración
nunca lee la base de datos real del `.env` (Neon) ni credenciales de Cloudinary.
Las variables de entorno tienen prioridad sobre el archivo `.env`.
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "clave-exclusiva-de-pruebas-0123456789abcdef"
os.environ["CLOUDINARY_URL"] = "cloudinary://123456:secreto-de-pruebas@nube-pruebas"
os.environ["CORS_ORIGINS"] = "http://localhost:4200"
for _variable in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"):
    os.environ.pop(_variable, None)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.limites import reiniciar_limitadores  # noqa: E402
from app.db.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.auth.roles import ROL_ADMIN, ROL_SUPERADMIN, ROL_USUARIO  # noqa: E402
from app.services.auth.seguridad import hash_password  # noqa: E402
from app.services.auth.tokens import create_access_token  # noqa: E402

CLAVE_PRUEBA = "Clave1234"
# bcrypt es lento a propósito: se calcula una sola vez para toda la suite.
_HASH_PRUEBA = hash_password(CLAVE_PRUEBA)


@pytest.fixture
def motor():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sesion_factory(motor):
    return sessionmaker(bind=motor, autoflush=False)


@pytest.fixture
def db(sesion_factory):
    sesion = sesion_factory()
    yield sesion
    sesion.close()


@pytest.fixture
def client(sesion_factory):
    def _get_db_pruebas():
        sesion = sesion_factory()
        try:
            yield sesion
        finally:
            sesion.close()

    app.dependency_overrides[get_db] = _get_db_pruebas
    reiniciar_limitadores()
    yield TestClient(app)
    app.dependency_overrides.clear()
    reiniciar_limitadores()


@pytest.fixture
def crear_usuario(db):
    contador = {"n": 0}

    def _crear(rol=ROL_USUARIO, email=None, comite=None, activo=True, nombre="Persona Prueba"):
        contador["n"] += 1
        usuario = User(
            email=email or f"persona{contador['n']}@test.com",
            hashed_password=_HASH_PRUEBA,
            full_name=nombre,
            phone="3000000000",
            role=rol,
            comite=comite,
            is_active=activo,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    return _crear


def cabecera_de(usuario: User) -> dict:
    """Cabecera Authorization con un JWT válido para el usuario."""
    token = create_access_token({"sub": usuario.email, "role": usuario.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin(crear_usuario):
    return crear_usuario(rol=ROL_ADMIN, nombre="Admin Prueba")


@pytest.fixture
def superadmin(crear_usuario):
    return crear_usuario(rol=ROL_SUPERADMIN, nombre="Super Prueba")


@pytest.fixture
def ciudadano(crear_usuario):
    return crear_usuario(rol=ROL_USUARIO, nombre="Ciudadano Prueba")
