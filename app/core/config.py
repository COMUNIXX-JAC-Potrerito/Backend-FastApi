# Configuración central de la aplicación: lee variables de entorno y centraliza
# la conexión a la base de datos, JWT y servicios externos como SMTP y Cloudinary.
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # URL de conexión a la base de datos (SQLite, PostgreSQL, etc.).
    database_url: str
    # Clave secreta usada para firmar y verificar tokens JWT de autenticación.
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
        # Carga las variables de entorno desde un archivo .env en el proyecto.
        env_file = ".env"


# Instancia global con todas las configuraciones leídas del entorno.
settings = Settings()