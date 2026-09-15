from app.services.auth.roles import ROLES_GESTION, es_rol_valido


def test_rol_valido():
    assert es_rol_valido("superadministrador") is True


def test_rol_invalido():
    assert es_rol_valido("jefe") is False


def test_gestion_incluye_admin_no_usuario():
    assert "administrador" in ROLES_GESTION
    assert "superadministrador" in ROLES_GESTION
    assert "usuario" not in ROLES_GESTION
