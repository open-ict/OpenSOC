from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base


class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    plan = Column(String(50), default='starter', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship('User', back_populates='tenant', cascade='all, delete-orphan')
    integrations = relationship('TenantIntegration', back_populates='tenant', cascade='all, delete-orphan')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='owner', nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    oidc_subject = Column(String(255), nullable=True)

    tenant = relationship('Tenant', back_populates='users')


class TenantIntegration(Base):
    __tablename__ = 'tenant_integrations'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    provider = Column(String(50), nullable=False)
    base_url = Column(String(500), nullable=False)
    username = Column(String(255), nullable=False)
    encrypted_password = Column(Text, nullable=False)
    verify_ssl = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    rotated_at = Column(DateTime, nullable=True)

    tenant = relationship('Tenant', back_populates='integrations')
    __table_args__ = (UniqueConstraint('tenant_id', 'provider', name='uq_tenant_provider'),)


class Endpoint(Base):
    __tablename__ = 'endpoints'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    wazuh_agent_id = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    ip = Column(String(64), nullable=True)
    os = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    last_seen = Column(String(128), nullable=True)
    __table_args__ = (UniqueConstraint('tenant_id', 'wazuh_agent_id', name='uq_tenant_agent'),)


class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    external_id = Column(String(255), nullable=False)
    rule_level = Column(Integer, nullable=True)
    rule_description = Column(Text, nullable=True)
    agent_name = Column(String(255), nullable=True)
    timestamp = Column(String(128), nullable=True)
    raw = Column(Text, nullable=True)
    __table_args__ = (UniqueConstraint('tenant_id', 'external_id', name='uq_tenant_alert'),)


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=True)
    actor_email = Column(String(255), nullable=True)
    action = Column(String(255), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class NotificationChannel(Base):
    __tablename__ = 'notification_channels'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    type = Column(String(50), nullable=False)
    target = Column(String(500), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, unique=True)
    plan = Column(String(50), default='starter', nullable=False)
    status = Column(String(50), default='trial', nullable=False)
    endpoint_limit = Column(Integer, default=50, nullable=False)
    current_period_end = Column(String(64), nullable=True)


class SyncJob(Base):
    __tablename__ = 'sync_jobs'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    job_type = Column(String(50), nullable=False)
    status = Column(String(50), default='queued', nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TenantPolicy(Base):
    __tablename__ = 'tenant_policies'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, unique=True)
    min_alert_level = Column(Integer, default=7, nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    auto_sync_enabled = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
