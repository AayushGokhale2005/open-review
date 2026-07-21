"""Dashboard aggregate endpoints."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from openreview.db.session import get_db
from openreview.models import PullRequest, Repository, Review, ReviewComment, ReviewStatus
from openreview.repositories import PullRequestRepository, RepositoryRepository, ReviewRepository
from openreview.schemas import (
    ActivityItem,
    DashboardOut,
    DashboardStats,
    PullRequestOut,
    RepositoryOut,
    ReviewOut,
)

router = APIRouter()


@router.get("", response_model=DashboardOut)
async def get_dashboard(db: AsyncSession = Depends(get_db)) -> DashboardOut:
    repo_repo = RepositoryRepository(db)
    pr_repo = PullRequestRepository(db)
    review_repo = ReviewRepository(db)

    repos = await repo_repo.search(limit=50)
    prs = await pr_repo.list_open(limit=10)
    reviews = await review_repo.recent(limit=5)

    repo_count = await db.scalar(select(func.count()).select_from(Repository)) or 0
    open_prs = await db.scalar(
        select(func.count()).select_from(PullRequest).where(PullRequest.state == "open")
    ) or 0
    completed = await db.scalar(
        select(func.count())
        .select_from(Review)
        .where(Review.status == ReviewStatus.COMPLETED)
    ) or 0
    avg_health = await db.scalar(select(func.avg(Repository.health_score))) or 0
    comments = await db.scalar(select(func.count()).select_from(ReviewComment)) or 0

    activity = [
        ActivityItem(
            id="a1",
            type="review_completed",
            title="Review completed",
            description="AI review finished on feat: add modular AI review pipeline",
            timestamp=datetime.now(UTC) - timedelta(hours=2),
            meta={"score": 83},
        ),
        ActivityItem(
            id="a2",
            type="repo_connected",
            title="Repository connected",
            description="Connected acme/open-review",
            timestamp=datetime.now(UTC) - timedelta(days=1),
        ),
        ActivityItem(
            id="a3",
            type="pr_opened",
            title="Pull request opened",
            description="#41 fix: prevent token leakage in OAuth callback",
            timestamp=datetime.now(UTC) - timedelta(days=1, hours=4),
        ),
        ActivityItem(
            id="a4",
            type="provider_configured",
            title="AI provider ready",
            description="Ollama configured as default provider",
            timestamp=datetime.now(UTC) - timedelta(days=2),
        ),
    ]

    return DashboardOut(
        stats=DashboardStats(
            repositories=int(repo_count),
            open_pull_requests=int(open_prs),
            reviews_completed=int(completed),
            avg_health_score=int(avg_health),
            comments_this_week=int(comments),
        ),
        recent_reviews=[ReviewOut.model_validate(r) for r in reviews],
        latest_pull_requests=[PullRequestOut.model_validate(p) for p in prs],
        activity=activity,
        repositories=[RepositoryOut.model_validate(r) for r in repos],
    )
