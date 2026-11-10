from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator

from app.schemas.comunes import Codigo, Correo, DesdeORM, Telefono

# bcrypt solo usa los primeros 72 bytes: una clave más larga se truncaría sin aviso.
_MAX_BYTES_CLAVE = 72


class UserLogin(BaseModel):
    email: Correo
    password: Annotated[str, Field(max_length=128)]


class UserCreate(BaseModel):
    full_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    email: Correo
    password: Annotated[str, Field(max_length=128)]
    phone: Telefono

    @field_validator("password")
    @classmethod
    def _limite_bcrypt(cls, valor: str) -> str:
        if len(valor.encode("utf-8")) > _MAX_BYTES_CLAVE:
            raise ValueError("la contraseña no puede superar 72 bytes")
        return valor


class UserResponse(DesdeORM):
    id: int
    email: str
    full_name: str
    phone: str | None = None
    role: str
    comite: str | None = None


class CambiarRol(BaseModel):
    rol: Codigo


class CambiarComite(BaseModel):
    # Comité/comisión del dignatario. Vacío ("") lo deja sin comisión.
    comite: Annotated[str, Field(max_length=100)]
