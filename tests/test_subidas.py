"""POST /api/uploads: tamaño acotado, tipo real verificado y errores controlados."""

import pytest

from app.services.uploads.firmas import contenido_coincide

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
PDF = b"%PDF-1.7\n" + b"0" * 64
HTML = b"<html><script>alert(1)</script></html>"


@pytest.fixture
def cloudinary_falso(monkeypatch):
    llamadas = []

    def _upload(contenido, **opciones):
        llamadas.append(opciones)
        return {"secure_url": "https://res.cloudinary.com/nube-pruebas/x.png", "resource_type": "image"}

    monkeypatch.setattr("cloudinary.uploader.upload", _upload)
    return llamadas


@pytest.mark.parametrize(
    ("tipo", "contenido", "esperado"),
    [
        ("image/png", PNG, True),
        ("image/png", HTML, False),
        ("image/svg+xml", b"<svg onload='alert(1)'/>", False),
        ("application/pdf", PDF, True),
        ("application/pdf", PNG, False),
        ("audio/webm;codecs=opus", b"\x1a\x45\xdf\xa3" + b"\x00" * 16, True),
        ("video/mp4", b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 16, True),
        ("text/plain", b"Hola, comunidad", True),
        ("text/plain", b"\x00\x01binario", False),
    ],
)
def test_contenido_coincide_con_el_tipo_declarado(tipo, contenido, esperado):
    assert contenido_coincide(tipo, contenido) is esperado


def test_subida_valida_devuelve_la_url(client, cloudinary_falso):
    respuesta = client.post("/api/uploads", files={"archivo": ("foto.png", PNG, "image/png")})
    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "url": "https://res.cloudinary.com/nube-pruebas/x.png",
        "tipo": "image",
        "nombre": "foto.png",
    }


def test_subida_rechaza_html_disfrazado_de_imagen(client, cloudinary_falso):
    respuesta = client.post("/api/uploads", files={"archivo": ("x.png", HTML, "image/png")})
    assert respuesta.status_code == 400
    assert cloudinary_falso == []


def test_subida_rechaza_archivo_de_mas_de_10_mb_sin_subirlo(client, cloudinary_falso):
    grande = PNG + b"\x00" * (10 * 1024 * 1024)
    respuesta = client.post("/api/uploads", files={"archivo": ("g.png", grande, "image/png")})
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El archivo supera el límite de 10 MB."
    assert cloudinary_falso == []


def test_subida_vacia_se_rechaza(client, cloudinary_falso):
    respuesta = client.post("/api/uploads", files={"archivo": ("v.png", b"", "image/png")})
    assert respuesta.status_code == 400


def test_fallo_de_cloudinary_responde_502_sin_detalles_internos(client, monkeypatch):
    def _falla(*_args, **_kwargs):
        raise RuntimeError("api_secret=filtrado")

    monkeypatch.setattr("cloudinary.uploader.upload", _falla)
    respuesta = client.post("/api/uploads", files={"archivo": ("f.png", PNG, "image/png")})
    assert respuesta.status_code == 502
    assert "filtrado" not in respuesta.text


def test_subidas_tienen_limite_de_frecuencia(client, cloudinary_falso):
    codigos = [
        client.post("/api/uploads", files={"archivo": ("f.png", PNG, "image/png")}).status_code
        for _ in range(31)
    ]
    assert codigos[:30] == [201] * 30
    assert codigos[30] == 429
