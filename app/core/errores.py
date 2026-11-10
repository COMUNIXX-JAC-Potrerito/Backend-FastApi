"""Errores de dominio y su traducción a respuestas HTTP.

Los servicios lanzan estas excepciones (sin conocer FastAPI) y un único manejador
global las convierte en `{"detail": "<mensaje>"}` con su código HTTP. Así los
routers no necesitan bloques try/except repetidos.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class ErrorDominio(Exception):
    """Base de los errores de negocio; cada subclase define su código HTTP."""

    codigo_http = status.HTTP_400_BAD_REQUEST

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class DatosInvalidos(ErrorDominio):
    codigo_http = status.HTTP_400_BAD_REQUEST


class NoAutenticado(ErrorDominio):
    codigo_http = status.HTTP_401_UNAUTHORIZED


class SinPermiso(ErrorDominio):
    codigo_http = status.HTTP_403_FORBIDDEN


class NoEncontrado(ErrorDominio):
    codigo_http = status.HTTP_404_NOT_FOUND


class Conflicto(ErrorDominio):
    codigo_http = status.HTTP_409_CONFLICT


class ErrorServicioExterno(ErrorDominio):
    codigo_http = status.HTTP_502_BAD_GATEWAY


class ServicioNoDisponible(ErrorDominio):
    codigo_http = status.HTTP_503_SERVICE_UNAVAILABLE


_MENSAJES_VALIDACION = {
    "missing": "es obligatorio",
    "string_too_long": "supera el máximo de {max_length} caracteres",
    "string_too_short": "debe tener al menos {min_length} caracteres",
    "too_long": "admite como máximo {max_length} elementos",
    "too_short": "debe tener al menos {min_length} elementos",
    "string_type": "debe ser texto",
    "int_parsing": "debe ser un número entero",
    "bool_parsing": "debe ser verdadero o falso",
    "datetime_parsing": "debe ser una fecha válida",
    "datetime_from_date_parsing": "debe ser una fecha válida",
    "json_invalid": "el cuerpo no es un JSON válido",
}


def mensaje_de_validacion(errores: list[dict]) -> str:
    """Resume el primer error de validación en una frase legible en español."""
    if not errores:
        return "Datos inválidos"
    error = errores[0]
    campo = ".".join(str(parte) for parte in error.get("loc", ())[1:]) or "cuerpo"
    plantilla = _MENSAJES_VALIDACION.get(error.get("type", ""))
    if plantilla:
        detalle = plantilla.format(**error.get("ctx", {}))
    else:
        detalle = str(error.get("msg", "valor inválido")).removeprefix("Value error, ")
    return f"Dato inválido en '{campo}': {detalle}"


def registrar_manejadores(app: FastAPI) -> None:
    """Conecta los manejadores globales de errores a la aplicación."""

    @app.exception_handler(ErrorDominio)
    async def _error_dominio(_: Request, error: ErrorDominio) -> JSONResponse:
        cabeceras = {"WWW-Authenticate": "Bearer"} if isinstance(error, NoAutenticado) else None
        return JSONResponse(
            status_code=error.codigo_http, content={"detail": error.mensaje}, headers=cabeceras
        )

    @app.exception_handler(RequestValidationError)
    async def _error_validacion(_: Request, error: RequestValidationError) -> JSONResponse:
        errores = error.errors()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": mensaje_de_validacion(errores),
                "errores": jsonable_encoder(errores),
            },
        )

    @app.exception_handler(IntegrityError)
    async def _error_integridad(request: Request, error: IntegrityError) -> JSONResponse:
        logger.warning("Conflicto de integridad en %s %s: %s", request.method, request.url.path, error.orig)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "La operación entra en conflicto con datos existentes"},
        )
