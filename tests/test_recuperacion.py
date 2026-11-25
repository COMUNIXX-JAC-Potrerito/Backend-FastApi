"""Pruebas del flujo de recuperación de contraseña."""

import secrets
from datetime import timedelta

from app.core.tiempo import ahora_utc
from app.models.recuperacion import PasswordResetToken
from app.services.auth.recuperacion import hash_token


def _crear_token(db, usuario, vencido=False):
    raw = secrets.token_urlsafe(16)
    db.add(
        PasswordResetToken(
            user_id=usuario.id,
            token_hash=hash_token(raw),
            expires_at=ahora_utc() + (timedelta(hours=-1) if vencido else timedelta(hours=1)),
        )
    )
    db.commit()
    return raw


def test_recuperar_no_revela_si_el_correo_existe(client, ciudadano):
    r1 = client.post("/api/recuperar", json={"email": "no-existe@test.com"})
    r2 = client.post("/api/recuperar", json={"email": ciudadano.email})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()


def test_restablecer_cambia_la_clave_con_token_valido(client, db, ciudadano):
    raw = _crear_token(db, ciudadano)
    r = client.post("/api/restablecer", json={"token": raw, "password": "NuevaClave1"})
    assert r.status_code == 200
    login = client.post(
        "/api/login", json={"email": ciudadano.email, "password": "NuevaClave1"}
    )
    assert login.status_code == 200


def test_restablecer_rechaza_token_vencido(client, db, ciudadano):
    raw = _crear_token(db, ciudadano, vencido=True)
    r = client.post("/api/restablecer", json={"token": raw, "password": "NuevaClave1"})
    assert r.status_code == 400


def test_restablecer_rechaza_token_ya_usado(client, db, ciudadano):
    raw = _crear_token(db, ciudadano)
    client.post("/api/restablecer", json={"token": raw, "password": "NuevaClave1"})
    r = client.post("/api/restablecer", json={"token": raw, "password": "OtraClave2"})
    assert r.status_code == 400
