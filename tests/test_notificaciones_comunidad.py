"""Pruebas de los avisos por correo de encuestas y publicaciones."""

from app.models.encuesta import Encuesta
from app.models.publicacion import Publicacion
from app.services.notificaciones.comunidad import (
    correos_activos,
    cuerpo_encuesta,
    cuerpo_publicacion,
)


def test_cuerpo_publicacion_incluye_titulo_y_enlace():
    pub = Publicacion(titulo="Jornada de salud", categoria="actividad", contenido="Ven")
    _asunto, html = cuerpo_publicacion(pub)
    assert "Jornada de salud" in html
    assert "comunix.vercel.app" in html


def test_cuerpo_encuesta_incluye_titulo():
    enc = Encuesta(titulo="Censo 2026", tipo="censo")
    _asunto, html = cuerpo_encuesta(enc)
    assert "Censo 2026" in html


def test_correos_activos_solo_activos_con_correo(db, crear_usuario):
    crear_usuario(email="activa@x.com", activo=True)
    crear_usuario(email="inactiva@x.com", activo=False)
    assert set(correos_activos(db)) == {"activa@x.com"}
