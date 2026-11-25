"""Columnas de control de avisos de plazo en las PQRS.

En las filas existentes quedan NULL, que la aplicación trata como "aún no avisado"
(se podrán avisar en el próximo chequeo de plazos).

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


def downgrade() -> None:
    op.drop_column("pqrs", "aviso_vencido_enviado")
    op.drop_column("pqrs", "aviso_previo_enviado")
