from app.services.auth.validaciones import is_password_strong


def test_password_too_short():
    assert is_password_strong("Abc1") == False


def test_password_sin_mayuscula():
    assert is_password_strong("abcdefg1") == False


def test_password_sin_numero():
    assert is_password_strong("Abcdefgh") == False


def test_password_valida():
    assert is_password_strong("Abcdefg1") == True