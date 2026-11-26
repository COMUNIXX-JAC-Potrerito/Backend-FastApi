"""Pruebas del envío masivo: público dirigido y guardado opcional en bitácora."""

from app.models.comunicacion import Comunicacion
from app.schemas.envio import EnvioCreate
from app.services.auth.roles import ROL_ADMIN, ROL_ENTIDAD, ROL_SUPERADMIN, ROL_USUARIO
from app.services.envios.gestion import enviar_masivo


def _datos(publico="todos", guardar=False):
    return EnvioCreate(
        asunto="Comunicado de prueba",
        contenido="Cuerpo del comunicado.",
        publico=publico,
        guardar_en_bitacora=guardar,
    )


def test_publico_todos_excluye_entidad(db, crear_usuario):
    autor = crear_usuario(rol=ROL_ADMIN, email="a@x.com")
    crear_usuario(rol=ROL_USUARIO, email="u@x.com")
    crear_usuario(rol=ROL_ENTIDAD, email="e@x.com")  # nunca debe recibir

    r = enviar_masivo(db, _datos(publico="todos"), enviado_por_id=autor.id)

    assert r["destinatarios"] == 2  # admin + usuario, sin la entidad


def test_publico_jac_solo_dignatarios(db, crear_usuario):
    autor = crear_usuario(rol=ROL_ADMIN, email="a@x.com")
    crear_usuario(rol=ROL_SUPERADMIN, email="s@x.com")
    crear_usuario(rol=ROL_USUARIO, email="u@x.com")  # no es dignatario
    crear_usuario(rol=ROL_ENTIDAD, email="e@x.com")

    r = enviar_masivo(db, _datos(publico="jac"), enviado_por_id=autor.id)

    assert r["destinatarios"] == 2  # admin + superadmin


def test_guardar_en_bitacora_crea_comunicacion(db, crear_usuario):
    autor = crear_usuario(rol=ROL_ADMIN, email="a@x.com")

    r = enviar_masivo(db, _datos(publico="jac", guardar=True), enviado_por_id=autor.id)

    coms = db.query(Comunicacion).all()
    assert len(coms) == 1
    c = coms[0]
    assert (c.tipo, c.entidad) == ("enviada", "Miembros de la JAC")
    assert c.asunto == "Comunicado de prueba"
    assert c.descripcion == "Cuerpo del comunicado."
    assert c.registrado_por_id == autor.id
    assert r.get("guardado_en_bitacora") is True


def test_no_guarda_si_la_casilla_esta_apagada(db, crear_usuario):
    autor = crear_usuario(rol=ROL_ADMIN, email="a@x.com")

    r = enviar_masivo(db, _datos(publico="todos", guardar=False), enviado_por_id=autor.id)

    assert db.query(Comunicacion).count() == 0
    assert r.get("guardado_en_bitacora") in (False, None)


def test_etiqueta_bitacora_cuando_el_publico_es_todos(db, crear_usuario):
    autor = crear_usuario(rol=ROL_ADMIN, email="a@x.com")

    enviar_masivo(db, _datos(publico="todos", guardar=True), enviado_por_id=autor.id)

    c = db.query(Comunicacion).one()
    assert c.entidad == "Comunidad — todos los usuarios"
