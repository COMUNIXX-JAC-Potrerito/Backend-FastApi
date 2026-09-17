from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.upload import AdjuntoResponse
from app.services.uploads.almacenamiento import subir_archivo

router = APIRouter()

# Límite de tamaño por archivo (10 MB) y tipos permitidos.
MAX_BYTES = 10 * 1024 * 1024
PREFIJOS_PERMITIDOS = ("image/", "video/", "audio/")
TIPOS_EXTRA = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
}


def _tipo_permitido(content_type: str | None) -> bool:
    if content_type is None:
        return False
    if content_type.startswith(PREFIJOS_PERMITIDOS):
        return True
    return content_type in TIPOS_EXTRA


@router.post("/uploads", response_model=AdjuntoResponse, status_code=status.HTTP_201_CREATED)
async def subir(archivo: UploadFile = File(...)):
    """Sube un archivo (imagen, video, audio o documento) a Cloudinary y
    devuelve su URL pública. Se usa tanto en mensajería como al radicar PQRS."""
    if not _tipo_permitido(archivo.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido (solo imágenes, video, audio o documentos).",
        )

    contenido = await archivo.read()
    if len(contenido) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo supera el límite de 10 MB.",
        )
    if len(contenido) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío.",
        )

    try:
        return subir_archivo(contenido, archivo.filename or "archivo")
    except ValueError as error:
        # Cloudinary no configurado
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo subir el archivo. Intenta de nuevo.",
        )
