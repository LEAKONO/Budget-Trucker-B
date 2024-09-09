"""second migration

Revision ID: 9575821d58d4
Revises: 715e6d6a2165
Create Date: 2024-09-09 12:46:30.033959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9575821d58d4'
down_revision = '715e6d6a2165'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(length=150), nullable=False))
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.VARCHAR(length=150), nullable=False))
        batch_op.drop_column('password')

    # ### end Alembic commands ###
