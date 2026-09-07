"""add users table

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String()),
        sa.Column("phone", sa.String(), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String()),
        sa.Column("language", sa.String()),
        sa.Column("district", sa.String()),
        sa.Column("created_at", sa.DateTime()),
    )


def downgrade():
    op.drop_table("users")
