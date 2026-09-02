from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str | None = None
    role: str

    class Config:
        from_attributes = True
