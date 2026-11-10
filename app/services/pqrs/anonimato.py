"""Serialización de PQRS aplicando la regla de anonimato."""

# Nombre genérico para el archivo de una PQRS anónima: el nombre original
# (p. ej. "Queja de Pedro Pérez.pdf") puede revelar quién la radicó.
NOMBRE_ADJUNTO_ANONIMO = "Adjunto"

_CAMPOS_IDENTIDAD = ("radicado_por_id", "nombre_contacto", "email_contacto", "telefono_contacto")


def respuestas_de(pqrs) -> list[dict]:
    """Hilo de respuestas de la JAC.

    Si la PQRS solo tiene la respuesta única de la versión anterior (columna
    `respuesta`), se incluye como primera respuesta para no perderla.
    """
    hilo = [
        {
            "id": r.id,
            "texto": r.texto,
            "autor_id": r.autor_id,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in pqrs.respuestas
    ]
    if not hilo and pqrs.respuesta:
        hilo.append(
            {
                "id": 0,  # respuesta de la versión anterior: no editable
                "texto": pqrs.respuesta,
                "autor_id": None,
                "created_at": pqrs.respuesta_fecha or pqrs.created_at,
                "updated_at": None,
            }
        )
    return hilo


def nombre_adjunto_visible(pqrs) -> str | None:
    if pqrs.es_anonima and pqrs.adjunto_nombre:
        return NOMBRE_ADJUNTO_ANONIMO
    return pqrs.adjunto_nombre


def ocultar_si_anonima(pqrs) -> dict:
    """Convierte una PQRS en dict; si es anónima, oculta lo que revela la identidad.

    El código de seguimiento y el adjunto se conservan: no identifican a nadie.
    """
    datos = {
        "id": pqrs.id,
        "codigo_seguimiento": pqrs.codigo_seguimiento,
        "tipo": pqrs.tipo,
        "asunto": pqrs.asunto,
        "descripcion": pqrs.descripcion,
        "estado": pqrs.estado,
        "es_anonima": pqrs.es_anonima,
        "comite": pqrs.comite,
        "respuesta": pqrs.respuesta,
        "respuesta_fecha": pqrs.respuesta_fecha,
        "respuestas": respuestas_de(pqrs),
        "radicado_por_id": pqrs.radicado_por_id,
        "nombre_contacto": pqrs.nombre_contacto,
        "email_contacto": pqrs.email_contacto,
        "telefono_contacto": pqrs.telefono_contacto,
        "created_at": pqrs.created_at,
        "updated_at": pqrs.updated_at,
        "adjunto_url": pqrs.adjunto_url,
        "adjunto_tipo": pqrs.adjunto_tipo,
        "adjunto_nombre": nombre_adjunto_visible(pqrs),
    }
    if pqrs.es_anonima:
        datos.update(dict.fromkeys(_CAMPOS_IDENTIDAD))
    return datos
