from app.services.auth.validaciones import is_password_strong, is_valid_email


def test_password_too_short():
    assert is_password_strong("Abc1") == False


def test_password_sin_mayuscula():
    assert is_password_strong("abcdefg1") == False


def test_password_sin_numero():
    assert is_password_strong("Abcdefgh") == False


def test_password_valida():
    assert is_password_strong("Abcdefg1") == True


def test_email_valido():
    assert is_valid_email("juanca@test.com") == True


def test_email_sin_arroba():
    assert is_valid_email("juanca.test.com") == False


def test_email_sin_dominio():
    assert is_valid_email("juanca@") == False


def test_email_con_espacio():
    assert is_valid_email("juan ca@test.com") == False
