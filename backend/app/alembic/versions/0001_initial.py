"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-02 10:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('slug', sa.String(length=255), nullable=False, unique=True),
        sa.Column('plan', sa.String(length=50), nullable=False, server_default='starter'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='owner'),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('oidc_subject', sa.String(length=255), nullable=True),
    )
    op.create_table(
        'tenant_integrations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('base_url', sa.String(length=500), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('encrypted_password', sa.Text(), nullable=False),
        sa.Column('verify_ssl', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('rotated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('tenant_id', 'provider', name='uq_tenant_provider')
    )
    op.create_table(
        'endpoints',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('wazuh_agent_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('os', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('last_seen', sa.String(length=128), nullable=True),
        sa.UniqueConstraint('tenant_id', 'wazuh_agent_id', name='uq_tenant_agent')
    )
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('rule_level', sa.Integer(), nullable=True),
        sa.Column('rule_description', sa.Text(), nullable=True),
        sa.Column('agent_name', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.String(length=128), nullable=True),
        sa.Column('raw', sa.Text(), nullable=True),
        sa.UniqueConstraint('tenant_id', 'external_id', name='uq_tenant_alert')
    )
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('actor_email', sa.String(length=255), nullable=True),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'notification_channels',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('target', sa.String(length=500), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False, unique=True),
        sa.Column('plan', sa.String(length=50), nullable=False, server_default='starter'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='trial'),
        sa.Column('endpoint_limit', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('current_period_end', sa.String(length=64), nullable=True),
    )
    op.create_table(
        'sync_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'tenant_policies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False, unique=True),
        sa.Column('min_alert_level', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('auto_sync_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in ['tenant_policies', 'sync_jobs', 'subscriptions', 'notification_channels', 'audit_logs', 'alerts', 'endpoints', 'tenant_integrations', 'users', 'tenants']:
        op.drop_table(table)
