"""add profile visibility flags

Revision ID: initial
Revises: 
Create Date: 2025-07-13 16:44:31.987664

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем флаги видимости для каждого поля
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('show_status', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_bio', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_full_name', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_degree', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_interests', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_organization', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_location', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_scholar_links', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_website', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_birthdate', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_public_email', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('show_telegram', sa.Boolean(), nullable=True, server_default='1'))


def downgrade():
    # Удаляем добавленные флаги
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('show_telegram')
        batch_op.drop_column('show_public_email')
        batch_op.drop_column('show_birthdate')
        batch_op.drop_column('show_website')
        batch_op.drop_column('show_scholar_links')
        batch_op.drop_column('show_location')
        batch_op.drop_column('show_organization')
        batch_op.drop_column('show_interests')
        batch_op.drop_column('show_degree')
        batch_op.drop_column('show_full_name')
        batch_op.drop_column('show_bio')
        batch_op.drop_column('show_status')
