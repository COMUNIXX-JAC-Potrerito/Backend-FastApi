from tests.conftest import cabecera_de


def test_no_se_puede_quitar_el_rol_al_ultimo_superadmin(client, superadmin):
    respuesta = client.put(
        f"/api/usuarios/{superadmin.id}/rol",
        json={"rol": "usuario"},
        headers=cabecera_de(superadmin),
    )
    assert respuesta.status_code == 400


def test_al_dejar_de_ser_dignatario_pierde_la_comision(client, superadmin, crear_usuario):
    dignatario = crear_usuario(rol="administrador", comite="Tesorero")
    respuesta = client.put(
        f"/api/usuarios/{dignatario.id}/rol",
        json={"rol": "usuario"},
        headers=cabecera_de(superadmin),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["comite"] is None


def test_mensaje_no_puede_editarse_hasta_quedar_vacio(client, admin, crear_usuario):
    destino = crear_usuario(rol="administrador")
    mensaje = client.post(
        "/api/mensajes",
        json={"destinatario_id": destino.id, "contenido": "Hola"},
        headers=cabecera_de(admin),
    ).json()
    respuesta = client.put(
        f"/api/mensajes/{mensaje['id']}", json={"contenido": "   "}, headers=cabecera_de(admin)
    )
    assert respuesta.status_code == 400


def test_solo_el_autor_edita_un_mensaje(client, admin, crear_usuario):
    destino = crear_usuario(rol="administrador")
    mensaje = client.post(
        "/api/mensajes",
        json={"destinatario_id": destino.id, "contenido": "Hola"},
        headers=cabecera_de(admin),
    ).json()
    respuesta = client.put(
        f"/api/mensajes/{mensaje['id']}", json={"contenido": "Cambio"}, headers=cabecera_de(destino)
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == "Solo el autor puede editar"


def test_un_tercero_no_puede_borrar_mensajes_ajenos(client, admin, crear_usuario):
    destino = crear_usuario(rol="administrador")
    tercero = crear_usuario(rol="administrador")
    mensaje = client.post(
        "/api/mensajes",
        json={"destinatario_id": destino.id, "contenido": "Privado"},
        headers=cabecera_de(admin),
    ).json()
    respuesta = client.delete(f"/api/mensajes/{mensaje['id']}", headers=cabecera_de(tercero))
    assert respuesta.status_code == 404
