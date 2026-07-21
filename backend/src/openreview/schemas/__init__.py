"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Auth ──────────────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    provider: str = Field(pattern="^(github|gitlab)$")


class LoginResponse(BaseModel):
    authorization_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    provider: str
    code: str
    state: str
    code_verifier: str | None = None


class OAuthAccountOut(ORMModel):
    id: str
    provider: str
    username: str
    provider_user_id: str


class UserOut(ORMModel):
    id: str
    display_name: str
    email: str | None
    avatar_url: str | None
    onboarding_completed: bool
    oauth_accounts: list[OAuthAccountOut] = []


# ── Repositories ──────────────────────────────────────────────────────────────


class RepositoryCreate(BaseModel):
    provider: str = "github"
    full_name: str
    name: str | None = None
    clone_url: str | None = None
    local_path: str | None = None
    language: str | None = None
    stars: int = 0
    default_branch: str = "main"
    description: str | None = None
    html_url: str | None = None


class RepositoryImportLocal(BaseModel):
    path: str
    name: str | None = None


class RepositoryOut(ORMModel):
    id: str
    provider: str
    name: str
    full_name: str
    description: str | None
    language: str | None
    stars: int
    default_branch: str
    clone_url: str | None
    local_path: str | None
    html_url: str | None
    open_pr_count: int
    health_score: int
    last_reviewed_at: datetime | None


# ── Pull Requests ─────────────────────────────────────────────────────────────


class PullRequestOut(ORMModel):
    id: str
    repository_id: str
    remote_id: str
    number: int
    title: str
    body: str | None
    state: str
    author: str
    author_avatar: str | None
    source_branch: str
    target_branch: str
    additions: int
    deletions: int
    changed_files: int
    html_url: str | None
    draft: bool
    labels: list[str] | None
    created_at: datetime
    updated_at: datetime


class FileDiff(BaseModel):
    path: str
    status: str  # added | modified | deleted | renamed
    additions: int
    deletions: int
    patch: str | None = None
    language: str | None = None


class PullRequestDetail(PullRequestOut):
    files: list[FileDiff] = []
    repository: RepositoryOut | None = None


# ── Reviews ───────────────────────────────────────────────────────────────────


class ReviewStartRequest(BaseModel):
    pull_request_id: str
    provider: str | None = None
    model: str | None = None


class ReviewCommentOut(ORMModel):
    id: str
    agent: str
    file_path: str | None
    line_start: int | None
    line_end: int | None
    severity: str
    title: str
    body: str
    suggestion: str | None


class ReviewOut(ORMModel):
    id: str
    pull_request_id: str
    status: str
    provider: str
    model: str
    summary: str | None
    verdict: str | None
    score: int | None
    agent_results: dict[str, Any] | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    comments: list[ReviewCommentOut] = []


# ── AI Providers ──────────────────────────────────────────────────────────────


class ProviderInfo(BaseModel):
    id: str
    name: str
    description: str
    local: bool
    requires_api_key: bool
    base_url: str | None = None
    models: list[str] = []
    available: bool = False
    configured: bool = False


class ProviderUpdate(BaseModel):
    provider: str | None = None
    model: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    base_url: str | None = None


# ── Settings ──────────────────────────────────────────────────────────────────


class SettingsOut(ORMModel):
    theme: str
    ai_provider: str
    ai_model: str
    review_strictness: str
    auto_review: bool
    ignored_files: list[str] | None
    custom_rules: str | None
    repos_path: str | None
    telemetry_enabled: bool
    has_openai_key: bool = False
    has_anthropic_key: bool = False
    has_openrouter_key: bool = False


class SettingsUpdate(BaseModel):
    theme: str | None = None
    ai_provider: str | None = None
    ai_model: str | None = None
    review_strictness: str | None = None
    auto_review: bool | None = None
    ignored_files: list[str] | None = None
    custom_rules: str | None = None
    repos_path: str | None = None
    telemetry_enabled: bool | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    onboarding_completed: bool | None = None


# ── Dashboard ─────────────────────────────────────────────────────────────────


class DashboardStats(BaseModel):
    repositories: int
    open_pull_requests: int
    reviews_completed: int
    avg_health_score: int
    comments_this_week: int


class ActivityItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: datetime
    meta: dict[str, Any] | None = None


class DashboardOut(BaseModel):
    stats: DashboardStats
    recent_reviews: list[ReviewOut]
    latest_pull_requests: list[PullRequestOut]
    activity: list[ActivityItem]
    repositories: list[RepositoryOut]
