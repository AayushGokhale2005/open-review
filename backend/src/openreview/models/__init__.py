"""SQLAlchemy ORM models."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from openreview.db.session import Base


def _uuid() -> str:
    return str(uuid4())


class GitProvider(str, enum.Enum):
    GITHUB = "github"
    GITLAB = "gitlab"


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommentSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(back_populates="user")
    settings: Mapped[AppSettings | None] = relationship(back_populates="user", uselist=False)


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[GitProvider] = mapped_column(Enum(GitProvider))
    provider_user_id: Mapped[str] = mapped_column(String(128))
    username: Mapped[str] = mapped_column(String(255))
    access_token_enc: Mapped[str] = mapped_column(Text)
    refresh_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="oauth_accounts")


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[GitProvider] = mapped_column(Enum(GitProvider))
    remote_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    default_branch: Mapped[str] = mapped_column(String(128), default="main")
    clone_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    html_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    open_pr_count: Mapped[int] = mapped_column(Integer, default=0)
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    pull_requests: Mapped[list[PullRequest]] = relationship(back_populates="repository")


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    repository_id: Mapped[str] = mapped_column(ForeignKey("repositories.id"), index=True)
    remote_id: Mapped[str] = mapped_column(String(128))
    number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(512))
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str] = mapped_column(String(32), default="open")
    author: Mapped[str] = mapped_column(String(255))
    author_avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_branch: Mapped[str] = mapped_column(String(255))
    target_branch: Mapped[str] = mapped_column(String(255))
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    changed_files: Mapped[int] = mapped_column(Integer, default=0)
    html_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    draft: Mapped[bool] = mapped_column(Boolean, default=False)
    labels: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    repository: Mapped[Repository] = relationship(back_populates="pull_requests")
    reviews: Mapped[list[Review]] = relationship(back_populates="pull_request")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    pull_request_id: Mapped[str] = mapped_column(ForeignKey("pull_requests.id"), index=True)
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    provider: Mapped[str] = mapped_column(String(64), default="ollama")
    model: Mapped[str] = mapped_column(String(128), default="llama3.2")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(64), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    agent_results: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pull_request: Mapped[PullRequest] = relationship(back_populates="reviews")
    comments: Mapped[list[ReviewComment]] = relationship(back_populates="review")


class ReviewComment(Base):
    __tablename__ = "review_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    review_id: Mapped[str] = mapped_column(ForeignKey("reviews.id"), index=True)
    agent: Mapped[str] = mapped_column(String(64))
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    line_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[CommentSeverity] = mapped_column(
        Enum(CommentSeverity), default=CommentSeverity.INFO
    )
    title: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    review: Mapped[Review] = relationship(back_populates="comments")


class AppSettings(Base):
    __tablename__ = "settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    theme: Mapped[str] = mapped_column(String(32), default="dark")
    ai_provider: Mapped[str] = mapped_column(String(64), default="ollama")
    ai_model: Mapped[str] = mapped_column(String(128), default="llama3.2")
    review_strictness: Mapped[str] = mapped_column(String(32), default="balanced")
    auto_review: Mapped[bool] = mapped_column(Boolean, default=False)
    ignored_files: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    custom_rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    repos_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    telemetry_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    openai_api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    anthropic_api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    openrouter_api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="settings")


class CachedMetadata(Base):
    __tablename__ = "cached_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    cache_key: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSON)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(128))
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
