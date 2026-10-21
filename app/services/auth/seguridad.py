# Funciones para cifrar y verificar contraseñas de forma segura usando bcrypt.
from passlib.context import CryptContext

# Contexto de hashing para generar contraseñas seguras y compatibles con verificación futura.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hashea la contraseña antes de guardarla en la base de datos.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Compara la contraseña en texto plano con la versión cifrada almacenada.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)