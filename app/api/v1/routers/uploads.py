"""Subida de adjuntos a Cloudinary.

Es pública porque las PQRS anónimas también pueden llevar adjunto; por eso tiene
límite de frecuencia, de tamaño y verificación del tipo real del archivo.
"""

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.limites import limite_subidas
from app.schemas.upload import AdjuntoResponse
from app.services.uploads import almacenamiento

router = APIRouter(tags=["uploads"])


# `def` (no `async def`): FastAPI lo ejecuta en un hilo aparte, así la lectura del
# archivo y la llamada a Cloudinary no bloquean al resto de peticiones.
@router.post(
    "/uploads",
    response_model=AdjuntoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limite_subidas)],
)
def subir(archivo: UploadFile = File(...)):
    """Sube una imagen, video, audio o documento y devuelve su URL pública."""
    almacenamiento.validar_tipo_declarado(archivo.content_type)
    contenido = almacenamiento.leer_con_limite(archivo.file)
    almacenamiento.validar_contenido(archivo.content_type, contenido)
    return almacenamiento.subir_archivo(contenido, almacenamiento.nombre_seguro(archivo.filename))
