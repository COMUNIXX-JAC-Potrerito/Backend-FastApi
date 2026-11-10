"""Subida de archivos a Cloudinary.

La firma (api_secret) vive solo en el backend: el navegador nunca la ve. El
frontend manda el archivo a POST /api/uploads y aquí se sube a Cloudinary; se
devuelve la URL pública (CDN) que luego se guarda en la base de datos.
"""

import logging
from functools import lru_cache
from typing import BinaryIO
from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader

from app.core.config import settings
from app.core.errores import DatosInvalidos, ErrorServicioExterno, ServicioNoDisponible
from app.services.uploads.firmas import contenido_coincide, tipo_declarado_permitido

logger = logging.getLogger(__name__)

MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LARGO_MAXIMO_NOMBRE = 255
MENSAJE_TIPO_NO_PERMITIDO = "Tipo de archivo no permitido (solo imágenes, video, audio o documentos)."


@lru_cache(maxsize=1)
def _configurar_cloudinary() -> None:
    """Configura el SDK una sola vez a partir de CLOUDINARY_URL.

    Si falta la variable se lanza el error (y no se guarda en caché), así que un
    reinicio con la variable ya definida funciona sin cambios de código.
    """
    if not settings.cloudinary_url:
        raise ServicioNoDisponible("La subida de archivos no está configurada (falta CLOUDINARY_URL).")
    url = urlparse(settings.cloudinary_url)
    cloudinary.config(
        cloud_name=url.hostname,
        api_key=url.username,
        api_secret=url.password,
        secure=True,
    )


def leer_con_limite(archivo: BinaryIO, maximo_bytes: int = MAX_BYTES) -> bytes:
    """Lee como máximo `maximo_bytes` + 1, sin cargar en memoria un archivo enorme."""
    contenido = archivo.read(maximo_bytes + 1)
    if len(contenido) > maximo_bytes:
        raise DatosInvalidos("El archivo supera el límite de 10 MB.")
    if not contenido:
        raise DatosInvalidos("El archivo está vacío.")
    return contenido


def validar_tipo_declarado(content_type: str | None) -> None:
    if not tipo_declarado_permitido(content_type):
        raise DatosInvalidos(MENSAJE_TIPO_NO_PERMITIDO)


def validar_contenido(content_type: str | None, contenido: bytes) -> None:
    if not contenido_coincide(content_type, contenido):
        raise DatosInvalidos("El contenido del archivo no corresponde a su tipo.")


def nombre_seguro(nombre: str | None) -> str:
    """Nombre original para mostrar, sin rutas y con largo acotado."""
    base = (nombre or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    return base[:LARGO_MAXIMO_NOMBRE] or "archivo"


def subir_archivo(contenido: bytes, nombre: str) -> dict:
    """Sube el archivo y devuelve {url, tipo, nombre}.

    `tipo` es el resource_type de Cloudinary: 'image', 'video' (incluye audio) o
    'raw' (documentos).
    """
    _configurar_cloudinary()
    try:
        resultado = cloudinary.uploader.upload(
            contenido,
            resource_type="auto",
            folder="comunix",
            use_filename=True,
            unique_filename=True,
        )
    except Exception as error:
        # El SDK puede lanzar varios tipos de error; ninguno debe llegar al cliente.
        logger.exception("Fallo al subir un archivo a Cloudinary")
        raise ErrorServicioExterno("No se pudo subir el archivo. Intenta de nuevo.") from error

    return {
        "url": resultado["secure_url"],
        "tipo": resultado.get("resource_type", "raw"),
        "nombre": nombre,
    }
