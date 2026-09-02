from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.pqrs import router as pqrs_router
from app.db.session import Base, engine
from app.models import (  # noqa: F401  (importados para que Base registre las tablas antes de create_all)
    pqrs,
    user,
)

# Crea las tablas que aún no existan al arrancar (users, etc.)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="COMUNIX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # origen de Angular en dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(pqrs_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
