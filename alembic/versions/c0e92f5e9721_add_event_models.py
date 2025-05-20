"""Add event models

Revision ID: c0e92f5e9721
Revises: 02411897f536
Create Date: 2025-05-20 15:45:30.673319

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c0e92f5e9721'
down_revision = '02411897f536'
branch_labels = None
depends_on = None


def upgrade():
    # Check if tables already exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Only proceed if tables don't exist
    if 'events' not in existing_tables:
        # Check if enum types exist before creating
        has_userrole = False
        has_recurrencepattern = False
        
        for enum in inspector.get_enums():
            if enum['name'] == 'userrole':
                has_userrole = True
            elif enum['name'] == 'recurrencepattern':
                has_recurrencepattern = True
        
        # Create UserRole enum type if it doesn't exist
        if not has_userrole:
            userrole_type = postgresql.ENUM('owner', 'editor', 'viewer', name='userrole')
            userrole_type.create(conn, checkfirst=True)
        
        # Create RecurrencePattern enum type if it doesn't exist
        if not has_recurrencepattern:
            recurrence_pattern_type = postgresql.ENUM('none', 'daily', 'weekly', 'monthly', 'yearly', 'custom', 
                                                 name='recurrencepattern')
            recurrence_pattern_type.create(conn, checkfirst=True)
    
    # Create events table
    op.create_table('events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, default=False),
        sa.Column('recurrence_pattern', sa.Enum('none', 'daily', 'weekly', 'monthly', 'yearly', 'custom', 
                                                name='recurrencepattern'), default='none'),
        sa.Column('recurrence_rule', postgresql.JSON(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), default=1, nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_title'), 'events', ['title'], unique=False)
    op.create_index(op.f('ix_events_start_time'), 'events', ['start_time'], unique=False)
    op.create_index(op.f('ix_events_end_time'), 'events', ['end_time'], unique=False)
    
    # Create event_permissions table
    op.create_table('event_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('owner', 'editor', 'viewer', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_permissions_id'), 'event_permissions', ['id'], unique=False)
    
    # Create event_versions table
    op.create_table('event_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('data', postgresql.JSON(), nullable=False),
        sa.Column('changed_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('change_description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'version', name='uix_event_version')
    )
    op.create_index(op.f('ix_event_versions_id'), 'event_versions', ['id'], unique=False)


def downgrade():
    # Check if tables exist before dropping
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Only drop tables that exist
    if 'event_versions' in existing_tables:
        op.drop_index(op.f('ix_event_versions_id'), table_name='event_versions')
        op.drop_table('event_versions')
    
    if 'event_permissions' in existing_tables:
        op.drop_index(op.f('ix_event_permissions_id'), table_name='event_permissions')
        op.drop_table('event_permissions')
    
    if 'events' in existing_tables:
        op.drop_index(op.f('ix_events_end_time'), table_name='events')
        op.drop_index(op.f('ix_events_start_time'), table_name='events')
        op.drop_index(op.f('ix_events_title'), table_name='events')
        op.drop_index(op.f('ix_events_id'), table_name='events')
        op.drop_table('events')
    
    # Check if enum types exist before dropping
    has_enum_types = False
    for enum in inspector.get_enums():
        if enum['name'] in ['recurrencepattern', 'userrole']:
            has_enum_types = True
            break
    
    if has_enum_types:
        # Drop enum types using conditional logic
        op.execute('DROP TYPE IF EXISTS recurrencepattern')
        op.execute('DROP TYPE IF EXISTS userrole')
