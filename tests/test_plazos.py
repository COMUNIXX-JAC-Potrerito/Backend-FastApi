"""Pruebas del cálculo de días hábiles y fecha límite de las PQRS."""

from datetime import datetime

from app.models.pqrs import PQRS
from app.services.pqrs.plazos import fecha_limite, sumar_dias_habiles


def test_sumar_dias_habiles_salta_fin_de_semana():
    viernes = datetime(2026, 11, 6, 10, 0)
    assert sumar_dias_habiles(viernes, 1).date() == datetime(2026, 11, 9).date()  # lunes


def test_sumar_dias_habiles_salta_festivo_colombiano():
    # martes 2026-12-08 es festivo (Inmaculada); lunes + 1 hábil = miércoles.
    lunes = datetime(2026, 12, 7, 10, 0)
    assert sumar_dias_habiles(lunes, 1).date() == datetime(2026, 12, 9).date()


def test_fecha_limite_none_para_sugerencia():
    pqrs = PQRS(tipo="Sugerencia", created_at=datetime(2026, 11, 6, 10, 0))
    assert fecha_limite(pqrs) is None


def test_fecha_limite_peticion_son_15_dias_habiles():
    creado = datetime(2026, 11, 6, 10, 0)
    pqrs = PQRS(tipo="Peticion", created_at=creado)
    assert fecha_limite(pqrs) == sumar_dias_habiles(creado, 15)
