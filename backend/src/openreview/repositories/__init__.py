"""Data access layer — repository pattern."""

from __future__ import annotations

from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from openreview.models import (
    AppSettings,
    AuditLog,
    OAuthAccount,
    PullRequest,
    Repository,
    Review,
    ReviewComment,
    User,
)

T = TypeVar("T")


class BaseRepository[T]:
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def get(self, id: str) -> T | None:
        return await self.session.get(self.model, id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> list[T]:
        result = await self.session.execute(select(self.model).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_with_accounts(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts), selectinload(User.settings))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_primary(self) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts), selectinload(User.settings))
            .limit(1)
        )
        return result.scalar_one_or_none()


class OAuthAccountRepository(BaseRepository[OAuthAccount]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, OAuthAccount)


class RepositoryRepository(BaseRepository[Repository]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Repository)

    async def search(self, q: str | None = None, limit: int = 100) -> list[Repository]:
        stmt = select(Repository).order_by(Repository.updated_at.desc()).limit(limit)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                Repository.name.ilike(like) | Repository.full_name.ilike(like)
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class PullRequestRepository(BaseRepository[PullRequest]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PullRequest)

    async def list_by_repo(self, repository_id: str) -> list[PullRequest]:
        result = await self.session.execute(
            select(PullRequest)
            .where(PullRequest.repository_id == repository_id)
            .order_by(PullRequest.updated_at.desc())
        )
        return list(result.scalars().all())

    async def list_open(self, limit: int = 50) -> list[PullRequest]:
        result = await self.session.execute(
            select(PullRequest)
            .where(PullRequest.state == "open")
            .order_by(PullRequest.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Review)

    async def get_with_comments(self, review_id: str) -> Review | None:
        result = await self.session.execute(
            select(Review)
            .options(selectinload(Review.comments))
            .where(Review.id == review_id)
        )
        return result.scalar_one_or_none()

    async def recent(self, limit: int = 10) -> list[Review]:
        result = await self.session.execute(
            select(Review)
            .options(selectinload(Review.comments))
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class SettingsRepository(BaseRepository[AppSettings]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AppSettings)

    async def get_for_user(self, user_id: str) -> AppSettings | None:
        result = await self.session.execute(
            select(AppSettings).where(AppSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)
