"""Plazo legal de respuesta de las PQRS, en días hábiles.

Según la Ley 1755 de 2015 la regla general del derecho de petición es de 15 días
hábiles. Aquí se aplica a Petición, Queja y Reclamo; las Sugerencias no tienen
plazo estricto. Los días hábiles excluyen fines de semana y festivos de Colombia.
"""

from datetime import datetime, timedelta

import holidays

from app.models.pqrs import PQRS

DIAS_LIMITE = 15
_TIPOS_CON_PLAZO = frozenset({"Peticion", "Queja", "Reclamo"})
_festivos = holidays.CO()


def _es_habil(dia: datetime) -> bool:
    return dia.weekday() < 5 and dia.date() not in _festivos


def sumar_dias_habiles(desde: datetime, n: int) -> datetime:
    """Devuelve la fecha n días hábiles después de `desde` (sin contar `desde`)."""
    dia = desde
    restantes = n
    while restantes > 0:
        dia += timedelta(days=1)
        if _es_habil(dia):
            restantes -= 1
    return dia


def fecha_limite(pqrs: PQRS) -> datetime | None:
    """Fecha límite legal de respuesta, o None si el tipo no tiene plazo."""
    if pqrs.tipo not in _TIPOS_CON_PLAZO:
        return None
    return sumar_dias_habiles(pqrs.created_at, DIAS_LIMITE)
