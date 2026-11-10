"""Una respuesta por cuenta en cada encuesta (índice único).

Antes de crear el índice se eliminan las respuestas repetidas de una misma cuenta
en una misma encuesta, conservando la primera (la de menor id) con sus ítems.
En Neon había 1 repetida, de pruebas (revisado el 2026-11-10).

El downgrade quita el índice, pero no recupera las respuestas eliminadas.

Revisión: 0002
Anterior: 0001
Fecha: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDICE = "uq_respuestas_encuesta_encuesta_usuario"

# Respuestas de una cuenta que ya tenía una anterior en la misma encuesta.
_REPETIDAS = """
    SELECT r.id FROM respuestas_encuesta r
    WHERE r.usuario_id IS NOT NULL
      AND r.id > (
          SELECT MIN(p.id) FROM respuestas_encuesta p
          WHERE p.encuesta_id = r.encuesta_id AND p.usuario_id = r.usuario_id
      )
"""


def upgrade() -> None:
    # _REPETIDAS es una constante de este archivo: no lleva datos de usuarios.
    op.execute(sa.text(f"DELETE FROM respuesta_items WHERE respuesta_id IN ({_REPETIDAS})"))  # noqa: S608
    op.execute(sa.text(f"DELETE FROM respuestas_encuesta WHERE id IN ({_REPETIDAS})"))  # noqa: S608
    op.create_index(INDICE, "respuestas_encuesta", ["encuesta_id", "usuario_id"], unique=True)


def downgrade() -> None:
    op.drop_index(INDICE, table_name="respuestas_encuesta")
