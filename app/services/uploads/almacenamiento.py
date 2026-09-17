"""Subida de archivos multimedia a Cloudinary.

La firma (api_secret) vive SOLO en el backend: el navegador nunca la ve.
El frontend manda el archivo a POST /api/uploads y aquí lo subimos a Cloudinary,
devolviendo la URL pública (CDN) que luego se guarda en la base de datos.
"""

import os

import cloudinary
import cloudinary.uploader

from app.core.config import settings

_configurado = False


def _asegurar_config() -> None:
    """Configura Cloudinary una sola vez a partir de settings.cloudinary_url.

    El SDK lee la variable de entorno CLOUDINARY_URL; como pydantic-settings
    carga el .env en el objeto settings (no en os.environ), la inyectamos aquí.
    """
    global _configurado
    if _configurado:
        return

    if not settings.cloudinary_url:
        raise ValueError(
            "La subida de archivos no está configurada (falta CLOUDINARY_URL)."
        )

    os.environ.setdefault("CLOUDINARY_URL", settings.cloudinary_url)
    cloudinary.config(secure=True)
    _configurado = True


def subir_archivo(contenido: bytes, nombre: str) -> dict:
    """Sube el archivo a Cloudinary y devuelve {url, tipo, nombre}.

    - `tipo` es el resource_type de Cloudinary: 'image', 'video' (incluye audio)
      o 'raw' (documentos: pdf, docx, etc.).
    """
    _asegurar_config()

    resultado = cloudinary.uploader.upload(
        contenido,
        resource_type="auto",   # detecta imagen / video / audio / documento
        folder="comunix",       # todo lo del proyecto queda en una carpeta
        use_filename=True,
        unique_filename=True,
    )

    return {
        "url": resultado["secure_url"],
        "tipo": resultado.get("resource_type", "raw"),
        "nombre": nombre,
    }
