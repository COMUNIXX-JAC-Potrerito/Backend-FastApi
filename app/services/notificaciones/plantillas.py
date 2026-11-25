"""Plantilla HTML base para los correos de COMUNIX.

Usa inline CSS (los clientes de correo ignoran las hojas de estilo externas) y
una tabla de maquetación para que se vea bien en la mayoría de los clientes.
"""

from html import escape

VERDE = "#2E7D4F"
VERDE_OSCURO = "#1B5E3A"
PIE = "COMUNIX · Junta de Acción Comunal de la Vereda Potrerito"


def render_base(
    titulo: str,
    parrafos: list[str],
    cta_texto: str | None = None,
    cta_url: str | None = None,
) -> str:
    """HTML de un correo con encabezado, título, párrafos y botón opcional.

    Escapa `titulo`, `parrafos`, `cta_texto` y `cta_url` para evitar inyección.
    """
    titulo_esc = escape(titulo)
    cuerpo = "".join(
        f'<p style="margin:0 0 16px;font-size:15px;line-height:1.5;color:#333333;">{escape(p)}</p>'
        for p in parrafos
    )
    boton = ""
    if cta_texto and cta_url:
        boton = (
            '<p style="margin:24px 0 0;">'
            f'<a href="{escape(cta_url)}" '
            f'style="background:{VERDE};color:#ffffff;text-decoration:none;'
            'padding:12px 24px;border-radius:6px;font-size:15px;font-weight:bold;'
            f'display:inline-block;">{escape(cta_texto)}</a></p>'
        )
    return f"""\
<!doctype html>
<html lang="es">
<body style="margin:0;padding:0;background:#F4F6F4;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F4F6F4;padding:24px 0;">
<tr><td align="center">
<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="background:#FFFFFF;border-radius:10px;overflow:hidden;max-width:560px;width:100%;">
<tr><td style="background:{VERDE};padding:20px 32px;">
<span style="color:#FFFFFF;font-size:22px;font-weight:bold;letter-spacing:1px;">COMUNIX</span>
</td></tr>
<tr><td style="padding:28px 32px;">
<h1 style="margin:0 0 16px;font-size:19px;color:{VERDE_OSCURO};">{titulo_esc}</h1>
{cuerpo}{boton}
</td></tr>
<tr><td style="padding:16px 32px;border-top:1px solid #E5E5E5;">
<span style="font-size:12px;color:#888888;">{PIE}</span>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""
