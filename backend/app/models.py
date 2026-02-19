import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .database import Base

class UserStatus(enum.Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(Text)
    status = Column(Enum(UserStatus), default=UserStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    refresh_tokens = relationship("RefreshToken", back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token_hash = Column(Text, nullable=False)
    device_info = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

class TokenType(enum.Enum):
    email_verification = "email_verification"
    password_reset = "password_reset"
    email_change = "email_change"
    trial_access = "trial_access"

class OneTimeToken(Base):
    __tablename__ = "one_time_tokens"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token_hash = Column(Text, nullable=False)
    type = Column(Enum(TokenType), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Plan(Base):
    __tablename__ = "plans"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    container_type = Column(String, nullable=False)
    container_id = Column(String(36), nullable=False)
    metadata = Column(JSONB, default={})
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    visibility = Column(String, default="private")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(BigInteger, default=1)

    memberships = relationship("Membership", back_populates="plan")
    buckets = relationship("Bucket", back_populates="plan")


class Membership(Base):
    __tablename__ = "memberships"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, default="member")
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="memberships")


class Bucket(Base):
    __tablename__ = "buckets"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    order_hint = Column(String, nullable=False)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("Plan", back_populates="buckets")
    tasks = relationship("Task", back_populates="bucket")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    bucket_id = Column(String(36), ForeignKey("buckets.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    details = Column(JSONB, default={})
    assignments = Column(JSONB, default={})
    labels = Column(JSONB, default=list)
    order_hint = Column(String, nullable=False)
    percent_complete = Column(Integer, default=0)
    priority = Column(Integer, default=0)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(BigInteger, default=1)

    bucket = relationship("Bucket", back_populates="tasks")
    checklists = relationship("Checklist", back_populates="task")
    attachments = relationship("Attachment", back_populates="task")
    comments = relationship("Comment", back_populates="task")


class Checklist(Base):
    __tablename__ = "checklists"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=True)
    items = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="checklists")


class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=True)
    size = Column(BigInteger, nullable=True)
    mime = Column(String, nullable=True)
    storage_ref = Column(JSONB, default={})
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="attachments")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")


class Event(Base):
    __tablename__ = "events"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    aggregate_type = Column(String, nullable=False)
    aggregate_id = Column(String(36), nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    aggregate_version = Column(BigInteger, nullable=False, default=1)


class Snapshot(Base):
    __tablename__ = "snapshots"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    aggregate_type = Column(String, nullable=False)
    aggregate_id = Column(String(36), nullable=False)
    snapshot = Column(JSONB, nullable=False)
    last_event_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
