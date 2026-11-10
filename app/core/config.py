"""Configuración central: se lee de variables de entorno (o del archivo `.env`)."""

from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Valores de ejemplo que nunca deben usarse para firmar tokens reales.
_CLAVES_DE_EJEMPLO = {"cambia-esto-por-una-clave-secreta-larga"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Cadena de conexión de SQLAlchemy (PostgreSQL en producción, SQLite en local).
    database_url: str
    # Clave para firmar los JWT. Generar con:
    #   python -c "import secrets; print(secrets.token_urlsafe(48))"
    secret_key: str = Field(min_length=32)

    # Orígenes permitidos por CORS, separados por coma.
    cors_origins: str = "http://localhost:4200"
    # Patrón de orígenes dinámicos: solo los despliegues del frontend del proyecto
    # en Vercel (URL oficial y URLs de cada deploy), no cualquier app de Vercel.
    cors_origin_regex: str | None = r"https://frontend-angular-comunixx(-[a-z0-9-]+)?\.vercel\.app"

    # Proxies delante de la app. En Render son 2: Cloudflare (anota la IP del
    # cliente) y el balanceador de Render (anota la de Cloudflare), así que
    # X-Forwarded-For llega como "<cliente>, <borde de Cloudflare>". La IP real es
    # la entrada en esa posición contando desde el final; lo anterior lo puede
    # escribir el cliente. Un valor menor tomaría la IP de Cloudflare, compartida
    # por muchos usuarios (y los límites los bloquearían a todos). 0 = sin proxy.
    proxies_confiables: int = Field(default=2, ge=0, le=10)

    # SMTP para el envío masivo (opcional). Sin host/usuario, el envío es "simulado".
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None

    # Cloudinary: cloudinary://<api_key>:<api_secret>@<cloud_name>. Sin él, no hay subidas.
    cloudinary_url: str | None = None

    @field_validator("secret_key")
    @classmethod
    def _rechazar_clave_de_ejemplo(cls, valor: str) -> str:
        if valor in _CLAVES_DE_EJEMPLO:
            raise ValueError("SECRET_KEY usa el valor de ejemplo; genera una clave propia")
        return valor

    @property
    def lista_cors_origins(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]

    @property
    def cloudinary_cloud_name(self) -> str | None:
        """Nombre de la nube de Cloudinary, para validar que los adjuntos vengan de ella."""
        if not self.cloudinary_url:
            return None
        return urlparse(self.cloudinary_url).hostname


settings = Settings()
