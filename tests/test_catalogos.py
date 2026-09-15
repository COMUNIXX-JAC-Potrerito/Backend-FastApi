from app.services.pqrs.catalogos import (
    es_comite_valido,
    es_estado_valido,
    es_tipo_valido,
)


def test_tipo_valido():
    assert es_tipo_valido("Peticion") is True


def test_tipo_invalido():
    assert es_tipo_valido("Otro") is False


def test_estado_valido():
    assert es_estado_valido("En_Proceso") is True


def test_estado_invalido():
    assert es_estado_valido("Cerrada") is False


def test_comite_valido_cargo():
    assert es_comite_valido("Tesorero") is True


def test_comite_valido_comision():
    assert es_comite_valido("Comisión de Salud") is True


def test_comite_invalido():
    assert es_comite_valido("Comité Inventado") is False
