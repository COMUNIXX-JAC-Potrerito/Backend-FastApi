from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.comunes import Correo


class RecuperarRequest(BaseModel):
    email: Correo


class RestablecerRequest(BaseModel):
    token: Annotated[str, Field(min_length=10, max_length=200)]
    password: Annotated[str, Field(max_length=128)]
