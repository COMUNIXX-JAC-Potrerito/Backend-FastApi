"""Columnas reutilizables entre modelos (no crean tablas por sí mismas)."""

from sqlalchemy import Column, String


class AdjuntoMixin:
    """Adjunto opcional (multimedia/archivo) subido a Cloudinary."""

    adjunto_url = Column(String, nullable=True)
    adjunto_tipo = Column(String, nullable=True)  # image | video | raw
    adjunto_nombre = Column(String, nullable=True)
