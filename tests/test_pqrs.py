from app.models.pqrs import PQRS
from tests.conftest import cabecera_de

ADJUNTO = "https://res.cloudinary.com/nube-pruebas/raw/upload/v1/comunix/doc.pdf"


def _radicar(client, **extra):
    datos = {"tipo": "Queja", "asunto": "Vía dañada", "descripcion": "Hueco grande", **extra}
    respuesta = client.post("/api/pqrs", json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_pqrs_no_anonima_exige_contacto(client):
    respuesta = client.post("/api/pqrs", json={"tipo": "Queja", "asunto": "a", "descripcion": "d"})
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Indica tu nombre, o marca la PQRS como anónima"


def test_adjunto_debe_ser_de_cloudinary(client):
    respuesta = client.post(
        "/api/pqrs",
        json={
            "tipo": "Queja",
            "asunto": "a",
            "descripcion": "d",
            "es_anonima": True,
            "adjunto_url": "javascript:alert(document.cookie)",
        },
    )
    assert respuesta.status_code == 422


def test_adjunto_vacio_se_trata_como_sin_adjunto(client):
    pqrs = _radicar(client, es_anonima=True, adjunto_url="")
    assert pqrs["adjunto_url"] is None


def test_anonima_oculta_tambien_el_nombre_del_archivo(client, admin):
    _radicar(client, es_anonima=True, adjunto_url=ADJUNTO, adjunto_nombre="Queja de Pedro Pérez.pdf")
    historial = client.get("/api/pqrs/historial", headers=cabecera_de(admin)).json()
    assert historial[0]["adjunto_url"] == ADJUNTO
    assert "Pedro" not in (historial[0]["adjunto_nombre"] or "")


def test_historial_incluye_fecha_de_actualizacion(client, admin):
    _radicar(client, es_anonima=True)
    historial = client.get("/api/pqrs/historial", headers=cabecera_de(admin)).json()
    assert historial[0]["updated_at"] is not None


def test_entrantes_se_ordenan_de_la_mas_antigua_a_la_mas_nueva(client, admin):
    primera = _radicar(client, es_anonima=True, asunto="primera")
    segunda = _radicar(client, es_anonima=True, asunto="segunda")
    entrantes = client.get("/api/pqrs/entrantes", headers=cabecera_de(admin)).json()
    assert [p["id"] for p in entrantes] == [primera["id"], segunda["id"]]


def test_respuesta_vacia_se_rechaza(client, admin):
    pqrs = _radicar(client, es_anonima=True)
    respuesta = client.put(
        f"/api/pqrs/{pqrs['id']}/responder", json={"respuesta": ""}, headers=cabecera_de(admin)
    )
    assert respuesta.status_code == 422


def test_solo_el_autor_edita_su_respuesta(client, admin, crear_usuario):
    otro_admin = crear_usuario(rol="administrador")
    pqrs = _radicar(client, es_anonima=True)
    hilo = client.put(
        f"/api/pqrs/{pqrs['id']}/responder",
        json={"respuesta": "Vamos a revisar"},
        headers=cabecera_de(admin),
    ).json()["respuestas"]
    respuesta_id = hilo[0]["id"]

    ajena = client.put(
        f"/api/pqrs/respuestas/{respuesta_id}",
        json={"respuesta": "Texto cambiado"},
        headers=cabecera_de(otro_admin),
    )
    propia = client.put(
        f"/api/pqrs/respuestas/{respuesta_id}",
        json={"respuesta": "Vamos a revisar mañana"},
        headers=cabecera_de(admin),
    )
    assert ajena.status_code == 403
    assert propia.status_code == 200
    assert propia.json()["respuestas"][0]["texto"] == "Vamos a revisar mañana"


def test_estado_invalido_menciona_todos_los_estados(client, admin):
    pqrs = _radicar(client, es_anonima=True)
    respuesta = client.put(
        f"/api/pqrs/{pqrs['id']}/estado", json={"estado": "Cerrada"}, headers=cabecera_de(admin)
    )
    assert respuesta.status_code == 400
    assert "En_Espera" in respuesta.json()["detail"]


def test_pqrs_inexistente_responde_404(client, admin):
    respuesta = client.put("/api/pqrs/999/estado", json={"estado": "Finalizada"}, headers=cabecera_de(admin))
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "No existe la PQRS indicada"


def test_seguimiento_publico_no_revela_identidad(client):
    pqrs = _radicar(client, nombre_contacto="Laura", email_contacto="laura@test.com", es_anonima=False)
    respuesta = client.get(f"/api/pqrs/seguimiento/{pqrs['codigo_seguimiento']}")
    assert respuesta.status_code == 200
    assert "laura@test.com" not in respuesta.text


def test_resumen_cuenta_las_pqrs_en_espera(client, admin, db):
    pqrs = _radicar(client, es_anonima=True)
    db.query(PQRS).filter(PQRS.id == pqrs["id"]).update({"estado": "En_Espera"})
    db.commit()
    resumen = client.get("/api/reportes/resumen", headers=cabecera_de(admin)).json()
    assert resumen["pqrs_en_espera"] == 1
    assert resumen["pqrs_total"] == 1


# --- RN-012: un comité asignado no se cambia (salvo un superadministrador) ---
def _asignar(client, usuario, pqrs_id, comite):
    return client.put(f"/api/pqrs/{pqrs_id}/asignar", json={"comite": comite}, headers=cabecera_de(usuario))


def test_asignar_comite_no_cambia_el_estado(client, admin):
    pqrs = _radicar(client, es_anonima=True)
    respuesta = _asignar(client, admin, pqrs["id"], "Fiscal")
    assert respuesta.status_code == 200
    assert respuesta.json()["comite"] == "Fiscal"
    assert respuesta.json()["estado"] == "Nueva"


def test_administrador_no_reasigna_un_comite_ya_asignado(client, admin):
    pqrs = _radicar(client, es_anonima=True)
    _asignar(client, admin, pqrs["id"], "Fiscal")

    respuesta = _asignar(client, admin, pqrs["id"], "Tesorero")

    assert respuesta.status_code == 409
    assert "superadministrador" in respuesta.json()["detail"]
    historial = client.get("/api/pqrs/historial", headers=cabecera_de(admin)).json()
    assert historial[0]["comite"] == "Fiscal"


def test_asignar_el_mismo_comite_otra_vez_no_falla(client, admin):
    pqrs = _radicar(client, es_anonima=True)
    _asignar(client, admin, pqrs["id"], "Fiscal")
    assert _asignar(client, admin, pqrs["id"], "Fiscal").status_code == 200


def test_superadministrador_puede_corregir_el_comite(client, admin, superadmin):
    pqrs = _radicar(client, es_anonima=True)
    _asignar(client, admin, pqrs["id"], "Fiscal")

    respuesta = _asignar(client, superadmin, pqrs["id"], "Tesorero")

    assert respuesta.status_code == 200
    assert respuesta.json()["comite"] == "Tesorero"
