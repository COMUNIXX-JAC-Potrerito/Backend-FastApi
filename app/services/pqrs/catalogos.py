"""Valores válidos del dominio PQRS (tipos, estados y comités/cargos).

La lista de comités/cargos se basa en la estructura de una Junta de Acción
Comunal en Colombia (Ley 2166 de 2021): cargos directivos + fiscal + comisiones
de trabajo. Es una lista INICIAL; se refinará con los estatutos reales de la
JAC de Potrerito.
"""

# Tipos de PQRS
TIPOS_VALIDOS = ["Peticion", "Queja", "Reclamo", "Sugerencia"]

# Estados del ciclo de vida de una PQRS
ESTADO_NUEVA = "Nueva"
ESTADO_EN_PROCESO = "En_Proceso"
ESTADO_FINALIZADA = "Finalizada"
ESTADOS_VALIDOS = [ESTADO_NUEVA, ESTADO_EN_PROCESO, ESTADO_FINALIZADA]

# A quién se puede asignar una PQRS: cargos (dignatarios) + comisiones de trabajo
COMITES_VALIDOS = [
    # Cargos / dignatarios
    "Presidente",
    "Vicepresidente",
    "Tesorero",
    "Secretario",
    "Fiscal",
    # Comisiones de trabajo
    "Comisión de Convivencia y Conciliación",
    "Comisión de Obras e Infraestructura",
    "Comisión de Deportes y Recreación",
    "Comisión de Salud",
    "Comisión de Medio Ambiente y Gestión del Riesgo",
    "Comisión de Educación y Cultura",
]


def es_tipo_valido(tipo: str) -> bool:
    return tipo in TIPOS_VALIDOS


def es_estado_valido(estado: str) -> bool:
    return estado in ESTADOS_VALIDOS


def es_comite_valido(comite: str) -> bool:
    return comite in COMITES_VALIDOS
