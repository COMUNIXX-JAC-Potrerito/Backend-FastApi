"""Toda ruta de gestión exige sesión (401) y rol de dignatario (403)."""

import pytest

from tests.conftest import cabecera_de

RUTAS_DIGNATARIOS = [
    ("get", "/api/pqrs/entrantes"),
    ("get", "/api/pqrs/historial"),
    ("get", "/api/pqrs/asignadas"),
    ("put", "/api/pqrs/1/responder"),
    ("put", "/api/pqrs/respuestas/1"),
    ("put", "/api/pqrs/1/asignar"),
    ("put", "/api/pqrs/1/estado"),
    ("get", "/api/usuarios"),
    ("post", "/api/publicaciones"),
    ("put", "/api/publicaciones/1"),
    ("delete", "/api/publicaciones/1"),
    ("post", "/api/mensajes"),
    ("get", "/api/mensajes/recibidos"),
    ("get", "/api/mensajes/enviados"),
    ("put", "/api/mensajes/1/leido"),
    ("put", "/api/mensajes/1"),
    ("put", "/api/mensajes/1/fijar"),
    ("delete", "/api/mensajes/1"),
    ("post", "/api/comunicaciones"),
    ("get", "/api/comunicaciones"),
    ("delete", "/api/comunicaciones/1"),
    ("post", "/api/envios-masivos"),
    ("get", "/api/reportes/resumen"),
    ("get", "/api/reportes/carga-comites"),
    ("get", "/api/encuestas/gestion"),
    ("post", "/api/encuestas"),
    ("put", "/api/encuestas/1/publicar"),
    ("delete", "/api/encuestas/1"),
    ("get", "/api/encuestas/1/resultados"),
    ("get", "/api/encuestas/1/participantes"),
]

RUTAS_SUPERADMIN = [
    ("put", "/api/usuarios/1/rol"),
    ("put", "/api/usuarios/1/comite"),
]


@pytest.mark.parametrize(("metodo", "ruta"), RUTAS_DIGNATARIOS + RUTAS_SUPERADMIN)
def test_ruta_protegida_rechaza_sin_sesion(client, metodo, ruta):
    respuesta = client.request(metodo, ruta, json={})
    assert respuesta.status_code == 401


@pytest.mark.parametrize(("metodo", "ruta"), RUTAS_DIGNATARIOS + RUTAS_SUPERADMIN)
def test_ruta_protegida_rechaza_a_ciudadano(client, ciudadano, metodo, ruta):
    respuesta = client.request(metodo, ruta, json={}, headers=cabecera_de(ciudadano))
    assert respuesta.status_code == 403


@pytest.mark.parametrize(("metodo", "ruta"), RUTAS_SUPERADMIN)
def test_ruta_superadmin_rechaza_a_admin(client, admin, metodo, ruta):
    respuesta = client.request(metodo, ruta, json={}, headers=cabecera_de(admin))
    assert respuesta.status_code == 403


def test_usuario_inactivo_no_puede_usar_su_token(client, crear_usuario):
    inactivo = crear_usuario(rol="administrador", activo=False)
    respuesta = client.get("/api/pqrs/entrantes", headers=cabecera_de(inactivo))
    assert respuesta.status_code == 401
