"""add conversation and message tables for ai chatbot

Revision ID: b7c8d9e0f1g2
Revises: a1b2c3d4e5f6
Create Date: 2026-01-21 14:00:00.000000

This migration adds tables for AI chatbot conversation persistence:
- conversations: Chat sessions between user and AI assistant
- messages: Individual messages within conversations

Design follows stateless architecture with conversation_id as only state token.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1g2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create conversations and messages tables with proper relationships and indexes."""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_conversations_user_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes on conversations table
    op.create_index(
        op.f('ix_conversations_user_id'),
        'conversations',
        ['user_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_conversations_updated_at'),
        'conversations',
        ['updated_at'],
        unique=False
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tool_call_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['conversations.id'],
            name='fk_messages_conversation_id',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_messages_user_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create composite index for efficient chronological message retrieval
    # This is CRITICAL for performance - most queries fetch messages for a conversation ordered by time
    op.create_index(
        'ix_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at'],
        unique=False
    )

    # Create index on user_id for user isolation enforcement
    op.create_index(
        op.f('ix_messages_user_id'),
        'messages',
        ['user_id'],
        unique=False
    )


def downgrade() -> None:
    """Drop messages and conversations tables."""

    # Drop tables in reverse order (respect foreign key constraints)
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    op.drop_index('ix_messages_conversation_created', table_name='messages')
    op.drop_table('messages')

    op.drop_index(op.f('ix_conversations_updated_at'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_table('conversations')
