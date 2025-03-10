"""Add pdf_name column to podcast_sessions

Revision ID: 285526461d3a
Revises: 
Create Date: 2025-02-22 03:15:52.279557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '285526461d3a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('podcast_sessions', sa.Column('pdf_name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('podcast_sessions', 'pdf_name')
    # ### end Alembic commands ###
