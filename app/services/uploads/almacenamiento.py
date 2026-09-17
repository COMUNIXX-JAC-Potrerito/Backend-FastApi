"""Subida de archivos multimedia a Cloudinary.

La firma (api_secret) vive SOLO en el backend: el navegador nunca la ve.
El frontend manda el archivo a POST /api/uploads y aquí lo subimos a Cloudinary,
devolviendo la URL pública (CDN) que luego se guarda en la base de datos.
"""

from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader

from app.core.config import settings

_configurado = False


def _asegurar_config() -> None:
    """Configura Cloudinary una sola vez a partir de settings.cloudinary_url.

    Se parsea la cadena `cloudinary://<api_key>:<api_secret>@<cloud_name>` y se
    pasan los valores explícitamente (no dependemos de que el SDK lea la variable
    de entorno, que solo la toma al importar el módulo).
    """
    global _configurado
    if _configurado:
        return

    if not settings.cloudinary_url:
        raise ValueError(
            "La subida de archivos no está configurada (falta CLOUDINARY_URL)."
        )

    u = urlparse(settings.cloudinary_url)
    cloudinary.config(
        cloud_name=u.hostname,
        api_key=u.username,
        api_secret=u.password,
        secure=True,
    )
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
