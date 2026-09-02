def ocultar_si_anonima(pqrs) -> dict:
    """Convierte una PQRS en un dict para responder.
    Si es anónima, oculta (pone en None) los datos que revelan la identidad.
    El codigo_seguimiento NO se oculta: no revela quién es y sirve para consultar el estado.
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
        "radicado_por_id": pqrs.radicado_por_id,
        "nombre_contacto": pqrs.nombre_contacto,
        "email_contacto": pqrs.email_contacto,
        "telefono_contacto": pqrs.telefono_contacto,
        "created_at": pqrs.created_at,
    }

    if pqrs.es_anonima:
        datos["radicado_por_id"] = None
        datos["nombre_contacto"] = None
        datos["email_contacto"] = None
        datos["telefono_contacto"] = None

    return datos
