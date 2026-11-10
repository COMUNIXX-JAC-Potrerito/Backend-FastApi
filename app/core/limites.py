"""Protección contra abuso: límite de frecuencia y de tamaño de las peticiones.

El limitador guarda los contadores en memoria del proceso. Es suficiente para
una sola instancia (el plan actual de Render); con varias instancias habría que
llevar los contadores a un almacén compartido como Redis.
"""

import threading
import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, Request, status
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings

_registrados: list[Limitador] = []


class Limitador:
    """Ventana deslizante: permite `maximo` eventos por clave cada `ventana_segundos`."""

    def __init__(self, maximo: int, ventana_segundos: float, reloj: Callable[[], float] = time.monotonic):
        self.maximo = maximo
        self.ventana = ventana_segundos
        self._reloj = reloj
        self._eventos: dict[str, deque[float]] = {}
        self._candado = threading.Lock()

    def permitir(self, clave: str) -> bool:
        """Registra un evento para la clave; False si ya superó el máximo."""
        ahora = self._reloj()
        with self._candado:
            eventos = self._eventos.setdefault(clave, deque())
            while eventos and ahora - eventos[0] >= self.ventana:
                eventos.popleft()
            if len(eventos) >= self.maximo:
                return False
            eventos.append(ahora)
            if len(self._eventos) > 10_000:
                self._purgar(ahora)
            return True

    def verificar(self, clave: str) -> None:
        """Igual que `permitir`, pero lanza 429 si se superó el límite."""
        if not self.permitir(clave):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas solicitudes. Espera unos minutos e inténtalo de nuevo.",
            )

    def reiniciar(self) -> None:
        with self._candado:
            self._eventos.clear()

    def _purgar(self, ahora: float) -> None:
        vencidas = [c for c, ev in self._eventos.items() if not ev or ahora - ev[-1] >= self.ventana]
        for clave in vencidas:
            del self._eventos[clave]


def ip_cliente(request: Request) -> str:
    """IP real del cliente, aunque falsee la cabecera X-Forwarded-For.

    Cada proxy agrega al final la IP de quien le habló. Con `proxies_confiables`
    proxies propios, la IP real es la entrada en esa posición contando desde el
    final; lo que haya antes lo pudo escribir el cliente y se ignora.
    """
    directa = request.client.host if request.client else "desconocida"
    saltos = settings.proxies_confiables
    reenviada = request.headers.get("x-forwarded-for")
    if saltos == 0 or not reenviada:
        return directa
    cadena = [ip.strip() for ip in reenviada.split(",") if ip.strip()]
    if not cadena:
        return directa
    return cadena[-saltos] if len(cadena) >= saltos else cadena[0]


def limite_por_ip(maximo: int, ventana_segundos: float):
    """Crea una dependencia de FastAPI que limita la frecuencia por IP."""
    limitador = Limitador(maximo, ventana_segundos)
    _registrados.append(limitador)

    def _dependencia(request: Request) -> None:
        limitador.verificar(f"{request.url.path}|{ip_cliente(request)}")

    return _dependencia


def limitador_registrado(maximo: int, ventana_segundos: float) -> Limitador:
    """Crea un limitador que se reinicia junto con los demás (p. ej. por cuenta)."""
    limitador = Limitador(maximo, ventana_segundos)
    _registrados.append(limitador)
    return limitador


def reiniciar_limitadores() -> None:
    """Vacía todos los contadores (útil en tests)."""
    for limitador in _registrados:
        limitador.reiniciar()


# Límites por endpoint público (por IP).
limite_login = limite_por_ip(maximo=20, ventana_segundos=60)
limite_registro = limite_por_ip(maximo=10, ventana_segundos=3600)
limite_radicar_pqrs = limite_por_ip(maximo=20, ventana_segundos=3600)
limite_seguimiento = limite_por_ip(maximo=60, ventana_segundos=60)
limite_responder_encuesta = limite_por_ip(maximo=30, ventana_segundos=3600)
limite_subidas = limite_por_ip(maximo=30, ventana_segundos=3600)
# Intentos de login por cuenta desde una misma IP (frena la fuerza bruta sin que
# un atacante pueda bloquear al dueño de la cuenta, que entra desde otra IP).
limite_login_por_cuenta_e_ip = limitador_registrado(maximo=10, ventana_segundos=900)
# Tope global por cuenta, más alto, contra ataques repartidos entre muchas IP.
limite_login_por_cuenta = limitador_registrado(maximo=50, ventana_segundos=900)


class CuerpoDemasiadoGrande(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="La petición supera el tamaño máximo permitido.",
        )


class LimiteTamanoCuerpo:
    """Middleware ASGI que corta las peticiones cuyo cuerpo supera `maximo_bytes`.

    Revisa Content-Length (rechazo inmediato) y además cuenta los bytes recibidos,
    para cubrir las peticiones enviadas por fragmentos sin esa cabecera.
    """

    def __init__(self, app: ASGIApp, maximo_bytes: int):
        self.app = app
        self.maximo = maximo_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        declarado = dict(scope.get("headers", [])).get(b"content-length")
        if declarado is not None and declarado.isdigit() and int(declarado) > self.maximo:
            await self._responder_413(send)
            return

        recibidos = 0

        async def _receive_acotado() -> Message:
            nonlocal recibidos
            mensaje = await receive()
            if mensaje["type"] == "http.request":
                recibidos += len(mensaje.get("body", b""))
                if recibidos > self.maximo:
                    raise CuerpoDemasiadoGrande()
            return mensaje

        await self.app(scope, _receive_acotado, send)

    @staticmethod
    async def _responder_413(send: Send) -> None:
        cuerpo = b'{"detail":"La petici\\u00f3n supera el tama\\u00f1o m\\u00e1ximo permitido."}'
        await send(
            {
                "type": "http.response.start",
                "status": status.HTTP_413_CONTENT_TOO_LARGE,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(cuerpo)).encode()),
                ],
            }
        )
        await send({"type": "http.response.body", "body": cuerpo})
