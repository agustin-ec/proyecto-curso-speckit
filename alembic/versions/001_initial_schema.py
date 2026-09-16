"""initial schema with usuarios and gastos

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Table: usuarios
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_usuarios')
    )
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)
    op.create_index('ix_usuarios_id', 'usuarios', ['id'], unique=False)

    # Table: gastos
    op.create_table(
        'gastos',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('descripcion', sa.String(length=255), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.CheckConstraint('monto > 0', name='check_monto_positivo'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='fk_gastos_usuario_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_gastos')
    )
    op.create_index('ix_gastos_id', 'gastos', ['id'], unique=False)
    op.create_index('ix_gastos_categoria', 'gastos', ['categoria'], unique=False)
    op.create_index('ix_gastos_usuario_id', 'gastos', ['usuario_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_gastos_usuario_id', table_name='gastos')
    op.drop_index('ix_gastos_categoria', table_name='gastos')
    op.drop_index('ix_gastos_id', table_name='gastos')
    op.drop_table('gastos')
    op.drop_index('ix_usuarios_id', table_name='usuarios')
    op.drop_index('ix_usuarios_email', table_name='usuarios')
    op.drop_table('usuarios')
