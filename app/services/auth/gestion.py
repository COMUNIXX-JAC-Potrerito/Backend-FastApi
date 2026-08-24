from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth.seguridad import verify_password
from app.services.auth.tokens import create_access_token


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