from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str

    # Orígenes permitidos por CORS, separados por coma.
    # En producción se agrega el dominio del frontend (Vercel) por variable de entorno.
    cors_origins: str = "http://localhost:4200"

    # Patrón (regex) de orígenes permitidos, para dominios dinámicos.
    # Por defecto acepta cualquier subdominio de Vercel (las URLs cambian por deploy).
    cors_origin_regex: str | None = r"https://.*\.vercel\.app"

    # Config SMTP para el envío masivo de correos (OPCIONAL).
    # Si no se define smtp_host/smtp_user, el envío masivo funciona en modo
    # "simulado" (registra el envío pero no manda correos reales).
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None

    # Cloudinary (almacenamiento de multimedia/archivos). Formato:
    # cloudinary://<api_key>:<api_secret>@<cloud_name>
    # Si no se define, la subida de adjuntos queda deshabilitada (devuelve error claro).
    cloudinary_url: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()