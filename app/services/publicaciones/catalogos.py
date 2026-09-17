"""Categorías válidas de una publicación."""

CATEGORIA_DECISION = "decision"     # HU11: decisiones tomadas en reuniones
CATEGORIA_ACTIVIDAD = "actividad"   # HU12: actividades comunitarias
CATEGORIA_CONTENIDO = "contenido"   # HU13: contenidos institucionales

CATEGORIAS_VALIDAS = [CATEGORIA_DECISION, CATEGORIA_ACTIVIDAD, CATEGORIA_CONTENIDO]


def es_categoria_valida(categoria: str) -> bool:
    return categoria in CATEGORIAS_VALIDAS
