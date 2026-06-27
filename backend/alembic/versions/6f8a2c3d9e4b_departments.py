"""departments — 部门管理与权限控制

Revision ID: 6f8a2c3d9e4b
Revises: 649c16d7abf3
Create Date: 2026-06-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f8a2c3d9e4b'
down_revision: Union[str, Sequence[str], None] = '649c16d7abf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级：新增 departments 表，修改 users/documents 表"""
    # 1. 创建 departments 表
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # 2. 预置默认部门
    op.execute(
        "INSERT INTO departments (name, description) VALUES "
        "('技术部', '软件开发、IT运维、技术支持'),"
        "('财务部', '财务核算、预算管理、审计'),"
        "('人事部', '招聘、培训、薪酬福利管理'),"
        "('市场部', '市场营销、品牌推广、客户关系'),"
        "('综合管理部', '行政后勤、法务合规、战略规划')"
    )

    # 3. users 表新增 department_id
    op.add_column(
        'users',
        sa.Column('department_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_users_department_id',
        'users', 'departments',
        ['department_id'], ['id'],
    )
    op.create_index(
        op.f('ix_users_department_id'),
        'users', ['department_id'],
        unique=False,
    )

    # 4. documents 表新增 department_id 和 visibility
    op.add_column(
        'documents',
        sa.Column('department_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_documents_department_id',
        'documents', 'departments',
        ['department_id'], ['id'],
    )
    op.create_index(
        op.f('ix_documents_department_id'),
        'documents', ['department_id'],
        unique=False,
    )

    op.add_column(
        'documents',
        sa.Column(
            'visibility',
            sa.Enum('public', 'department', 'restricted', name='doc_visibility'),
            nullable=False,
            server_default='public',
        ),
    )

    # 5. 创建 document_departments 关联表
    op.create_table(
        'document_departments',
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['document_id'], ['documents.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['department_id'], ['departments.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('document_id', 'department_id'),
    )
    op.create_index(
        op.f('ix_document_departments_document_id'),
        'document_departments', ['document_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_document_departments_department_id'),
        'document_departments', ['department_id'],
        unique=False,
    )


def downgrade() -> None:
    """回滚：删除所有新增内容"""
    # 删除 document_departments 表
    op.drop_index(
        op.f('ix_document_departments_department_id'),
        table_name='document_departments',
    )
    op.drop_index(
        op.f('ix_document_departments_document_id'),
        table_name='document_departments',
    )
    op.drop_table('document_departments')

    # 删除 documents 表的新增列
    op.drop_column('documents', 'visibility')
    op.drop_index(
        op.f('ix_documents_department_id'),
        table_name='documents',
    )
    op.drop_constraint('fk_documents_department_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'department_id')

    # 删除 users 表的新增列
    op.drop_index(
        op.f('ix_users_department_id'),
        table_name='users',
    )
    op.drop_constraint('fk_users_department_id', 'users', type_='foreignkey')
    op.drop_column('users', 'department_id')

    # 删除 departments 表
    op.drop_table('departments')
