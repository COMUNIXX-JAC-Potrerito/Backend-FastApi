"""Límites contra abuso: frecuencia por IP/cuenta y tamaño de las peticiones."""

from app.core.limites import Limitador


def test_limitador_bloquea_al_superar_el_maximo_y_libera_tras_la_ventana():
    reloj = {"t": 0.0}
    limitador = Limitador(maximo=2, ventana_segundos=60, reloj=lambda: reloj["t"])
    assert limitador.permitir("ip-1")
    assert limitador.permitir("ip-1")
    assert not limitador.permitir("ip-1")
    assert limitador.permitir("ip-2")  # otra clave no se ve afectada
    reloj["t"] = 61
    assert limitador.permitir("ip-1")


def test_login_por_cuenta_se_bloquea_tras_muchos_intentos(client, crear_usuario):
    crear_usuario(email="victima@test.com")
    codigos = [
        client.post("/api/login", json={"email": "victima@test.com", "password": "Mala1234"}).status_code
        for _ in range(11)
    ]
    assert codigos[:10] == [401] * 10
    assert codigos[10] == 429


def test_cuerpo_demasiado_grande_responde_413(client):
    enorme = "x" * (13 * 1024 * 1024)
    respuesta = client.post(
        "/api/register",
        content=enorme,
        headers={"Content-Type": "application/json"},
    )
    assert respuesta.status_code == 413


def test_texto_que_supera_el_maximo_responde_422_con_mensaje_legible(client):
    datos = {
        "tipo": "Queja",
        "asunto": "a" * 1000,
        "descripcion": "d",
        "es_anonima": True,
    }
    respuesta = client.post("/api/pqrs", json=datos)
    assert respuesta.status_code == 422
    detalle = respuesta.json()["detail"]
    assert isinstance(detalle, str)
    assert "asunto" in detalle


def test_radicar_pqrs_tiene_limite_de_frecuencia(client):
    datos = {"tipo": "Queja", "asunto": "a", "descripcion": "d", "es_anonima": True}
    codigos = [client.post("/api/pqrs", json=datos).status_code for _ in range(21)]
    assert codigos[:20] == [201] * 20
    assert codigos[20] == 429
