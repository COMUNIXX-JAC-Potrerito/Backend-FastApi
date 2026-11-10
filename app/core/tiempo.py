"""Fechas del sistema.

Las columnas de la base son `DateTime` sin zona horaria y siempre guardan UTC.
`ahora_utc` reemplaza a `datetime.utcnow()` (obsoleto desde Python 3.12) sin
cambiar ese formato, para no mezclar fechas con y sin zona en comparaciones.
"""

from datetime import UTC, datetime


def ahora_utc() -> datetime:
    """Fecha y hora actual en UTC, sin información de zona (como en la base)."""
    return datetime.now(UTC).replace(tzinfo=None)
