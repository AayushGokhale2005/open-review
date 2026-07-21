"""Modular AI review pipeline engine."""

from __future__ import annotations

from typing import Any

from openreview.core.logging import get_logger
from openreview.services.ai.manager import AIProviderManager
from openreview.services.review.agents import (
    ArchitectureAgent,
    ContextBuilder,
    DiffExtractor,
    MaintainabilityAgent,
    PerformanceAgent,
    PlannerAgent,
    RepositoryIndexer,
    SecurityAgent,
    StyleAgent,
)
from openreview.services.review.agents.base import AgentResult, ReviewAgent, ReviewContext

logger = get_logger(__name__)


class ReviewEngine:
    """
    Orchestrates the review pipeline:

    Indexer → Diff → Context → Planner → Specialist Agents → Merge
    """

    def __init__(
        self,
        ai_manager: AIProviderManager,
        agents: list[ReviewAgent] | None = None,
    ) -> None:
        self.ai_manager = ai_manager
        self.pipeline_agents: list[ReviewAgent] = agents or [
            RepositoryIndexer(),
            DiffExtractor(),
            ContextBuilder(),
            PlannerAgent(),
            SecurityAgent(),
            PerformanceAgent(),
            ArchitectureAgent(),
            StyleAgent(),
            MaintainabilityAgent(),
        ]

    def replace_agent(self, name: str, agent: ReviewAgent) -> None:
        """Swap a single agent by name — enables future LangGraph/CrewAI backends."""
        for i, existing in enumerate(self.pipeline_agents):
            if existing.name == name:
                self.pipeline_agents[i] = agent
                return
        self.pipeline_agents.append(agent)

    async def run(
        self,
        *,
        title: str,
        description: str | None,
        files: list[dict[str, Any]],
        repo_name: str = "",
        language: str | None = None,
        strictness: str = "balanced",
        custom_rules: str | None = None,
        use_live_ai: bool = False,
    ) -> dict[str, Any]:
        context = ReviewContext(
            title=title,
            description=description,
            files=files,
            repo_name=repo_name,
            language=language,
            strictness=strictness,
            custom_rules=custom_rules,
        )

        agent_results: list[AgentResult] = []
        for agent in self.pipeline_agents:
            logger.info("review_agent_start", agent=agent.name)
            result = await agent.run(context)
            agent_results.append(result)
            logger.info("review_agent_done", agent=agent.name, score=result.score)

        merged = self._merge(agent_results)

        if use_live_ai:
            try:
                provider = self.ai_manager.get_provider()
                from openreview.services.ai.base import ReviewRequest

                live = await provider.review_pull_request(
                    ReviewRequest(
                        title=title,
                        description=description,
                        files=files,
                        strictness=strictness,
                        custom_rules=custom_rules,
                    )
                )
                merged["summary"] = live.summary or merged["summary"]
                merged["verdict"] = live.verdict or merged["verdict"]
                if live.score:
                    merged["score"] = live.score
            except Exception as exc:
                logger.warning("live_ai_review_failed", error=str(exc))

        return merged

    def _merge(self, results: list[AgentResult]) -> dict[str, Any]:
        specialist = [
            r
            for r in results
            if r.agent
            in {"security", "performance", "architecture", "style", "maintainability"}
        ]
        all_comments = []
        for r in specialist:
            for c in r.comments:
                all_comments.append(
                    {
                        "agent": r.agent,
                        "file_path": c.file_path,
                        "line_start": c.line_start,
                        "line_end": c.line_end,
                        "severity": c.severity,
                        "title": c.title,
                        "body": c.body,
                        "suggestion": c.suggestion,
                    }
                )

        avg_score = (
            int(sum(r.score for r in specialist) / len(specialist)) if specialist else 80
        )
        warnings = sum(1 for c in all_comments if c["severity"] in ("warning", "error", "critical"))
        verdict = "request_changes" if warnings >= 3 else "comment" if warnings else "approve"

        summary = (
            f"Completed multi-agent review with {len(all_comments)} findings "
            f"({warnings} actionable). Overall score: {avg_score}/100."
        )

        return {
            "summary": summary,
            "verdict": verdict,
            "score": avg_score,
            "comments": all_comments,
            "agent_results": {
                r.agent: {"summary": r.summary, "score": r.score, "metadata": r.metadata}
                for r in results
            },
        }
