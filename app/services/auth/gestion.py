from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth.seguridad import hash_password, verify_password
from app.services.auth.tokens import create_access_token
from app.services.auth.validaciones import is_password_strong, is_valid_email


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)

    if not user:
        return None

    token_data = {"sub": user.email, "role": user.role}
    access_token = create_access_token(token_data)

    return access_token


def register_user(db: Session, full_name: str, email: str, password: str, phone: str) -> User:
    if not is_valid_email(email):
        raise ValueError("El correo no tiene un formato válido")

    if not is_password_strong(password):
        raise ValueError("La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("Ya existe un usuario registrado con ese correo")

    new_user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        phone=phone,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
