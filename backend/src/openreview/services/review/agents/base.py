"""Review agent base class — each specialist agent is replaceable."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentComment:
    file_path: str | None
    line_start: int | None
    line_end: int | None
    severity: str  # info | warning | error | critical
    title: str
    body: str
    suggestion: str | None = None


@dataclass
class AgentResult:
    agent: str
    summary: str
    score: int
    comments: list[AgentComment] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewContext:
    """Shared context passed through the review pipeline."""

    title: str
    description: str | None
    files: list[dict[str, Any]]
    repo_name: str = ""
    language: str | None = None
    strictness: str = "balanced"
    custom_rules: str | None = None
    index: dict[str, Any] = field(default_factory=dict)
    diff: dict[str, Any] = field(default_factory=dict)
    built_context: dict[str, Any] = field(default_factory=dict)
    plan: dict[str, Any] = field(default_factory=dict)


class ReviewAgent(ABC):
    """Base class for every specialist review agent."""

    name: str
    description: str

    @abstractmethod
    async def run(self, context: ReviewContext) -> AgentResult:
        """Execute the agent against the review context."""
