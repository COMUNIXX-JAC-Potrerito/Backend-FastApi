"""Aplicación FastAPI: middlewares, manejadores de errores y routers."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registra todos los modelos antes de usarlos)
from app.api.v1.routers import (
    auth,
    comunicaciones,
    encuestas,
    envios,
    mensajes,
    pqrs,
    publicaciones,
    reportes,
    uploads,
    usuarios,
)
from app.core.cabeceras import CabecerasSeguridad
from app.core.config import settings
from app.core.errores import registrar_manejadores
from app.core.limites import LimiteTamanoCuerpo
from app.core.logs import configurar_logs
from app.db.migrar import migrar

# Tamaño máximo de cualquier petición: el adjunto (10 MB) más el resto del formulario.
MAX_BYTES_PETICION = 12 * 1024 * 1024

ROUTERS = (
    auth,
    pqrs,
    usuarios,
    publicaciones,
    mensajes,
    comunicaciones,
    envios,
    reportes,
    uploads,
    encuestas,
)


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI) -> AsyncIterator[None]:
    # Aplica las migraciones pendientes (crea o modifica tablas). Ver docs/migraciones.md.
    migrar(settings.database_url)
    yield


configurar_logs()

app = FastAPI(title="COMUNIX API", lifespan=ciclo_de_vida)

registrar_manejadores(app)
app.add_middleware(LimiteTamanoCuerpo, maximo_bytes=MAX_BYTES_PETICION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.lista_cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Último en agregarse = el más externo: decora todas las respuestas, incluidos 413 y CORS.
app.add_middleware(CabecerasSeguridad)

for modulo in ROUTERS:
    app.include_router(modulo.router, prefix="/api")


# GET y HEAD: los monitores de disponibilidad (UptimeRobot) suelen usar HEAD.
@app.api_route("/health", methods=["GET", "HEAD"], tags=["salud"])
def health_check():
    return {"status": "ok"}
