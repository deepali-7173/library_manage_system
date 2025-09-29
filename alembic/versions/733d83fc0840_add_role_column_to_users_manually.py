from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'new_revision_id_here'
down_revision = '5c62f8ba4880'  # the last correct migration
branch_labels = None
depends_on = None

def upgrade():
    # Add 'role' column to existing 'User' table
    op.add_column('user', sa.Column('role', sa.String(length=50), nullable=False, server_default='student'))

def downgrade():
    # Remove 'role' column if downgrading
    op.drop_column('user', 'role')

