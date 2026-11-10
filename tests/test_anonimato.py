from app.core.tiempo import ahora_utc
from app.services.pqrs.anonimato import NOMBRE_ADJUNTO_ANONIMO, ocultar_si_anonima


class _PQRSFake:
    """Objeto mínimo que imita una fila PQRS para probar la regla de anonimato
    sin tocar la base de datos."""

    def __init__(self, es_anonima: bool):
        self.id = 1
        self.codigo_seguimiento = "abc1234567"
        self.tipo = "Queja"
        self.asunto = "Prueba"
        self.descripcion = "Detalle"
        self.estado = "Nueva"
        self.es_anonima = es_anonima
        self.comite = None
        self.radicado_por_id = 5
        self.nombre_contacto = "Pepe Pérez"
        self.email_contacto = "pepe@test.com"
        self.telefono_contacto = "3001112222"
        self.created_at = ahora_utc()
        self.updated_at = ahora_utc()
        self.respuesta = None
        self.respuesta_fecha = None
        self.respuestas = []
        self.adjunto_url = "https://res.cloudinary.com/nube/raw/upload/doc.pdf"
        self.adjunto_tipo = "raw"
        self.adjunto_nombre = "Queja de Pepe Pérez.pdf"


def test_anonima_oculta_identidad():
    datos = ocultar_si_anonima(_PQRSFake(es_anonima=True))
    assert datos["radicado_por_id"] is None
    assert datos["nombre_contacto"] is None
    assert datos["email_contacto"] is None
    assert datos["telefono_contacto"] is None
    # El código de seguimiento NO se oculta: no revela identidad
    assert datos["codigo_seguimiento"] == "abc1234567"


def test_anonima_conserva_el_adjunto_pero_no_su_nombre_original():
    datos = ocultar_si_anonima(_PQRSFake(es_anonima=True))
    assert datos["adjunto_url"].endswith("doc.pdf")
    assert datos["adjunto_nombre"] == NOMBRE_ADJUNTO_ANONIMO


def test_no_anonima_conserva_identidad():
    datos = ocultar_si_anonima(_PQRSFake(es_anonima=False))
    assert datos["radicado_por_id"] == 5
    assert datos["nombre_contacto"] == "Pepe Pérez"
    assert datos["adjunto_nombre"] == "Queja de Pepe Pérez.pdf"
