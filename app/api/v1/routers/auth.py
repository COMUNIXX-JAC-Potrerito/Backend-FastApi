from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserLogin
from app.schemas.token import Token
from app.services.auth.gestion import login_user

router = APIRouter()


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    access_token = login_user(db, credentials.email, credentials.password)

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    return {"access_token": access_token, "token_type": "bearer"}