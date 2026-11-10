"""Migraciones de la base de datos (Alembic).

Corren contra SQLite en un archivo temporal. Si existe TEST_POSTGRES_URL (en CI
hay un PostgreSQL de servicio) corren contra PostgreSQL, el motor de producción.
"""

import os

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from app.db.migrar import REVISION_BASE, config_alembic, migrar
from app.db.session import Base
from app.services.encuestas import respuestas
from tests.conftest import cabecera_de


@pytest.fixture
def url_bd(tmp_path):
    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        return f"sqlite:///{(tmp_path / 'migraciones.db').as_posix()}"
    motor_bd = create_engine(url)
    with motor_bd.begin() as conexion:  # base vacía para cada test
        conexion.execute(text("DROP SCHEMA public CASCADE"))
        conexion.execute(text("CREATE SCHEMA public"))
    motor_bd.dispose()
    return url


@pytest.fixture
def motor_bd(url_bd):
    engine = create_engine(url_bd)
    yield engine
    engine.dispose()


def _version(motor_bd) -> str | None:
    with motor_bd.connect() as conexion:
        return MigrationContext.configure(conexion).get_current_revision()


def _head(url: str) -> str:
    return ScriptDirectory.from_config(config_alembic(url)).get_current_head()


def _como_neon_hoy(url_bd, motor_bd) -> None:
    """Base creada con create_all en la v1.2.0: el esquema base, sin registro de Alembic."""
    command.upgrade(config_alembic(url_bd), REVISION_BASE)
    with motor_bd.begin() as conexion:
        conexion.execute(text("DROP TABLE alembic_version"))


def _insertar(conexion, tabla: str, **valores) -> None:
    columnas = ", ".join(valores)
    marcadores = ", ".join(f":{c}" for c in valores)
    # Tabla y columnas las fija cada test; los valores van como parámetros.
    conexion.execute(text(f"INSERT INTO {tabla} ({columnas}) VALUES ({marcadores})"), valores)  # noqa: S608


def _usuario_y_encuesta(conexion) -> None:
    _insertar(conexion, "users", id=1, email="a@test.com", hashed_password="x", full_name="A", role="usuario")
    _insertar(conexion, "encuestas", id=1, titulo="Censo", tipo="censo", publicada=True)
    _insertar(conexion, "preguntas", id=1, encuesta_id=1, texto="¿Agua?", tipo="texto", orden=0)


def test_base_vacia_queda_igual_a_los_modelos(url_bd, motor_bd):
    migrar(url_bd)

    with motor_bd.connect() as conexion:
        diferencias = compare_metadata(MigrationContext.configure(conexion), Base.metadata)
    assert diferencias == []
    assert _version(motor_bd) == _head(url_bd)


def test_base_existente_sin_registro_se_marca_sin_perder_datos(url_bd, motor_bd):
    _como_neon_hoy(url_bd, motor_bd)
    with motor_bd.begin() as conexion:
        _usuario_y_encuesta(conexion)

    migrar(url_bd)

    assert _version(motor_bd) == _head(url_bd)
    with motor_bd.connect() as conexion:
        assert conexion.execute(text("SELECT email FROM users")).scalar() == "a@test.com"


def test_respuestas_duplicadas_conservan_la_primera(url_bd, motor_bd):
    _como_neon_hoy(url_bd, motor_bd)
    with motor_bd.begin() as conexion:
        _usuario_y_encuesta(conexion)
        for respuesta_id in (10, 11):
            _insertar(conexion, "respuestas_encuesta", id=respuesta_id, encuesta_id=1, usuario_id=1)
            _insertar(conexion, "respuesta_items", respuesta_id=respuesta_id, pregunta_id=1, valor="v")

    migrar(url_bd)

    with motor_bd.connect() as conexion:
        assert conexion.execute(text("SELECT id FROM respuestas_encuesta")).scalars().all() == [10]
        items = conexion.execute(text("SELECT respuesta_id FROM respuesta_items")).scalars().all()
        assert items == [10]


def test_la_base_impide_que_una_cuenta_responda_dos_veces(url_bd, motor_bd):
    migrar(url_bd)
    with motor_bd.begin() as conexion:
        _usuario_y_encuesta(conexion)
        _insertar(conexion, "respuestas_encuesta", id=1, encuesta_id=1, usuario_id=1)

    with pytest.raises(IntegrityError), motor_bd.begin() as conexion:
        _insertar(conexion, "respuestas_encuesta", id=2, encuesta_id=1, usuario_id=1)


def test_respuestas_anonimas_no_chocan_con_el_indice(url_bd, motor_bd):
    # usuario_id NULL (sin cuenta) puede repetirse: el índice solo aplica a cuentas.
    migrar(url_bd)
    with motor_bd.begin() as conexion:
        _usuario_y_encuesta(conexion)
        _insertar(conexion, "respuestas_encuesta", id=1, encuesta_id=1, nombre="Ana")
        _insertar(conexion, "respuestas_encuesta", id=2, encuesta_id=1, nombre="Luis")


def test_migrar_dos_veces_no_hace_nada_la_segunda(url_bd, motor_bd):
    migrar(url_bd)
    migrar(url_bd)
    assert _version(motor_bd) == _head(url_bd)


def test_se_puede_volver_a_la_base(url_bd, motor_bd):
    migrar(url_bd)
    command.downgrade(config_alembic(url_bd), REVISION_BASE)

    indices = {i["name"] for i in inspect(motor_bd).get_indexes("respuestas_encuesta")}
    assert "uq_respuestas_encuesta_encuesta_usuario" not in indices


def test_respuesta_simultanea_de_la_misma_cuenta_responde_409(client, ciudadano, admin, monkeypatch):
    datos = {"titulo": "E", "preguntas": [{"texto": "¿Qué opina?", "tipo": "texto"}]}
    encuesta = client.post("/api/encuestas", json=datos, headers=cabecera_de(admin)).json()
    client.put(
        f"/api/encuestas/{encuesta['id']}/publicar", json={"publicada": True}, headers=cabecera_de(admin)
    )
    url = f"/api/encuestas/{encuesta['id']}/responder"
    items = [{"pregunta_id": encuesta["preguntas"][0]["id"], "valor": "Bien"}]
    assert client.post(url, json={"items": items}, headers=cabecera_de(ciudadano)).status_code == 201

    # Dos clics a la vez: ambos pasan la verificación previa; la base frena el segundo.
    monkeypatch.setattr(respuestas, "_ya_respondio", lambda *_: False)
    segunda = client.post(url, json={"items": items}, headers=cabecera_de(ciudadano))

    assert segunda.status_code == 409
    assert segunda.json()["detail"] == "Ya respondiste esta encuesta"
