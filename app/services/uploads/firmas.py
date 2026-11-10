"""Verificación del tipo real de un archivo por sus primeros bytes ("firma").

El `Content-Type` lo declara el cliente y se puede falsear (p. ej. un HTML con
script enviado como "image/png"). Aquí se exige que el contenido coincida con la
familia declarada. SVG queda excluido a propósito: puede contener scripts.
"""

from collections.abc import Callable

Firma = Callable[[bytes], bool]


def _empieza(*prefijos: bytes) -> Firma:
    return lambda datos: datos.startswith(prefijos)


def _riff(subtipo: bytes) -> Firma:
    return lambda datos: datos[:4] == b"RIFF" and datos[8:12] == subtipo


def _iso_bmff(datos: bytes) -> bool:
    """Contenedor ISO (MP4, MOV, M4A, 3GP, HEIC, AVIF): caja "ftyp" en el byte 4."""
    return datos[4:8] == b"ftyp"


def _mpeg_audio(datos: bytes) -> bool:
    """MP3 (con etiqueta ID3 o sin ella) y AAC con cabecera ADTS."""
    return datos.startswith(b"ID3") or (len(datos) > 1 and datos[0] == 0xFF and datos[1] & 0xE0 == 0xE0)


def _texto_plano(datos: bytes) -> bool:
    if b"\x00" in datos:
        return False
    try:
        datos.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


_EBML = _empieza(b"\x1a\x45\xdf\xa3")  # WebM / Matroska
_OGG = _empieza(b"OggS")
_ZIP = _empieza(b"PK\x03\x04")  # .docx / .xlsx
_OLE = _empieza(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")  # .doc / .xls

_FIRMAS_IMAGEN: tuple[Firma, ...] = (
    _empieza(b"\xff\xd8\xff"),  # JPEG
    _empieza(b"\x89PNG\r\n\x1a\n"),
    _empieza(b"GIF87a", b"GIF89a"),
    _riff(b"WEBP"),
    _empieza(b"BM"),
    _empieza(b"II*\x00", b"MM\x00*"),  # TIFF
    _iso_bmff,  # HEIC / AVIF (fotos de celular)
)
_FIRMAS_VIDEO: tuple[Firma, ...] = (
    _iso_bmff,
    _EBML,
    _OGG,
    _riff(b"AVI "),
    _empieza(b"\x00\x00\x01\xba", b"\x00\x00\x01\xb3"),  # MPEG
)
_FIRMAS_AUDIO: tuple[Firma, ...] = (
    _mpeg_audio,
    _riff(b"WAVE"),
    _OGG,
    _EBML,  # notas de voz grabadas en el navegador
    _iso_bmff,  # M4A
    _empieza(b"fLaC", b"#!AMR"),
)
_FIRMAS_DOCUMENTO: dict[str, tuple[Firma, ...]] = {
    "application/pdf": (_empieza(b"%PDF-"),),
    "application/msword": (_OLE,),
    "application/vnd.ms-excel": (_OLE,),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (_ZIP,),
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": (_ZIP,),
    "text/plain": (_texto_plano,),
}
_FIRMAS_POR_FAMILIA: dict[str, tuple[Firma, ...]] = {
    "image/": _FIRMAS_IMAGEN,
    "video/": _FIRMAS_VIDEO,
    "audio/": _FIRMAS_AUDIO,
}
_TIPOS_EXCLUIDOS = {"image/svg+xml"}


def _firmas_para(content_type: str) -> tuple[Firma, ...]:
    tipo = content_type.split(";", maxsplit=1)[0].strip().lower()
    if tipo in _TIPOS_EXCLUIDOS:
        return ()
    if tipo in _FIRMAS_DOCUMENTO:
        return _FIRMAS_DOCUMENTO[tipo]
    for familia, firmas in _FIRMAS_POR_FAMILIA.items():
        if tipo.startswith(familia):
            return firmas
    return ()


def tipo_declarado_permitido(content_type: str | None) -> bool:
    """El tipo declarado está entre los admitidos (sin mirar el contenido)."""
    return bool(content_type) and bool(_firmas_para(content_type))


def contenido_coincide(content_type: str | None, contenido: bytes) -> bool:
    """El contenido es realmente del tipo declarado."""
    if not content_type:
        return False
    return any(firma(contenido) for firma in _firmas_para(content_type))
