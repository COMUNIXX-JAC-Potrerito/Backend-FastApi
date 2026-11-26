"""Pruebas de la construcción del mensaje de correo (texto y HTML)."""

from app.services.envios.correo import construir_mensaje


def test_construir_mensaje_solo_texto():
    msg = construir_mensaje("de@x.com", "para@x.com", "Asunto", "Hola texto")
    assert msg["Subject"] == "Asunto"
    assert msg["To"] == "para@x.com"
    assert msg.get_content_type() == "text/plain"
    assert "Hola texto" in msg.get_content()


def test_construir_mensaje_con_html_adjunta_alternativa():
    msg = construir_mensaje(
        "de@x.com", "para@x.com", "Asunto", "texto plano", html="<b>hola</b>"
    )
    assert msg.get_content_type() == "multipart/alternative"
    tipos = [p.get_content_type() for p in msg.iter_parts()]
    assert "text/plain" in tipos
    assert "text/html" in tipos
