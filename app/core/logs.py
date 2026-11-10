"""Configuración de logs de la aplicación (salida estándar, la recoge Render)."""

import logging


def configurar_logs(nivel: int = logging.INFO) -> None:
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
