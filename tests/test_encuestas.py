import pytest

from tests.conftest import cabecera_de


@pytest.fixture
def encuesta(client, admin):
    datos = {
        "titulo": "Censo 2026",
        "tipo": "censo",
        "preguntas": [
            {"texto": "¿Tiene agua potable?", "tipo": "opciones", "opciones": ["Sí", "No"]},
            {"texto": "Comentarios", "tipo": "texto"},
        ],
    }
    creada = client.post("/api/encuestas", json=datos, headers=cabecera_de(admin))
    assert creada.status_code == 201, creada.text
    encuesta = creada.json()
    client.put(
        f"/api/encuestas/{encuesta['id']}/publicar",
        json={"publicada": True},
        headers=cabecera_de(admin),
    )
    return encuesta


def _items(encuesta, opcion="Sí", comentario="Bien"):
    opciones, texto = encuesta["preguntas"]
    return [
        {"pregunta_id": opciones["id"], "valor": opcion},
        {"pregunta_id": texto["id"], "valor": comentario},
    ]


def test_detalle_devuelve_las_opciones_como_lista(client, encuesta):
    detalle = client.get(f"/api/encuestas/{encuesta['id']}").json()
    assert detalle["preguntas"][0]["opciones"] == ["Sí", "No"]
    assert detalle["preguntas"][1]["opciones"] is None


def test_encuesta_con_pregunta_de_opciones_incompleta_no_se_crea(client, admin):
    datos = {"titulo": "Mala", "preguntas": [{"texto": "x", "tipo": "opciones", "opciones": ["Sí"]}]}
    respuesta = client.post("/api/encuestas", json=datos, headers=cabecera_de(admin))
    assert respuesta.status_code == 400
    assert client.get("/api/encuestas/gestion", headers=cabecera_de(admin)).json() == []


def test_usuario_registrado_no_responde_dos_veces_aunque_omita_el_token(client, encuesta, ciudadano):
    url = f"/api/encuestas/{encuesta['id']}/responder"
    con_sesion = client.post(url, json={"items": _items(encuesta)}, headers=cabecera_de(ciudadano))
    sin_token = client.post(
        url,
        json={"items": _items(encuesta), "nombre": "Otro", "email": ciudadano.email.upper()},
    )
    assert con_sesion.status_code == 201
    assert sin_token.status_code == 409


def test_con_sesion_se_usan_los_datos_de_la_cuenta(client, encuesta, ciudadano, admin):
    client.post(
        f"/api/encuestas/{encuesta['id']}/responder",
        json={"items": _items(encuesta), "nombre": "Suplantado", "email": "falso@test.com"},
        headers=cabecera_de(ciudadano),
    )
    participantes = client.get(
        f"/api/encuestas/{encuesta['id']}/participantes", headers=cabecera_de(admin)
    ).json()
    assert participantes[0]["nombre"] == ciudadano.full_name
    assert participantes[0]["email"] == ciudadano.email


def test_opcion_inexistente_se_rechaza(client, encuesta):
    respuesta = client.post(
        f"/api/encuestas/{encuesta['id']}/responder",
        json={"items": _items(encuesta, opcion="Tal vez"), "nombre": "Ana", "email": "a@t.co"},
    )
    assert respuesta.status_code == 400


def test_pregunta_de_otra_encuesta_se_rechaza(client, encuesta):
    items = [{"pregunta_id": 9999, "valor": "Sí"}]
    respuesta = client.post(
        f"/api/encuestas/{encuesta['id']}/responder",
        json={"items": items, "nombre": "Ana", "email": "a@t.co"},
    )
    assert respuesta.status_code == 400


def test_pregunta_repetida_en_una_respuesta_se_rechaza(client, encuesta):
    items = _items(encuesta) + _items(encuesta)
    respuesta = client.post(
        f"/api/encuestas/{encuesta['id']}/responder",
        json={"items": items, "nombre": "Ana", "email": "a@t.co"},
    )
    assert respuesta.status_code == 400


def test_resultados_cuentan_opciones_y_agrupan_textos(client, encuesta, admin):
    url = f"/api/encuestas/{encuesta['id']}/responder"
    client.post(url, json={"items": _items(encuesta, "Sí", "Bien"), "nombre": "A", "email": "a@t.co"})
    client.post(url, json={"items": _items(encuesta, "No", ""), "nombre": "B", "telefono": "300"})
    resultados = client.get(f"/api/encuestas/{encuesta['id']}/resultados", headers=cabecera_de(admin)).json()
    opciones, texto = resultados["preguntas"]
    assert resultados["total_respuestas"] == 2
    assert opciones["conteo"] == {"Sí": 1, "No": 1}
    assert opciones["respuestas_texto"] is None
    assert texto["respuestas_texto"] == ["Bien"]
    assert texto["conteo"] is None


def test_eliminar_encuesta_borra_sus_respuestas(client, encuesta, admin):
    client.post(
        f"/api/encuestas/{encuesta['id']}/responder",
        json={"items": _items(encuesta), "nombre": "A", "email": "a@t.co"},
    )
    borrada = client.delete(f"/api/encuestas/{encuesta['id']}", headers=cabecera_de(admin))
    assert borrada.status_code == 204
    assert client.get(f"/api/encuestas/{encuesta['id']}").status_code == 404
