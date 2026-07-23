import enum
import secrets
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_slug() -> str:
    return secrets.token_urlsafe(12)


class TriggerType(str, enum.Enum):
    webhook = "webhook"
    cron = "cron"
    telegram = "telegram"


class RunStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class Tenant(Base):
    """One row per Telegram user (or team owner) — the unit of isolation."""

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workflows = relationship("Workflow", back_populates="tenant", cascade="all, delete-orphan")
    credentials = relationship("Credential", back_populates="tenant", cascade="all, delete-orphan")


class Credential(Base):
    """Encrypted secrets (API keys, tokens) a tenant's connectors can use."""

    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    encrypted_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="credentials")


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)

    trigger_type = Column(Enum(TriggerType), nullable=False)
    # webhook: {} (nothing extra needed, slug below is the address)
    # cron: {"interval_seconds": 300, "next_run": "2026-07-23T10:00:00"}
    # telegram: {"command": "ship"}  -> fires on /ship from the owner
    trigger_config = Column(JSON, default=dict)

    webhook_slug = Column(String, unique=True, default=gen_slug, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="workflows")
    steps = relationship(
        "Step", back_populates="workflow", cascade="all, delete-orphan", order_by="Step.order"
    )
    runs = relationship("Run", back_populates="workflow", cascade="all, delete-orphan")


class Step(Base):
    """One action in a workflow's chain. Executed in `order`."""

    __tablename__ = "steps"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    order = Column(Integer, default=0)
    connector_type = Column(String, nullable=False)  # matches CONNECTOR_REGISTRY key
    config = Column(JSON, default=dict)

    workflow = relationship("Workflow", back_populates="steps")


class Run(Base):
    """One execution of a workflow, for history/debugging."""

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.pending)
    trigger_payload = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    workflow = relationship("Workflow", back_populates="runs")
