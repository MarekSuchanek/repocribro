"""empty message

Revision ID: d397ce02489b
Revises: 
Create Date: 2017-01-21 19:33:33.615805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd397ce02489b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UserAccount',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('RepositoryOwner',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('github_id', sa.Integer(), nullable=True),
    sa.Column('login', sa.String(length=40), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('name', sa.UnicodeText(), nullable=True),
    sa.Column('company', sa.UnicodeText(), nullable=True),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.Column('location', sa.UnicodeText(), nullable=True),
    sa.Column('blog_url', sa.UnicodeText(), nullable=True),
    sa.Column('avatar_url', sa.String(length=255), nullable=True),
    sa.Column('type', sa.String(length=30), nullable=True),
    sa.Column('hireable', sa.Boolean(), nullable=True),
    sa.Column('user_account_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_account_id'], ['UserAccount.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('github_id'),
    sa.UniqueConstraint('login')
    )
    op.create_table('Repository',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('github_id', sa.Integer(), nullable=True),
    sa.Column('fork_of', sa.Integer(), nullable=True),
    sa.Column('full_name', sa.String(length=150), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('languages', sa.UnicodeText(), nullable=True),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.Column('private', sa.Boolean(), nullable=True),
    sa.Column('visibility_type', sa.Integer(), nullable=True),
    sa.Column('secret', sa.String(length=255), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['RepositoryOwner.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('full_name'),
    sa.UniqueConstraint('github_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Repository')
    op.drop_table('RepositoryOwner')
    op.drop_table('UserAccount')
    # ### end Alembic commands ###