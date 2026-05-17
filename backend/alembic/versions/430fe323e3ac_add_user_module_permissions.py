"""add user module_permissions

Revision ID: 430fe323e3ac
Revises: 159de8fc55fb
Create Date: 2026-05-17 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '430fe323e3ac'
down_revision: Union[str, Sequence[str], None] = '159de8fc55fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('module_permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'module_permissions')
