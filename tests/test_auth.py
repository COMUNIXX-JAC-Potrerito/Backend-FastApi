import pytest
from pydantic import ValidationError

from app.core.config import Settings
from tests.conftest import CLAVE_PRUEBA

DATOS_REGISTRO = {
    "full_name": "Ana Gómez",
    "email": "Ana.Gomez@Test.com ",
    "password": "Segura123",
    "phone": "3001234567",
}


def test_registro_guarda_el_correo_normalizado(client):
    respuesta = client.post("/api/register", json=DATOS_REGISTRO)
    assert respuesta.status_code == 201
    assert respuesta.json()["email"] == "ana.gomez@test.com"
    assert "hashed_password" not in respuesta.json()


def test_registro_no_permite_duplicar_correo_con_otras_mayusculas(client):
    client.post("/api/register", json=DATOS_REGISTRO)
    otro = {**DATOS_REGISTRO, "email": "ANA.GOMEZ@test.com"}
    respuesta = client.post("/api/register", json=otro)
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Ya existe un usuario registrado con ese correo"


def test_registro_no_permite_asignarse_un_rol(client):
    datos = {**DATOS_REGISTRO, "role": "superadministrador"}
    respuesta = client.post("/api/register", json=datos)
    assert respuesta.json()["role"] == "usuario"


def test_registro_rechaza_contrasena_de_mas_de_72_bytes(client):
    datos = {**DATOS_REGISTRO, "password": "A1" + "ñ" * 40}  # 82 bytes en UTF-8
    respuesta = client.post("/api/register", json=datos)
    assert respuesta.status_code in (400, 422)


def test_login_no_distingue_mayusculas_en_el_correo(client, crear_usuario):
    crear_usuario(email="pepe@test.com")
    respuesta = client.post("/api/login", json={"email": " PEPE@Test.com", "password": CLAVE_PRUEBA})
    assert respuesta.status_code == 200
    assert respuesta.json()["token_type"] == "bearer"


def test_login_rechaza_usuario_inactivo(client, crear_usuario):
    crear_usuario(email="bloqueado@test.com", activo=False)
    respuesta = client.post("/api/login", json={"email": "bloqueado@test.com", "password": CLAVE_PRUEBA})
    assert respuesta.status_code == 401


def test_login_con_correo_inexistente_responde_igual_que_clave_erronea(client, crear_usuario):
    crear_usuario(email="real@test.com")
    inexistente = client.post("/api/login", json={"email": "nadie@test.com", "password": "x"})
    erronea = client.post("/api/login", json={"email": "real@test.com", "password": "x"})
    assert inexistente.status_code == erronea.status_code == 401
    assert inexistente.json() == erronea.json()


@pytest.mark.parametrize("clave", ["corta", "cambia-esto-por-una-clave-secreta-larga"])
def test_configuracion_rechaza_secret_key_insegura(clave):
    with pytest.raises(ValidationError):
        Settings(database_url="sqlite://", secret_key=clave, _env_file=None)
