from app.services.auth.validaciones import is_password_strong, is_valid_email, normalizar_email


def test_password_too_short():
    assert not is_password_strong("Abc1")


def test_password_sin_mayuscula():
    assert not is_password_strong("abcdefg1")


def test_password_sin_numero():
    assert not is_password_strong("Abcdefgh")


def test_password_valida():
    assert is_password_strong("Abcdefg1")


def test_email_valido():
    assert is_valid_email("juanca@test.com")


def test_email_sin_arroba():
    assert not is_valid_email("juanca.test.com")


def test_email_sin_dominio():
    assert not is_valid_email("juanca@")


def test_email_con_espacio():
    assert not is_valid_email("juan ca@test.com")


def test_normalizar_email_recorta_y_pasa_a_minusculas():
    assert normalizar_email("  Ana.Gomez@Test.COM ") == "ana.gomez@test.com"
