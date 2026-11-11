import ssl

import pytest

from app.db.session import opciones_motor
from app.services.envios import correo


def test_postgres_verifica_conexiones_antes_de_usarlas():
    opciones = opciones_motor("postgresql://u:p@host/db")
    assert opciones["pool_pre_ping"] is True
    assert opciones["pool_recycle"] > 0


def test_sqlite_no_usa_opciones_de_pool_de_postgres():
    opciones = opciones_motor("sqlite:///./dev.db")
    assert opciones == {"connect_args": {"check_same_thread": False}}


class _SMTPFalso:
    instancias: list = []

    def __init__(self, host, port, timeout=None):
        self.timeout = timeout
        self.contexto = None
        self.enviados = []
        _SMTPFalso.instancias.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def starttls(self, *, context=None):
        self.contexto = context

    def login(self, *_):
        pass

    def send_message(self, mensaje):
        if mensaje["To"] == "malo@test.com":
            raise correo.smtplib.SMTPRecipientsRefused({})
        self.enviados.append(mensaje["To"])


def test_smtp_verifica_el_certificado_y_cuenta_fallos(monkeypatch):
    _SMTPFalso.instancias = []
    monkeypatch.setattr(correo.smtplib, "SMTP", _SMTPFalso)
    monkeypatch.setattr(correo.settings, "smtp_host", "smtp.test")
    monkeypatch.setattr(correo.settings, "smtp_user", "jac@test.com")

    resultado = correo.enviar_correos(["a@test.com", "malo@test.com"], "Asunto", "Texto")

    servidor = _SMTPFalso.instancias[0]
    assert isinstance(servidor.contexto, ssl.SSLContext)
    assert servidor.contexto.verify_mode == ssl.CERT_REQUIRED
    assert servidor.timeout
    assert (resultado.enviados, resultado.fallidos, resultado.modo) == (1, 1, "parcial")


def test_sin_smtp_el_envio_es_simulado():
    resultado = correo.enviar_correos(["a@test.com"], "Asunto", "Texto")
    assert resultado.modo == "simulado"


def _origen_permitido(client, origen: str) -> bool:
    respuesta = client.options("/health", headers={"Origin": origen, "Access-Control-Request-Method": "GET"})
    return respuesta.headers.get("access-control-allow-origin") == origen


@pytest.mark.parametrize(
    "origen",
    [
        "https://comunix.vercel.app",
        "https://comunix-6fns6cas8-comunixx.vercel.app",
        "https://comunix-git-develop-comunixx.vercel.app",
    ],
)
def test_cors_acepta_los_despliegues_del_frontend(client, origen):
    assert _origen_permitido(client, origen)


@pytest.mark.parametrize(
    "origen",
    [
        "https://atacante.vercel.app",
        "https://comunix-falso.vercel.app",
        "https://comunix.vercel.app.atacante.com",
        "http://comunix.vercel.app",
    ],
)
def test_cors_no_acepta_cualquier_app_de_vercel(client, origen):
    assert not _origen_permitido(client, origen)


def test_health_responde_get_y_head(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.head("/health").status_code == 200
