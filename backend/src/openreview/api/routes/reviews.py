"""Review lifecycle endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from openreview.core.container import get_container
from openreview.db.session import get_db
from openreview.models import CommentSeverity, Review, ReviewComment, ReviewStatus
from openreview.repositories import PullRequestRepository, ReviewRepository, SettingsRepository, UserRepository
from openreview.schemas import ReviewCommentOut, ReviewOut, ReviewStartRequest

router = APIRouter()


@router.post("/start", response_model=ReviewOut, status_code=201)
async def start_review(
    body: ReviewStartRequest,
    db: AsyncSession = Depends(get_db),
) -> ReviewOut:
    pr = await PullRequestRepository(db).get(body.pull_request_id)
    if pr is None:
        raise HTTPException(status_code=404, detail="Pull request not found")

    container = get_container()
    users = UserRepository(db)
    user = await users.get_primary()
    settings = None
    if user:
        settings = await SettingsRepository(db).get_for_user(user.id)

    provider = body.provider or (settings.ai_provider if settings else "ollama")
    model = body.model or (settings.ai_model if settings else "llama3.2")
    strictness = settings.review_strictness if settings else "balanced"
    custom_rules = settings.custom_rules if settings else None

    review = Review(
        pull_request_id=pr.id,
        status=ReviewStatus.RUNNING,
        provider=provider,
        model=model,
        started_at=datetime.now(UTC),
    )
    await ReviewRepository(db).add(review)
    await db.flush()

    # Use mock diffs shaped like FileDiff dicts
    from openreview.api.routes.pullrequests import MOCK_DIFFS

    files = [
        f.model_dump()
        for f in MOCK_DIFFS.get(
            pr.number,
            [],
        )
    ]
    if not files:
        files = [
            {
                "path": "src/app.py",
                "status": "modified",
                "additions": 10,
                "deletions": 2,
                "patch": "+ print('hello')",
                "language": "python",
            }
        ]

    try:
        result = await container.review_engine.run(
            title=pr.title,
            description=pr.body,
            files=files,
            repo_name=pr.source_branch,
            strictness=strictness,
            custom_rules=custom_rules,
            use_live_ai=False,  # Phase 1: mocked specialist agents
        )
        review.status = ReviewStatus.COMPLETED
        review.summary = result["summary"]
        review.verdict = result["verdict"]
        review.score = result["score"]
        review.agent_results = result["agent_results"]
        review.completed_at = datetime.now(UTC)

        for c in result["comments"]:
            comment = ReviewComment(
                review_id=review.id,
                agent=c["agent"],
                file_path=c.get("file_path"),
                line_start=c.get("line_start"),
                line_end=c.get("line_end"),
                severity=CommentSeverity(c.get("severity", "info")),
                title=c["title"],
                body=c["body"],
                suggestion=c.get("suggestion"),
            )
            db.add(comment)
    except Exception as exc:
        review.status = ReviewStatus.FAILED
        review.error_message = str(exc)
        review.completed_at = datetime.now(UTC)

    await db.flush()
    full = await ReviewRepository(db).get_with_comments(review.id)
    return ReviewOut.model_validate(full)


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(review_id: str, db: AsyncSession = Depends(get_db)) -> ReviewOut:
    review = await ReviewRepository(db).get_with_comments(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewOut.model_validate(review)


@router.get("/{review_id}/comments", response_model=list[ReviewCommentOut])
async def get_review_comments(
    review_id: str, db: AsyncSession = Depends(get_db)
) -> list[ReviewCommentOut]:
    review = await ReviewRepository(db).get_with_comments(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return [ReviewCommentOut.model_validate(c) for c in review.comments]
