import re

# Formato básico de correo: algo@algo.algo (sin espacios ni segundo @)
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_password_strong(password: str) -> bool:
    if len(password) < 8:
        return False

    if not any(c.isupper() for c in password):
        return False

    if not any(c.isdigit() for c in password):
        return False

    return True


def is_valid_email(email: str) -> bool:
    return bool(_EMAIL_REGEX.match(email))
