"""align uuid column types

Revision ID: f3a8b2c90d1e
Revises: 321072f98829
Create Date: 2026-06-12 00:00:00.000000

Fix: EventTransaction.id was created as Integer in the initial migration but
the ORM model declares it as UUID(as_uuid=True). This migration corrects the
column type so that Alembic-managed databases match the ORM definition.

The upgrade drops and recreates the id column (safest path for a type change
that has no meaningful CAST from integer to UUID). Rows already in the table
will get a new random UUID assigned via the server default. On a fresh
database there are no rows, so this is always safe.

The downgrade reverts to INTEGER with autoincrement, discarding UUID values.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f3a8b2c90d1e"
down_revision: str | None = "321072f98829"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Change eventtransaction.id from Integer to UUID."""
    op.drop_constraint("eventtransaction_pkey", "eventtransaction", type_="primary")
    op.drop_column("eventtransaction", "id")
    op.add_column(
        "eventtransaction",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )
    op.create_primary_key("eventtransaction_pkey", "eventtransaction", ["id", "timestamp"])
    op.alter_column("eventtransaction", "id", server_default=None)


def downgrade() -> None:
    """Revert eventtransaction.id back to Integer (data loss — UUID values are discarded)."""
    op.drop_constraint("eventtransaction_pkey", "eventtransaction", type_="primary")
    op.drop_column("eventtransaction", "id")
    op.add_column(
        "eventtransaction",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    )
    op.create_primary_key("eventtransaction_pkey", "eventtransaction", ["id", "timestamp"])
