"""Create table

Revision ID: 8d2151fdef46
Revises: 4af663c9411b
Create Date: 2025-06-22 10:49:13.435203

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d2151fdef46'
down_revision: Union[str, Sequence[str], None] = '4af663c9411b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('documents_text_doc_id_fkey', 'documents_text', type_='foreignkey')
    op.create_foreign_key(
    'documents_text_doc_id_fkey',
    'documents_text',
    'document',
    ['doc_id'],
    ['id'],
    ondelete='CASCADE'
)


def downgrade() -> None:
    op.drop_constraint('documents_text_doc_id_fkey', 'documents_text', type_='foreignkey')
    op.create_foreign_key(
    'documents_text_doc_id_fkey',
    'documents_text',
    'document',
    ['doc_id'],
    ['id'],
)