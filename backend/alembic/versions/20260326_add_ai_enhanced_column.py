"""Add ai_enhanced column to parsed_resume_data

Revision ID: 002
Revises: 001
Create Date: 2026-03-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add ai_enhanced column to parsed_resume_data table
    op.add_column(
        'parsed_resume_data',
        sa.Column('ai_enhanced', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    # Remove ai_enhanced column
    op.drop_column('parsed_resume_data', 'ai_enhanced')
