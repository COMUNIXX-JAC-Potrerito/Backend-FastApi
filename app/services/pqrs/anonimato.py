def respuestas_de(pqrs) -> list:
    """Devuelve el hilo de respuestas de la JAC como lista de dicts.

    Usa la tabla respuestas_pqrs; si está vacía pero existe la respuesta
    legada (columna única antigua), la incluye para no perder respuestas viejas.
    """
    filas = getattr(pqrs, "respuestas", []) or []
    hilo = [
        {
            "id": r.id,
            "texto": r.texto,
            "autor_id": r.autor_id,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in filas
    ]
    legado = getattr(pqrs, "respuesta", None)
    if not hilo and legado:
        hilo.append(
            {
                "id": 0,  # respuesta legada: no editable
                "texto": legado,
                "autor_id": None,
                "created_at": getattr(pqrs, "respuesta_fecha", None)
                or getattr(pqrs, "created_at", None),
                "updated_at": None,
            }
        )
    return hilo


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
        "respuesta": pqrs.respuesta,
        "respuesta_fecha": pqrs.respuesta_fecha,
        "respuestas": respuestas_de(pqrs),
        "radicado_por_id": pqrs.radicado_por_id,
        "nombre_contacto": pqrs.nombre_contacto,
        "email_contacto": pqrs.email_contacto,
        "telefono_contacto": pqrs.telefono_contacto,
        "created_at": pqrs.created_at,
        # El adjunto es parte del contenido de la PQRS, NO revela identidad:
        # se conserva aunque sea anónima.
        "adjunto_url": pqrs.adjunto_url,
        "adjunto_tipo": pqrs.adjunto_tipo,
        "adjunto_nombre": pqrs.adjunto_nombre,
    }

    if pqrs.es_anonima:
        datos["radicado_por_id"] = None
        datos["nombre_contacto"] = None
        datos["email_contacto"] = None
        datos["telefono_contacto"] = None

    return datos
