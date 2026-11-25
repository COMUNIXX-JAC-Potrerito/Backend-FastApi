"""Pruebas de la selección de PQRS por plazo y del no-reenvío de avisos."""

import secrets
from datetime import timedelta

import holidays

from app.core.tiempo import ahora_utc
from app.models.pqrs import PQRS
from app.services.notificaciones.plazos import pqrs_por_avisar, revisar_plazos
from app.services.pqrs.plazos import sumar_dias_habiles

_CO = holidays.CO()


def _retroceder(fecha, n):
    """Fecha n días hábiles antes de `fecha` (para fabricar fechas de radicación)."""
    dia = fecha
    while n > 0:
        dia -= timedelta(days=1)
        if dia.weekday() < 5 and dia.date() not in _CO:
            n -= 1
    return dia


def _crear_pqrs(db, creado, tipo="Peticion", estado="En_Proceso", previo=False, vencido=False):
    pqrs = PQRS(
        tipo=tipo,
        asunto="Asunto",
        descripcion="Descripción",
        codigo_seguimiento=secrets.token_hex(5),
        estado=estado,
        comite="Comisión de Salud",
        created_at=creado,
        aviso_previo_enviado=previo,
        aviso_vencido_enviado=vencido,
    )
    db.add(pqrs)
    db.commit()
    db.refresh(pqrs)
    return pqrs


def test_selecciona_por_vencer_y_vencidas(db, crear_usuario):
    crear_usuario(comite="Comisión de Salud", email="dig@x.com")
    ahora = ahora_utc()
    creado_por_vencer = _retroceder(sumar_dias_habiles(ahora, 3), 15)  # vence en ~3 h
    creado_vencida = _retroceder(ahora, 20)  # venció hace ~5 h
    por_vencer = _crear_pqrs(db, creado_por_vencer)
    vencida = _crear_pqrs(db, creado_vencida)
    _crear_pqrs(db, creado_por_vencer, previo=True)  # ya avisada: se excluye
    _crear_pqrs(db, creado_por_vencer, estado="Finalizada")  # finalizada: se excluye
    _crear_pqrs(db, creado_por_vencer, tipo="Sugerencia")  # sin plazo: se excluye

    previas, vencidas = pqrs_por_avisar(db, ahora)
    assert {p.id for p in previas} == {por_vencer.id}
    assert {p.id for p in vencidas} == {vencida.id}


def test_revisar_plazos_marca_y_no_repite(db, crear_usuario):
    crear_usuario(comite="Comisión de Salud", email="dig@x.com")
    ahora = ahora_utc()
    _crear_pqrs(db, _retroceder(sumar_dias_habiles(ahora, 3), 15))
    _crear_pqrs(db, _retroceder(ahora, 20))

    revisar_plazos(db)

    previas, vencidas = pqrs_por_avisar(db, ahora_utc())
    assert previas == []
    assert vencidas == []
