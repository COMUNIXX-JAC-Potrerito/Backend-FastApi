from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers.auth import router as auth_router

app = FastAPI(title="COMUNIX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # origen de Angular en dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}