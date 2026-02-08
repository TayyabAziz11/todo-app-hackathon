"""add_phase_v4_fields_to_todos

Revision ID: b7c8d9e0f1g2
Revises: add_conversation_and_message_tables
Create Date: 2026-02-07 17:00:00.000000

This migration adds Phase V.4 fields to the todos table:
- priority: Priority level enum (LOW, MEDIUM, HIGH, URGENT)
- tags: Array of tags for categorization
- due_date: When the todo is due
- search_vector: Full-text search vector (tsvector)

Also creates indexes:
- GIN index on search_vector for full-text search
- GIN index on tags for tag queries
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c8d9e0f1g2h3'
down_revision: Union[str, None] = 'b7c8d9e0f1g2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Phase V.4 fields to todos table."""

    # Create priority enum type
    priority_enum = postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='priority', create_type=True)
    priority_enum.create(op.get_bind(), checkfirst=True)

    # Add priority column
    op.add_column(
        'todos',
        sa.Column('priority', priority_enum, nullable=True)
    )

    # Add tags column (array of strings)
    op.add_column(
        'todos',
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True)
    )

    # Add due_date column
    op.add_column(
        'todos',
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True)
    )

    # Add search_vector column (tsvector for full-text search)
    op.add_column(
        'todos',
        sa.Column('search_vector', postgresql.TSVECTOR, nullable=True)
    )

    # Create GIN index on search_vector for full-text search
    op.create_index(
        'idx_todos_search_vector',
        'todos',
        ['search_vector'],
        postgresql_using='gin'
    )

    # Create GIN index on tags for efficient tag queries
    op.create_index(
        'idx_todos_tags',
        'todos',
        ['tags'],
        postgresql_using='gin'
    )

    # Create index on due_date for sorting/filtering
    op.create_index(
        'idx_todos_due_date',
        'todos',
        ['due_date']
    )

    # Create index on priority for sorting/filtering
    op.create_index(
        'idx_todos_priority',
        'todos',
        ['priority']
    )

    # Enable pg_trgm extension for fuzzy search (if not already enabled)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade() -> None:
    """Remove Phase V.4 fields from todos table."""

    # Drop indexes first
    op.drop_index('idx_todos_priority', table_name='todos')
    op.drop_index('idx_todos_due_date', table_name='todos')
    op.drop_index('idx_todos_tags', table_name='todos')
    op.drop_index('idx_todos_search_vector', table_name='todos')

    # Drop columns
    op.drop_column('todos', 'search_vector')
    op.drop_column('todos', 'due_date')
    op.drop_column('todos', 'tags')
    op.drop_column('todos', 'priority')

    # Drop the enum type
    priority_enum = postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='priority')
    priority_enum.drop(op.get_bind(), checkfirst=True)
