"""Cabeceras de seguridad que se agregan a todas las respuestas.

La API solo devuelve JSON, así que se le pide al navegador lo más estricto:
no adivinar el tipo de contenido, no mostrarla dentro de un iframe, no enviar
la URL como "Referer" y, en las rutas /api, no guardar respuestas en caché
(pueden llevar datos personales).
"""

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

CABECERAS_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "frame-ancestors 'none'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}
PREFIJO_API = "/api/"


class CabecerasSeguridad:
    """Middleware ASGI que agrega `CABECERAS_SEGURIDAD` sin pisar las ya definidas."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        es_api = scope.get("path", "").startswith(PREFIJO_API)

        async def _send(mensaje: Message) -> None:
            if mensaje["type"] == "http.response.start":
                cabeceras = MutableHeaders(scope=mensaje)
                for nombre, valor in CABECERAS_SEGURIDAD.items():
                    cabeceras.setdefault(nombre, valor)
                if es_api:
                    cabeceras.setdefault("Cache-Control", "no-store")
            await send(mensaje)

        await self.app(scope, receive, _send)
