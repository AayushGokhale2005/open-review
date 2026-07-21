"""AI provider abstraction — no provider-specific logic outside this package."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    role: str  # system | user | assistant
    content: str


@dataclass
class ReviewRequest:
    title: str
    description: str | None
    files: list[dict[str, Any]]
    context: dict[str, Any] = field(default_factory=dict)
    strictness: str = "balanced"
    custom_rules: str | None = None


@dataclass
class ReviewResponse:
    summary: str
    verdict: str
    score: int
    comments: list[dict[str, Any]]
    raw: dict[str, Any] | None = None


class AIProvider(ABC):
    """Common interface implemented by every AI backend."""

    id: str
    name: str
    local: bool
    requires_api_key: bool

    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str = "") -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable / configured."""

    @abstractmethod
    async def list_models(self) -> list[str]:
        """List available models."""

    @abstractmethod
    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.2) -> str:
        """Run a chat completion and return assistant text."""

    async def review_pull_request(self, request: ReviewRequest) -> ReviewResponse:
        """High-level PR review — default uses chat; providers may override."""
        prompt = self._build_review_prompt(request)
        text = await self.chat(
            [
                ChatMessage(role="system", content=self._system_prompt(request.strictness)),
                ChatMessage(role="user", content=prompt),
            ]
        )
        return ReviewResponse(
            summary=text[:2000] if text else "Review completed.",
            verdict="comment",
            score=75,
            comments=[],
            raw={"text": text},
        )

    async def explain_comment(self, comment: str, code_context: str) -> str:
        return await self.chat(
            [
                ChatMessage(
                    role="system",
                    content="You explain code review comments clearly and concisely.",
                ),
                ChatMessage(
                    role="user",
                    content=f"Comment:\n{comment}\n\nCode:\n{code_context}\n\nExplain:",
                ),
            ]
        )

    async def generate_fix(self, code: str, issue: str) -> str:
        return await self.chat(
            [
                ChatMessage(
                    role="system",
                    content="You generate minimal, correct code fixes. Return only the fixed code.",
                ),
                ChatMessage(role="user", content=f"Issue: {issue}\n\nCode:\n{code}"),
            ]
        )

    def _system_prompt(self, strictness: str) -> str:
        return (
            f"You are an expert code reviewer. Strictness: {strictness}. "
            "Focus on correctness, security, and maintainability."
        )

    def _build_review_prompt(self, request: ReviewRequest) -> str:
        files_blob = "\n\n".join(
            f"### {f.get('path')}\n```\n{f.get('patch', '')[:4000]}\n```" for f in request.files[:20]
        )
        rules = f"\nCustom rules:\n{request.custom_rules}" if request.custom_rules else ""
        return (
            f"Review this pull request.\n\n"
            f"Title: {request.title}\n"
            f"Description: {request.description or '(none)'}\n"
            f"{rules}\n\nChanged files:\n{files_blob}"
        )
