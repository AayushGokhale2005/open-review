"""Specialist review agents — Phase 1 returns realistic mocked findings."""

from __future__ import annotations

from openreview.services.review.agents.base import AgentComment, AgentResult, ReviewAgent, ReviewContext


def _first_file(context: ReviewContext) -> str:
    if context.files:
        return context.files[0].get("path", "src/main.py")
    return "src/main.py"


class RepositoryIndexer(ReviewAgent):
    name = "indexer"
    description = "Indexes repository structure for contextual review"

    async def run(self, context: ReviewContext) -> AgentResult:
        context.index = {
            "file_count": len(context.files),
            "languages": list({f.get("language") for f in context.files if f.get("language")}),
            "paths": [f.get("path") for f in context.files],
        }
        return AgentResult(
            agent=self.name,
            summary=f"Indexed {len(context.files)} changed files.",
            score=100,
            metadata=context.index,
        )


class DiffExtractor(ReviewAgent):
    name = "diff_extractor"
    description = "Extracts and normalizes diffs for analysis"

    async def run(self, context: ReviewContext) -> AgentResult:
        additions = sum(f.get("additions", 0) for f in context.files)
        deletions = sum(f.get("deletions", 0) for f in context.files)
        context.diff = {"additions": additions, "deletions": deletions, "files": len(context.files)}
        return AgentResult(
            agent=self.name,
            summary=f"Extracted diff: +{additions} / -{deletions} across {len(context.files)} files.",
            score=100,
            metadata=context.diff,
        )


class ContextBuilder(ReviewAgent):
    name = "context_builder"
    description = "Builds surrounding code context for agents"

    async def run(self, context: ReviewContext) -> AgentResult:
        context.built_context = {
            "repo": context.repo_name,
            "title": context.title,
            "strictness": context.strictness,
            "focus_areas": ["security", "performance", "architecture", "style", "maintainability"],
        }
        return AgentResult(
            agent=self.name,
            summary="Built review context with focus areas.",
            score=100,
            metadata=context.built_context,
        )


class PlannerAgent(ReviewAgent):
    name = "planner"
    description = "Plans which checks to run based on the diff"

    async def run(self, context: ReviewContext) -> AgentResult:
        paths = [f.get("path", "") for f in context.files]
        plan = {
            "run_security": any(
                any(k in p.lower() for k in ("auth", "token", "password", "crypto", "secret"))
                for p in paths
            )
            or True,
            "run_performance": any(p.endswith((".py", ".ts", ".tsx", ".go", ".rs")) for p in paths),
            "run_architecture": len(context.files) >= 2,
            "run_style": True,
            "run_maintainability": True,
        }
        context.plan = plan
        return AgentResult(
            agent=self.name,
            summary="Planned specialist agent execution order.",
            score=100,
            metadata=plan,
        )


class SecurityAgent(ReviewAgent):
    name = "security"
    description = "Detects security vulnerabilities and risky patterns"

    async def run(self, context: ReviewContext) -> AgentResult:
        path = _first_file(context)
        comments = [
            AgentComment(
                file_path=path,
                line_start=42,
                line_end=48,
                severity="warning",
                title="Potential injection risk in user input handling",
                body=(
                    "User-controlled input appears to flow into a query or shell command without "
                    "sufficient sanitization. Prefer parameterized APIs and validate untrusted input."
                ),
                suggestion=(
                    "# Prefer parameterized queries\n"
                    "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
                ),
            ),
            AgentComment(
                file_path=path,
                line_start=12,
                line_end=15,
                severity="info",
                title="Secrets should not be hardcoded",
                body=(
                    "Ensure API keys and tokens are loaded from the environment or a secrets manager, "
                    "never committed to source control."
                ),
            ),
        ]
        return AgentResult(
            agent=self.name,
            summary="Found 1 warning and 1 informational security note.",
            score=78,
            comments=comments,
        )


class PerformanceAgent(ReviewAgent):
    name = "performance"
    description = "Identifies performance regressions and hotspots"

    async def run(self, context: ReviewContext) -> AgentResult:
        path = _first_file(context)
        comments = [
            AgentComment(
                file_path=path,
                line_start=88,
                line_end=102,
                severity="warning",
                title="N+1 query pattern detected",
                body=(
                    "This loop appears to issue a database or network call per item. "
                    "Consider batching or eager-loading related data to reduce latency."
                ),
                suggestion=(
                    "# Batch fetch instead of per-item queries\n"
                    "items = await repo.get_many(ids)\n"
                    "by_id = {i.id: i for i in items}"
                ),
            ),
        ]
        return AgentResult(
            agent=self.name,
            summary="Identified a potential N+1 query pattern.",
            score=82,
            comments=comments,
        )


class ArchitectureAgent(ReviewAgent):
    name = "architecture"
    description = "Reviews structural and design decisions"

    async def run(self, context: ReviewContext) -> AgentResult:
        path = context.files[1].get("path") if len(context.files) > 1 else _first_file(context)
        comments = [
            AgentComment(
                file_path=path,
                line_start=1,
                line_end=20,
                severity="info",
                title="Consider extracting a shared interface",
                body=(
                    "Multiple modules appear to duplicate similar orchestration logic. "
                    "A shared port/adapter or strategy interface would improve extensibility "
                    "for future agents and providers."
                ),
            ),
        ]
        return AgentResult(
            agent=self.name,
            summary="Suggested an interface extraction for better extensibility.",
            score=85,
            comments=comments,
        )


class StyleAgent(ReviewAgent):
    name = "style"
    description = "Checks style, naming, and consistency"

    async def run(self, context: ReviewContext) -> AgentResult:
        path = _first_file(context)
        comments = [
            AgentComment(
                file_path=path,
                line_start=5,
                line_end=5,
                severity="info",
                title="Naming inconsistency",
                body=(
                    "Identifier casing is inconsistent with the rest of the module. "
                    "Align with project conventions for readability."
                ),
            ),
        ]
        return AgentResult(
            agent=self.name,
            summary="Minor naming consistency note.",
            score=92,
            comments=comments,
        )


class MaintainabilityAgent(ReviewAgent):
    name = "maintainability"
    description = "Assesses complexity, duplication, and clarity"

    async def run(self, context: ReviewContext) -> AgentResult:
        path = _first_file(context)
        comments = [
            AgentComment(
                file_path=path,
                line_start=120,
                line_end=180,
                severity="warning",
                title="High cyclomatic complexity",
                body=(
                    "This function exceeds a comfortable complexity threshold. "
                    "Extract helper functions or use early returns to improve testability."
                ),
                suggestion=(
                    "def handle(event):\n"
                    "    if not event.valid:\n"
                    "        return reject(event)\n"
                    "    return process(event)"
                ),
            ),
        ]
        return AgentResult(
            agent=self.name,
            summary="Flagged a high-complexity function for refactoring.",
            score=80,
            comments=comments,
        )
