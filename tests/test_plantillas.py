"""Pruebas de la plantilla HTML base de los correos."""

from app.services.notificaciones.plantillas import render_base


def test_render_base_incluye_contenido_y_boton():
    html = render_base("Hola", ["Línea uno"], cta_texto="Abrir", cta_url="https://x.test")
    assert "Hola" in html
    assert "Línea uno" in html
    assert "https://x.test" in html
    assert "Abrir" in html


def test_render_base_escapa_html():
    html = render_base("<script>x</script>", ["a & b"])
    assert "<script>" not in html
    assert "&amp; b" in html


def test_render_base_sin_boton_no_incluye_cta():
    html = render_base("Solo texto", ["Cuerpo"])
    assert "Cuerpo" in html
    # Sin cta_url no debe haber un enlace de acción.
    assert "href" not in html
