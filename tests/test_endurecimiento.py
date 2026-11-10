"""Endurecimiento posterior a la v1.1.0: hallazgos de la segunda auditoría."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from starlette.requests import Request

from app.core.config import settings
from app.core.limites import ip_cliente
from app.services.auth.seguridad import verify_password
from tests.conftest import CLAVE_PRUEBA, cabecera_de

PQRS_ANONIMA = {"tipo": "Queja", "asunto": "a", "descripcion": "d", "es_anonima": True}


def _peticion(xff: str | None, host: str = "10.1.1.1") -> Request:
    cabeceras = [(b"x-forwarded-for", xff.encode())] if xff is not None else []
    return Request({"type": "http", "headers": cabeceras, "client": (host, 1234)})


# ---------- IP del cliente detrás del proxy ----------
def test_ip_cliente_usa_la_entrada_que_agrega_el_proxy_y_no_la_del_cliente():
    # El cliente puede inventar las primeras entradas; la última la agrega el proxy.
    assert ip_cliente(_peticion("1.2.3.4, 203.0.113.9")) == "203.0.113.9"


def test_ip_cliente_respeta_varios_proxies_confiables(monkeypatch):
    monkeypatch.setattr(settings, "proxies_confiables", 2)
    assert ip_cliente(_peticion("1.1.1.1, 203.0.113.9, 10.0.0.2")) == "203.0.113.9"


def test_ip_cliente_sin_proxies_ignora_la_cabecera(monkeypatch):
    monkeypatch.setattr(settings, "proxies_confiables", 0)
    assert ip_cliente(_peticion("1.2.3.4", host="10.9.9.9")) == "10.9.9.9"


def test_ip_cliente_con_cadena_mas_corta_que_los_proxies_usa_la_primera(monkeypatch):
    monkeypatch.setattr(settings, "proxies_confiables", 3)
    assert ip_cliente(_peticion("203.0.113.9")) == "203.0.113.9"


def test_falsear_x_forwarded_for_no_evade_el_limite(client):
    codigos = [
        client.post(
            "/api/pqrs", json=PQRS_ANONIMA, headers={"X-Forwarded-For": f"10.0.0.{i}, 203.0.113.5"}
        ).status_code
        for i in range(21)
    ]
    assert codigos[20] == 429


# ---------- Login: el bloqueo por cuenta no deja fuera al dueño ----------
def test_bloqueo_por_intentos_fallidos_no_bloquea_al_dueno_desde_otra_ip(client, crear_usuario):
    crear_usuario(email="victima@test.com")
    atacante = {"X-Forwarded-For": "198.51.100.7"}
    for _ in range(10):
        client.post(
            "/api/login", json={"email": "victima@test.com", "password": "Mala1234"}, headers=atacante
        )

    dueno = client.post(
        "/api/login",
        json={"email": "victima@test.com", "password": CLAVE_PRUEBA},
        headers={"X-Forwarded-For": "203.0.113.20"},
    )
    assert dueno.status_code == 200


# ---------- Tokens ----------
def _token(**contenido) -> str:
    return jwt.encode(contenido, settings.secret_key, algorithm="HS256")


def test_token_sin_vencimiento_se_rechaza(client, ciudadano):
    token = _token(sub=ciudadano.email)
    respuesta = client.get("/api/pqrs/mias", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 401


def test_token_vencido_se_rechaza(client, ciudadano):
    token = _token(sub=ciudadano.email, exp=datetime.now(UTC) - timedelta(minutes=1))
    respuesta = client.get("/api/pqrs/mias", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 401


def test_token_sin_firma_se_rechaza(client, ciudadano):
    token = jwt.encode(
        {"sub": ciudadano.email, "exp": datetime.now(UTC) + timedelta(hours=1)}, key=None, algorithm="none"
    )
    respuesta = client.get("/api/pqrs/mias", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 401


def test_hash_creado_con_la_version_anterior_sigue_siendo_valido():
    # Hash generado con passlib (v1.1.0): las cuentas existentes no deben perder el acceso.
    hash_antiguo = "$2b$12$9HkdLURg6K6zCl.jF7kXk.TNCpAQ/hnpEZx6awBavRgKx4.wc61P."
    assert verify_password(CLAVE_PRUEBA, hash_antiguo)
    assert not verify_password("Otra1234", hash_antiguo)


def test_hash_invalido_no_lanza_error():
    assert not verify_password(CLAVE_PRUEBA, "no-es-un-hash")


# ---------- Encuestas ----------
@pytest.fixture
def encuesta_publicada(client, admin):
    datos = {"titulo": "Encuesta", "preguntas": [{"texto": "¿Qué opina?", "tipo": "texto"}]}
    encuesta = client.post("/api/encuestas", json=datos, headers=cabecera_de(admin)).json()
    client.put(
        f"/api/encuestas/{encuesta['id']}/publicar", json={"publicada": True}, headers=cabecera_de(admin)
    )
    return encuesta


def test_sin_sesion_no_se_responde_con_el_correo_de_una_cuenta(client, encuesta_publicada, ciudadano):
    url = f"/api/encuestas/{encuesta_publicada['id']}/responder"
    items = [{"pregunta_id": encuesta_publicada["preguntas"][0]["id"], "valor": "Bien"}]

    suplantacion = client.post(url, json={"items": items, "nombre": "Falso", "email": ciudadano.email})
    assert suplantacion.status_code == 403
    assert "inicia sesión" in suplantacion.json()["detail"]

    # El dueño de la cuenta todavía puede responder.
    propia = client.post(url, json={"items": items}, headers=cabecera_de(ciudadano))
    assert propia.status_code == 201


# ---------- PQRS: seguimiento público ----------
def test_seguimiento_publico_no_revela_quien_respondio(client, admin):
    pqrs = client.post("/api/pqrs", json=PQRS_ANONIMA).json()
    client.put(f"/api/pqrs/{pqrs['id']}/responder", json={"respuesta": "Hola"}, headers=cabecera_de(admin))

    respuestas = client.get(f"/api/pqrs/seguimiento/{pqrs['codigo_seguimiento']}").json()["respuestas"]
    assert respuestas[0]["texto"] == "Hola"
    assert "autor_id" not in respuestas[0]


# ---------- Envío masivo ----------
def test_asunto_con_salto_de_linea_se_rechaza(client, admin):
    respuesta = client.post(
        "/api/envios-masivos",
        json={"asunto": "Aviso\r\nBcc: otro@test.com", "contenido": "Texto"},
        headers=cabecera_de(admin),
    )
    assert respuesta.status_code == 422


# ---------- Registro ----------
def test_registro_rechaza_nombre_solo_con_espacios(client):
    datos = {"full_name": "   ", "email": "n@test.com", "password": "Clave1234", "phone": "300"}
    assert client.post("/api/register", json=datos).status_code == 422


# ---------- Cabeceras de seguridad ----------
def test_respuestas_incluyen_cabeceras_de_seguridad(client):
    cabeceras = client.get("/health").headers
    assert cabeceras["x-content-type-options"] == "nosniff"
    assert cabeceras["x-frame-options"] == "DENY"
    assert cabeceras["referrer-policy"] == "no-referrer"


def test_respuestas_de_la_api_no_se_guardan_en_cache(client, ciudadano):
    respuesta = client.get("/api/pqrs/mias", headers=cabecera_de(ciudadano))
    assert respuesta.headers["cache-control"] == "no-store"
