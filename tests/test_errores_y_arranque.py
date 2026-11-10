from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.core.errores import NoEncontrado, registrar_manejadores
from app.main import app


def _app_de_prueba() -> FastAPI:
    aplicacion = FastAPI()
    registrar_manejadores(aplicacion)

    @aplicacion.get("/conflicto")
    def _conflicto():
        raise IntegrityError("INSERT ...", {}, Exception("duplicate key"))

    @aplicacion.get("/no-existe")
    def _no_existe():
        raise NoEncontrado("Recurso no encontrado")

    return aplicacion


def test_conflicto_de_integridad_responde_409_sin_detalles_de_la_base():
    respuesta = TestClient(_app_de_prueba()).get("/conflicto")
    assert respuesta.status_code == 409
    assert "duplicate" not in respuesta.text


def test_error_de_dominio_conserva_el_formato_detail():
    respuesta = TestClient(_app_de_prueba()).get("/no-existe")
    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Recurso no encontrado"}


def test_cuerpo_enviado_por_fragmentos_tambien_se_limita(client):
    def _fragmentos():
        bloque = b"x" * (1024 * 1024)
        for _ in range(13):
            yield bloque

    respuesta = client.post(
        "/api/register", content=_fragmentos(), headers={"Content-Type": "application/json"}
    )
    assert respuesta.status_code == 413


def test_la_app_arranca_y_crea_las_tablas():
    with TestClient(app) as cliente:
        assert cliente.get("/health").status_code == 200
