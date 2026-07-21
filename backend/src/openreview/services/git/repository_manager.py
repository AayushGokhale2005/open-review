"""Local git repository management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

from openreview.core.config import Settings
from openreview.core.logging import get_logger

logger = get_logger(__name__)


class RepositoryManager:
    """Clone, pull, switch branches, and generate diffs under ~/AIReviewer/repos/."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.root = Path(settings.repos_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve_path(self, name: str) -> Path:
        safe = name.replace("/", "__")
        return self.root / safe

    def clone(self, clone_url: str, name: str, depth: int | None = 1) -> Path:
        target = self.resolve_path(name)
        if target.exists():
            logger.info("repo_already_cloned", path=str(target))
            return target
        kwargs: dict[str, Any] = {"url": clone_url, "to_path": str(target)}
        if depth:
            kwargs["depth"] = depth
        logger.info("cloning_repo", url=clone_url, path=str(target))
        Repo.clone_from(**kwargs)
        return target

    def import_local(self, path: str | Path) -> Path:
        src = Path(path).expanduser().resolve()
        if not src.exists():
            raise FileNotFoundError(f"Path does not exist: {src}")
        try:
            Repo(src)
        except InvalidGitRepositoryError as exc:
            raise ValueError(f"Not a git repository: {src}") from exc
        return src

    def pull(self, path: str | Path) -> None:
        repo = Repo(path)
        origin = repo.remotes.origin
        origin.pull()

    def checkout(self, path: str | Path, branch: str) -> None:
        repo = Repo(path)
        repo.git.checkout(branch)

    def commit_history(self, path: str | Path, limit: int = 50) -> list[dict[str, Any]]:
        repo = Repo(path)
        commits = []
        for c in repo.iter_commits(max_count=limit):
            commits.append(
                {
                    "sha": c.hexsha,
                    "message": c.message.strip(),
                    "author": str(c.author),
                    "date": c.committed_datetime.isoformat(),
                }
            )
        return commits

    def diff(
        self,
        path: str | Path,
        base: str = "main",
        head: str = "HEAD",
    ) -> list[dict[str, Any]]:
        repo = Repo(path)
        try:
            diffs = repo.commit(base).diff(head, create_patch=True)
        except GitCommandError:
            diffs = repo.head.commit.diff(None, create_patch=True)

        files: list[dict[str, Any]] = []
        for d in diffs:
            patch = d.diff.decode("utf-8", errors="replace") if d.diff else ""
            status = "modified"
            if d.new_file:
                status = "added"
            elif d.deleted_file:
                status = "deleted"
            elif d.renamed_file:
                status = "renamed"
            path_str = d.b_path or d.a_path or "unknown"
            files.append(
                {
                    "path": path_str,
                    "status": status,
                    "additions": patch.count("\n+") - patch.count("\n+++"),
                    "deletions": patch.count("\n-") - patch.count("\n---"),
                    "patch": patch,
                    "language": self._guess_language(path_str),
                }
            )
        return files

    def cleanup(self, name: str) -> None:
        import shutil

        target = self.resolve_path(name)
        if target.exists():
            shutil.rmtree(target)
            logger.info("repo_cleaned", path=str(target))

    @staticmethod
    def _guess_language(path: str) -> str | None:
        ext_map = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".md": "markdown",
            ".css": "css",
            ".html": "html",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
        }
        for ext, lang in ext_map.items():
            if path.endswith(ext):
                return lang
        return None
