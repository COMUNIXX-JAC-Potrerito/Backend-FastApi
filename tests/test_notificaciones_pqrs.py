"""Pruebas de los avisos por correo de PQRS (destinatarios y contenido)."""

from app.models.pqrs import PQRS
from app.services.auth.roles import ROL_ADMIN, ROL_SUPERADMIN
from app.services.notificaciones import pqrs as notif_pqrs
from app.services.notificaciones.pqrs import (
    correos_del_comite,
    cuerpo_actualizacion,
    cuerpo_asignacion,
)


def _crear_pqrs(db, **extra):
    pqrs = PQRS(
        tipo="Queja",
        asunto="Ruido nocturno",
        descripcion="...",
        codigo_seguimiento=extra.pop("codigo", "cod1234567"),
        estado="Nueva",
        **extra,
    )
    db.add(pqrs)
    db.commit()
    db.refresh(pqrs)
    return pqrs


def test_cuerpo_nueva_pqrs_no_revela_identidad():
    pqrs = PQRS(
        tipo="Peticion",
        asunto="Bache en la vía",
        codigo_seguimiento="new1234567",
        es_anonima=False,
        nombre_contacto="Ana Privada",
        email_contacto="ana@secreto.com",
        telefono_contacto="3009998877",
        estado="Nueva",
    )
    _asunto, html = notif_pqrs.cuerpo_nueva_pqrs(pqrs)
    assert "Ana Privada" not in html
    assert "ana@secreto.com" not in html
    assert "3009998877" not in html
    assert "new1234567" in html


def test_preparar_nueva_pqrs_avisa_solo_a_superadmins(db, crear_usuario):
    crear_usuario(rol=ROL_SUPERADMIN, email="super@x.com")
    crear_usuario(rol=ROL_ADMIN, email="admin@x.com")  # no es superadmin: no recibe
    pqrs = _crear_pqrs(db, codigo="qrs1234567")

    envio = notif_pqrs.preparar_nueva_pqrs(db, pqrs.id)

    assert envio is not None
    correos, _asunto, _texto, _html = envio
    assert correos == ["super@x.com"]


def test_preparar_nueva_pqrs_sin_superadmins_es_none(db, crear_usuario):
    crear_usuario(rol=ROL_ADMIN, email="admin@x.com")
    pqrs = _crear_pqrs(db, codigo="none123456")

    assert notif_pqrs.preparar_nueva_pqrs(db, pqrs.id) is None


def test_cuerpo_asignacion_no_revela_identidad_si_anonima():
    pqrs = PQRS(
        tipo="Queja",
        asunto="Fuga de agua",
        codigo_seguimiento="abc1234567",
        es_anonima=True,
        nombre_contacto="Juan Secreto",
        email_contacto="juan@secreto.com",
        estado="Nueva",
    )
    _asunto, html = cuerpo_asignacion(pqrs)
    assert "Juan Secreto" not in html
    assert "juan@secreto.com" not in html
    assert "abc1234567" in html


def test_correos_del_comite_solo_activos_con_ese_comite(db, crear_usuario):
    crear_usuario(comite="Comisión de Salud", email="activo@x.com", activo=True)
    crear_usuario(comite="Comisión de Salud", email="inactivo@x.com", activo=False)
    crear_usuario(comite="Comisión de Obras e Infraestructura", email="otro@x.com", activo=True)
    assert set(correos_del_comite(db, "Comisión de Salud")) == {"activo@x.com"}


def test_cuerpo_actualizacion_incluye_codigo_y_enlace():
    pqrs = PQRS(
        tipo="Peticion", asunto="Poda", codigo_seguimiento="xyz7890123", estado="Finalizada"
    )
    _asunto, html = cuerpo_actualizacion(pqrs, "estado")
    assert "xyz7890123" in html
    assert "consultar?codigo=xyz7890123" in html
