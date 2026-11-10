"""Importa todos los modelos para que queden registrados en Base.metadata."""

from app.models import comunicacion, encuesta, envio_masivo, mensaje, pqrs, publicacion, user

__all__ = ["comunicacion", "encuesta", "envio_masivo", "mensaje", "pqrs", "publicacion", "user"]
