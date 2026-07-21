"""Pull request endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from openreview.db.session import get_db
from openreview.repositories import PullRequestRepository, RepositoryRepository
from openreview.schemas import FileDiff, PullRequestDetail, PullRequestOut, RepositoryOut

router = APIRouter()

# Realistic mock diffs for demo PRs
MOCK_DIFFS: dict[int, list[FileDiff]] = {
    42: [
        FileDiff(
            path="backend/src/openreview/services/review/engine.py",
            status="added",
            additions=156,
            deletions=0,
            language="python",
            patch="""@@ -0,0 +1,40 @@
+class ReviewEngine:
+    def __init__(self, ai_manager, agents=None):
+        self.ai_manager = ai_manager
+        self.pipeline_agents = agents or default_agents()
+
+    async def run(self, *, title, files, **kwargs):
+        context = ReviewContext(title=title, files=files)
+        results = []
+        for agent in self.pipeline_agents:
+            results.append(await agent.run(context))
+        return self._merge(results)
""",
        ),
        FileDiff(
            path="backend/src/openreview/services/ai/base.py",
            status="modified",
            additions=48,
            deletions=12,
            language="python",
            patch="""@@ -10,6 +10,18 @@
 class AIProvider(ABC):
+    async def review_pull_request(self, request: ReviewRequest) -> ReviewResponse:
+        ...
+    async def explain_comment(self, comment: str, code_context: str) -> str:
+        ...
""",
        ),
        FileDiff(
            path="frontend/src/pages/ReviewPage.tsx",
            status="added",
            additions=220,
            deletions=0,
            language="typescript",
            patch="""@@ -0,0 +1,30 @@
+export function ReviewPage() {
+  return (
+    <div className="grid grid-cols-[1fr_360px]">
+      <DiffViewer />
+      <ConversationPanel />
+    </div>
+  );
+}
""",
        ),
    ],
    41: [
        FileDiff(
            path="backend/src/openreview/services/oauth/manager.py",
            status="modified",
            additions=34,
            deletions=8,
            language="python",
            patch="""@@ -80,10 +80,18 @@
-        self._pending[state] = challenge
+        self._pending[state] = challenge
+        # Clear expired PKCE challenges
+        self._gc_pending()
""",
        ),
    ],
}


@router.get("", response_model=list[PullRequestOut])
async def list_pull_requests(
    repository_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[PullRequestOut]:
    pr_repo = PullRequestRepository(db)
    if repository_id:
        prs = await pr_repo.list_by_repo(repository_id)
    else:
        prs = await pr_repo.list_open()
    return [PullRequestOut.model_validate(p) for p in prs]


@router.get("/{pr_id}", response_model=PullRequestDetail)
async def get_pull_request(pr_id: str, db: AsyncSession = Depends(get_db)) -> PullRequestDetail:
    pr = await PullRequestRepository(db).get(pr_id)
    if pr is None:
        raise HTTPException(status_code=404, detail="Pull request not found")

    repo = await RepositoryRepository(db).get(pr.repository_id)
    files = MOCK_DIFFS.get(pr.number, [
        FileDiff(
            path="README.md",
            status="modified",
            additions=5,
            deletions=1,
            language="markdown",
            patch="@@ -1,3 +1,7 @@\n+# Updated\n",
        )
    ])

    detail = PullRequestDetail.model_validate(pr)
    detail.files = files
    detail.repository = RepositoryOut.model_validate(repo) if repo else None
    return detail
