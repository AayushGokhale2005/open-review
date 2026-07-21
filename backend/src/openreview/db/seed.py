"""Seed realistic mock data for first-run dashboard experience."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from openreview.models import (
    AppSettings,
    CommentSeverity,
    GitProvider,
    PullRequest,
    Repository,
    Review,
    ReviewComment,
    ReviewStatus,
    User,
)


async def seed_if_empty(session: AsyncSession) -> None:
    count = await session.scalar(select(func.count()).select_from(User))
    if count and count > 0:
        return

    user = User(
        display_name="Local Developer",
        email="dev@localhost",
        avatar_url=None,
        onboarding_completed=False,
    )
    session.add(user)
    await session.flush()

    settings = AppSettings(user_id=user.id)
    session.add(settings)

    repos_data = [
        {
            "name": "open-review",
            "full_name": "acme/open-review",
            "description": "Local-first AI code review desktop app",
            "language": "TypeScript",
            "stars": 1284,
            "open_pr_count": 3,
            "health_score": 92,
            "provider": GitProvider.GITHUB,
        },
        {
            "name": "vector-db",
            "full_name": "acme/vector-db",
            "description": "Embedded vector search for local RAG",
            "language": "Rust",
            "stars": 512,
            "open_pr_count": 1,
            "health_score": 88,
            "provider": GitProvider.GITHUB,
        },
        {
            "name": "api-gateway",
            "full_name": "acme/api-gateway",
            "description": "Edge gateway with rate limiting",
            "language": "Go",
            "stars": 340,
            "open_pr_count": 2,
            "health_score": 76,
            "provider": GitProvider.GITLAB,
        },
        {
            "name": "design-system",
            "full_name": "acme/design-system",
            "description": "Shared React component library",
            "language": "TypeScript",
            "stars": 890,
            "open_pr_count": 0,
            "health_score": 95,
            "provider": GitProvider.GITHUB,
        },
    ]

    repos: list[Repository] = []
    for rd in repos_data:
        repo = Repository(
            user_id=user.id,
            provider=rd["provider"],
            remote_id=rd["full_name"],
            name=rd["name"],
            full_name=rd["full_name"],
            description=rd["description"],
            language=rd["language"],
            stars=rd["stars"],
            default_branch="main",
            clone_url=f"https://github.com/{rd['full_name']}.git",
            html_url=f"https://github.com/{rd['full_name']}",
            open_pr_count=rd["open_pr_count"],
            health_score=rd["health_score"],
            last_reviewed_at=datetime.now(UTC) - timedelta(days=2),
        )
        session.add(repo)
        repos.append(repo)
    await session.flush()

    prs = [
        PullRequest(
            repository_id=repos[0].id,
            remote_id="101",
            number=42,
            title="feat: add modular AI review pipeline",
            body="Introduces specialist agents for security, performance, and architecture reviews.",
            state="open",
            author="alice",
            author_avatar=None,
            source_branch="feat/review-engine",
            target_branch="main",
            additions=842,
            deletions=126,
            changed_files=18,
            html_url="https://github.com/acme/open-review/pull/42",
            labels=["enhancement", "ai"],
        ),
        PullRequest(
            repository_id=repos[0].id,
            remote_id="102",
            number=41,
            title="fix: prevent token leakage in OAuth callback",
            body="Encrypts tokens at rest and clears PKCE state after exchange.",
            state="open",
            author="bob",
            source_branch="fix/oauth-hardening",
            target_branch="main",
            additions=56,
            deletions=12,
            changed_files=4,
            html_url="https://github.com/acme/open-review/pull/41",
            labels=["security"],
        ),
        PullRequest(
            repository_id=repos[1].id,
            remote_id="55",
            number=12,
            title="perf: batch embedding upserts",
            body="Reduces write amplification when indexing large repositories.",
            state="open",
            author="carol",
            source_branch="perf/batch-upsert",
            target_branch="main",
            additions=210,
            deletions=88,
            changed_files=7,
            html_url="https://github.com/acme/vector-db/pull/12",
            labels=["performance"],
        ),
        PullRequest(
            repository_id=repos[2].id,
            remote_id="88",
            number=7,
            title="chore: upgrade rate limiter defaults",
            body="Aligns defaults with production traffic patterns.",
            state="open",
            author="dave",
            source_branch="chore/rate-limits",
            target_branch="main",
            additions=34,
            deletions=9,
            changed_files=2,
            html_url="https://gitlab.com/acme/api-gateway/-/merge_requests/7",
            labels=["chore"],
        ),
    ]
    for pr in prs:
        session.add(pr)
    await session.flush()

    review = Review(
        pull_request_id=prs[0].id,
        status=ReviewStatus.COMPLETED,
        provider="ollama",
        model="llama3.2",
        summary=(
            "Completed multi-agent review with 6 findings (3 actionable). "
            "Overall score: 83/100."
        ),
        verdict="comment",
        score=83,
        agent_results={
            "security": {"summary": "1 warning", "score": 78},
            "performance": {"summary": "N+1 pattern", "score": 82},
            "architecture": {"summary": "Interface suggestion", "score": 85},
        },
        started_at=datetime.now(UTC) - timedelta(hours=2),
        completed_at=datetime.now(UTC) - timedelta(hours=1, minutes=55),
    )
    session.add(review)
    await session.flush()

    comments = [
        ReviewComment(
            review_id=review.id,
            agent="security",
            file_path="backend/src/openreview/services/oauth/manager.py",
            line_start=42,
            line_end=48,
            severity=CommentSeverity.WARNING,
            title="Potential injection risk in user input handling",
            body="Validate and sanitize untrusted OAuth state parameters before persistence.",
            suggestion="state = validate_state(raw_state)",
        ),
        ReviewComment(
            review_id=review.id,
            agent="performance",
            file_path="backend/src/openreview/services/review/engine.py",
            line_start=88,
            line_end=102,
            severity=CommentSeverity.WARNING,
            title="N+1 query pattern detected",
            body="Batch agent result persistence instead of writing per comment.",
        ),
        ReviewComment(
            review_id=review.id,
            agent="architecture",
            file_path="backend/src/openreview/services/ai/base.py",
            line_start=1,
            line_end=20,
            severity=CommentSeverity.INFO,
            title="Consider extracting a shared interface",
            body="Provider and agent ports are well-separated; keep DI boundaries clear.",
        ),
    ]
    for c in comments:
        session.add(c)

    await session.commit()
