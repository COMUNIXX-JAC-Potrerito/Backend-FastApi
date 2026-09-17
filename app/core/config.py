from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str

    # Config SMTP para el envío masivo de correos (OPCIONAL).
    # Si no se define smtp_host/smtp_user, el envío masivo funciona en modo
    # "simulado" (registra el envío pero no manda correos reales).
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()