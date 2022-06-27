"""Update: Updated forms_data's data type.

Revision ID: e0432d936a75
Revises: 2880526ae7a9
Create Date: 2022-06-27 04:40:07.377812

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e0432d936a75'
down_revision = '2880526ae7a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'folders', ['id'])
    op.alter_column('forms_data', 'data',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=False)
    op.create_unique_constraint(None, 'labels', ['id'])
    op.create_unique_constraint(None, 'roles', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'roles', type_='unique')
    op.drop_constraint(None, 'labels', type_='unique')
    op.alter_column('forms_data', 'data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               type_=postgresql.JSONB(astext_type=sa.Text()),
               existing_nullable=False)
    op.drop_constraint(None, 'folders', type_='unique')
    # ### end Alembic commands ###
