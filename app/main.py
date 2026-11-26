"""Aplicación FastAPI: middlewares, manejadores de errores y routers."""

import asyncio
import contextlib
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
from app.services.notificaciones.plazos import iniciar_scheduler_plazos

# Tamaño máximo de cualquier petición: el adjunto (10 MB) más el resto del formulario.
MAX_BYTES_PETICION = 12 * 1024 * 1024

DESCRIPCION_API = (
    "API del backend de **COMUNIX**: radicación y seguimiento de PQRS "
    "(públicas o anónimas), gestión por comisiones de la JAC, publicaciones, "
    "encuestas, mensajería interna, comunicaciones y envíos.\n\n"
    "**Autenticación:** inicia sesión en `/api/login`, copia el token y úsalo "
    "con el botón **Authorize** 🔒 para probar los endpoints privados."
)

# Descripción y orden de los grupos de endpoints que se muestran en /docs.
TAGS_METADATA = [
    {"name": "auth", "description": "Registro, inicio de sesión y emisión de tokens JWT."},
    {"name": "pqrs", "description": "Radicación pública o anónima, seguimiento y gestión por comisiones."},
    {"name": "usuarios", "description": "Administración de dignatarios y roles (solo superadministrador)."},
    {"name": "publicaciones", "description": "Cartelera comunitaria: avisos y noticias públicas."},
    {"name": "encuestas", "description": "Encuestas y censos: creación, respuesta y resultados."},
    {"name": "mensajes", "description": "Mensajería interna entre dignatarios."},
    {"name": "comunicaciones", "description": "Bitácora de comunicaciones externas de la JAC."},
    {"name": "envios", "description": "Envío de boletines y correos masivos."},
    {"name": "reportes", "description": "Estadísticas y reportes de gestión (solo dignatarios)."},
    {"name": "uploads", "description": "Subida validada de adjuntos y firmas a Cloudinary."},
    {"name": "salud", "description": "Estado del servicio para los monitores de disponibilidad."},
]

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
    # Revisa los plazos de las PQRS cada hora (la instancia no se duerme: UptimeRobot).
    tarea_plazos = asyncio.create_task(iniciar_scheduler_plazos())
    try:
        yield
    finally:
        tarea_plazos.cancel()
        # Espera a que la tarea termine de cancelarse (apagado limpio).
        with contextlib.suppress(asyncio.CancelledError):
            await tarea_plazos


configurar_logs()

app = FastAPI(
    title="COMUNIX API",
    version="1.4.0",
    description=DESCRIPCION_API,
    openapi_tags=TAGS_METADATA,
    contact={"name": "Equipo COMUNIX — SENA ADSO", "url": "https://comunix.vercel.app"},
    license_info={"name": "MIT", "identifier": "MIT"},
    lifespan=ciclo_de_vida,
)

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
