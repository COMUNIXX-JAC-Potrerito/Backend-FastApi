"""Pruebas de los avisos por correo de PQRS (destinatarios y contenido)."""

from app.models.pqrs import PQRS
from app.services.notificaciones.pqrs import (
    correos_del_comite,
    cuerpo_actualizacion,
    cuerpo_asignacion,
)


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
