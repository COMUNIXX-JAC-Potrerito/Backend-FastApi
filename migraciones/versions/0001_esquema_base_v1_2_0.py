"""Esquema base: las tablas tal como las creaba create_all hasta la v1.2.0.

Una base que ya las tiene (Neon) no ejecuta esta migración: app/db/migrar.py la
marca como aplicada. Coincide con la estructura de Neon revisada el 2026-11-10.

Revisión: 0001
Anterior:
Fecha: 2026-11-10 00:45:02.876654
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("comite", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_users_email"), ["email"], unique=True)
        batch_op.create_index(batch_op.f("ix_users_id"), ["id"], unique=False)

    op.create_table(
        "comunicaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("entidad", sa.String(), nullable=False),
        sa.Column("asunto", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=True),
        sa.Column("fecha", sa.DateTime(), nullable=True),
        sa.Column("registrado_por_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["registrado_por_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("comunicaciones", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_comunicaciones_id"), ["id"], unique=False)

    op.create_table(
        "encuestas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=True),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("publicada", sa.Boolean(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("encuestas", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_encuestas_id"), ["id"], unique=False)

    op.create_table(
        "envios_masivos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asunto", sa.String(), nullable=False),
        sa.Column("contenido", sa.String(), nullable=False),
        sa.Column("destinatarios", sa.Integer(), nullable=True),
        sa.Column("modo", sa.String(), nullable=True),
        sa.Column("enviado_por_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["enviado_por_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("envios_masivos", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_envios_masivos_id"), ["id"], unique=False)

    op.create_table(
        "mensajes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("remitente_id", sa.Integer(), nullable=False),
        sa.Column("destinatario_id", sa.Integer(), nullable=False),
        sa.Column("asunto", sa.String(), nullable=False),
        sa.Column("contenido", sa.String(), nullable=False),
        sa.Column("leido", sa.Boolean(), nullable=True),
        sa.Column("fijado", sa.Boolean(), nullable=True),
        sa.Column("editado", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("adjunto_url", sa.String(), nullable=True),
        sa.Column("adjunto_tipo", sa.String(), nullable=True),
        sa.Column("adjunto_nombre", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["destinatario_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["remitente_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("mensajes", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_mensajes_id"), ["id"], unique=False)

    op.create_table(
        "pqrs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo_seguimiento", sa.String(), nullable=True),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("asunto", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=False),
        sa.Column("estado", sa.String(), nullable=False),
        sa.Column("es_anonima", sa.Boolean(), nullable=True),
        sa.Column("radicado_por_id", sa.Integer(), nullable=True),
        sa.Column("nombre_contacto", sa.String(), nullable=True),
        sa.Column("email_contacto", sa.String(), nullable=True),
        sa.Column("telefono_contacto", sa.String(), nullable=True),
        sa.Column("comite", sa.String(), nullable=True),
        sa.Column("respuesta", sa.String(), nullable=True),
        sa.Column("respuesta_fecha", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("adjunto_url", sa.String(), nullable=True),
        sa.Column("adjunto_tipo", sa.String(), nullable=True),
        sa.Column("adjunto_nombre", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["radicado_por_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("pqrs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_pqrs_codigo_seguimiento"), ["codigo_seguimiento"], unique=True)
        batch_op.create_index(batch_op.f("ix_pqrs_id"), ["id"], unique=False)

    op.create_table(
        "publicaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("categoria", sa.String(), nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("contenido", sa.String(), nullable=False),
        sa.Column("fecha_evento", sa.DateTime(), nullable=True),
        sa.Column("publicado_por_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("adjunto_url", sa.String(), nullable=True),
        sa.Column("adjunto_tipo", sa.String(), nullable=True),
        sa.Column("adjunto_nombre", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["publicado_por_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("publicaciones", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_publicaciones_id"), ["id"], unique=False)

    op.create_table(
        "preguntas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("encuesta_id", sa.Integer(), nullable=False),
        sa.Column("texto", sa.String(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("opciones", sa.String(), nullable=True),
        sa.Column("orden", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["encuesta_id"],
            ["encuestas.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("preguntas", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_preguntas_id"), ["id"], unique=False)

    op.create_table(
        "respuestas_encuesta",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("encuesta_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("nombre", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("telefono", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["encuesta_id"],
            ["encuestas.id"],
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("respuestas_encuesta", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_respuestas_encuesta_id"), ["id"], unique=False)

    op.create_table(
        "respuestas_pqrs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pqrs_id", sa.Integer(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=True),
        sa.Column("texto", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["autor_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pqrs_id"],
            ["pqrs.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("respuestas_pqrs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_respuestas_pqrs_id"), ["id"], unique=False)
        batch_op.create_index(batch_op.f("ix_respuestas_pqrs_pqrs_id"), ["pqrs_id"], unique=False)

    op.create_table(
        "respuesta_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("respuesta_id", sa.Integer(), nullable=False),
        sa.Column("pregunta_id", sa.Integer(), nullable=False),
        sa.Column("valor", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["pregunta_id"],
            ["preguntas.id"],
        ),
        sa.ForeignKeyConstraint(
            ["respuesta_id"],
            ["respuestas_encuesta.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("respuesta_items", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_respuesta_items_id"), ["id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("respuesta_items", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_respuesta_items_id"))

    op.drop_table("respuesta_items")
    with op.batch_alter_table("respuestas_pqrs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_respuestas_pqrs_pqrs_id"))
        batch_op.drop_index(batch_op.f("ix_respuestas_pqrs_id"))

    op.drop_table("respuestas_pqrs")
    with op.batch_alter_table("respuestas_encuesta", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_respuestas_encuesta_id"))

    op.drop_table("respuestas_encuesta")
    with op.batch_alter_table("preguntas", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_preguntas_id"))

    op.drop_table("preguntas")
    with op.batch_alter_table("publicaciones", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_publicaciones_id"))

    op.drop_table("publicaciones")
    with op.batch_alter_table("pqrs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_pqrs_id"))
        batch_op.drop_index(batch_op.f("ix_pqrs_codigo_seguimiento"))

    op.drop_table("pqrs")
    with op.batch_alter_table("mensajes", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_mensajes_id"))

    op.drop_table("mensajes")
    with op.batch_alter_table("envios_masivos", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_envios_masivos_id"))

    op.drop_table("envios_masivos")
    with op.batch_alter_table("encuestas", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_encuestas_id"))

    op.drop_table("encuestas")
    with op.batch_alter_table("comunicaciones", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_comunicaciones_id"))

    op.drop_table("comunicaciones")
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_id"))
        batch_op.drop_index(batch_op.f("ix_users_email"))

    op.drop_table("users")
