from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.comunicaciones import router as comunicaciones_router
from app.api.v1.routers.encuestas import router as encuestas_router
from app.api.v1.routers.envios import router as envios_router
from app.api.v1.routers.mensajes import router as mensajes_router
from app.api.v1.routers.pqrs import router as pqrs_router
from app.api.v1.routers.publicaciones import router as publicaciones_router
from app.api.v1.routers.reportes import router as reportes_router
from app.api.v1.routers.uploads import router as uploads_router
from app.api.v1.routers.usuarios import router as usuarios_router
from app.core.config import settings
from app.db.session import Base, engine
from app.models import (  # noqa: F401  (importados para que Base registre las tablas antes de create_all)
    comunicacion,
    encuesta,
    envio_masivo,
    mensaje,
    pqrs,
    publicacion,
    user,
)

# Crea las tablas que aún no existan al arrancar (users, etc.)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="COMUNIX API")

# Orígenes permitidos (dev + los que se configuren en producción vía CORS_ORIGINS).
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=settings.cors_origin_regex,  # acepta las URLs de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(pqrs_router, prefix="/api")
app.include_router(usuarios_router, prefix="/api")
app.include_router(publicaciones_router, prefix="/api")
app.include_router(mensajes_router, prefix="/api")
app.include_router(comunicaciones_router, prefix="/api")
app.include_router(envios_router, prefix="/api")
app.include_router(reportes_router, prefix="/api")
app.include_router(uploads_router, prefix="/api")
app.include_router(encuestas_router, prefix="/api")


# GET y HEAD: los monitores de uptime (UptimeRobot, etc.) suelen usar HEAD.
@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok"}
