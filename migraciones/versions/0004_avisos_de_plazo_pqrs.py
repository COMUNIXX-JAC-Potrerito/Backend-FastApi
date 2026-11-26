"""Columnas de control de avisos de plazo en las PQRS.

Las filas existentes se marcan como ya avisadas: la función de avisos de plazo
es prospectiva (avisa de las PQRS a partir del despliegue), para no disparar una
ráfaga retroactiva de correos sobre PQRS antiguas en el primer chequeo. Las PQRS
nuevas nacen en False (default del modelo) y sí reciben sus avisos.

Revisión: 0004
Anterior: 0003
Fecha: 2026-11-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("pqrs", sa.Column("aviso_previo_enviado", sa.Boolean(), nullable=True))
    op.add_column("pqrs", sa.Column("aviso_vencido_enviado", sa.Boolean(), nullable=True))
    # Marca las PQRS ya existentes como avisadas (envío prospectivo, sin ráfaga
    # retroactiva). Literal booleano por-dialecto: 1 en SQLite, true en Postgres.
    pqrs = sa.table(
        "pqrs",
        sa.column("aviso_previo_enviado", sa.Boolean()),
        sa.column("aviso_vencido_enviado", sa.Boolean()),
    )
    op.execute(pqrs.update().values(aviso_previo_enviado=True, aviso_vencido_enviado=True))


def downgrade() -> None:
    op.drop_column("pqrs", "aviso_vencido_enviado")
    op.drop_column("pqrs", "aviso_previo_enviado")
