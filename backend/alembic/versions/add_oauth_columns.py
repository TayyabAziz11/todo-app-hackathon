"""add_oauth_columns

Revision ID: a1b2c3d4e5f6
Revises: 67230ddffbc4
Create Date: 2025-01-08 12:00:00.000000

This migration adds OAuth support columns to the users table:
- oauth_provider: The OAuth provider name (google, github)
- oauth_id: Unique ID from the OAuth provider
- name: User's display name (from OAuth profile)
- avatar_url: Profile picture URL (from OAuth)
- Also makes hashed_password nullable for OAuth users
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '67230ddffbc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add OAuth support columns to users table."""

    # Add oauth_provider column
    op.add_column(
        'users',
        sa.Column('oauth_provider', sa.String(length=50), nullable=True)
    )

    # Add oauth_id column
    op.add_column(
        'users',
        sa.Column('oauth_id', sa.String(length=255), nullable=True)
    )

    # Add name column
    op.add_column(
        'users',
        sa.Column('name', sa.String(length=255), nullable=True)
    )

    # Add avatar_url column
    op.add_column(
        'users',
        sa.Column('avatar_url', sa.String(length=500), nullable=True)
    )

    # Make hashed_password nullable (for OAuth users who don't have passwords)
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.String(length=255),
        nullable=True
    )


def downgrade() -> None:
    """Remove OAuth columns from users table."""

    # Make hashed_password non-nullable again
    # Note: This will fail if there are OAuth users without passwords
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.String(length=255),
        nullable=False
    )

    # Drop the OAuth columns
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'name')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
