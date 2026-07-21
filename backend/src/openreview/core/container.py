"""Dependency injection container."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openreview.core.config import Settings
    from openreview.services.ai.manager import AIProviderManager
    from openreview.services.git.repository_manager import RepositoryManager
    from openreview.services.oauth.manager import OAuthManager
    from openreview.services.review.engine import ReviewEngine


@dataclass
class Container:
    """Application service container for dependency injection."""

    settings: Settings
    ai_manager: AIProviderManager | None = None
    repo_manager: RepositoryManager | None = None
    oauth_manager: OAuthManager | None = None
    review_engine: ReviewEngine | None = None
    _initialized: bool = field(default=False, repr=False)

    def initialize(self) -> None:
        from openreview.services.ai.manager import AIProviderManager
        from openreview.services.git.repository_manager import RepositoryManager
        from openreview.services.oauth.manager import OAuthManager
        from openreview.services.review.engine import ReviewEngine

        self.ai_manager = AIProviderManager(self.settings)
        self.repo_manager = RepositoryManager(self.settings)
        self.oauth_manager = OAuthManager(self.settings)
        self.review_engine = ReviewEngine(self.ai_manager)
        self._initialized = True


_container: Container | None = None


def get_container() -> Container:
    if _container is None or not _container._initialized:
        raise RuntimeError("Container not initialized. Call init_container() first.")
    return _container


def init_container(settings: Settings) -> Container:
    global _container
    _container = Container(settings=settings)
    _container.initialize()
    return _container
