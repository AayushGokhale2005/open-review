"""Repository management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from openreview.core.container import get_container
from openreview.db.session import get_db
from openreview.models import GitProvider, Repository
from openreview.repositories import RepositoryRepository, UserRepository
from openreview.schemas import RepositoryCreate, RepositoryImportLocal, RepositoryOut

router = APIRouter()


@router.get("", response_model=list[RepositoryOut])
async def list_repositories(
    q: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[RepositoryOut]:
    repos = await RepositoryRepository(db).search(q=q)
    return [RepositoryOut.model_validate(r) for r in repos]


@router.post("", response_model=RepositoryOut, status_code=201)
async def create_repository(
    body: RepositoryCreate,
    db: AsyncSession = Depends(get_db),
) -> RepositoryOut:
    users = UserRepository(db)
    user = await users.get_primary()
    if user is None:
        raise HTTPException(status_code=400, detail="No user — complete onboarding first")

    container = get_container()
    local_path = body.local_path
    if body.clone_url and not local_path:
        try:
            path = container.repo_manager.clone(body.clone_url, body.full_name)
            local_path = str(path)
        except Exception as exc:
            # Non-fatal in demo mode — store metadata without clone
            local_path = None
            container  # noqa: B018 — keep reference
            _ = exc

    repo = Repository(
        user_id=user.id,
        provider=GitProvider(body.provider),
        name=body.name or body.full_name.split("/")[-1],
        full_name=body.full_name,
        description=body.description,
        language=body.language,
        stars=body.stars,
        default_branch=body.default_branch,
        clone_url=body.clone_url,
        local_path=local_path,
        html_url=body.html_url,
    )
    await RepositoryRepository(db).add(repo)
    return RepositoryOut.model_validate(repo)


@router.post("/import", response_model=RepositoryOut, status_code=201)
async def import_local(
    body: RepositoryImportLocal,
    db: AsyncSession = Depends(get_db),
) -> RepositoryOut:
    users = UserRepository(db)
    user = await users.get_primary()
    if user is None:
        raise HTTPException(status_code=400, detail="No user — complete onboarding first")

    container = get_container()
    try:
        path = container.repo_manager.import_local(body.path)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    name = body.name or path.name
    repo = Repository(
        user_id=user.id,
        provider=GitProvider.GITHUB,
        name=name,
        full_name=f"local/{name}",
        local_path=str(path),
        default_branch="main",
    )
    await RepositoryRepository(db).add(repo)
    return RepositoryOut.model_validate(repo)


@router.get("/{repo_id}", response_model=RepositoryOut)
async def get_repository(repo_id: str, db: AsyncSession = Depends(get_db)) -> RepositoryOut:
    repo = await RepositoryRepository(db).get(repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    return RepositoryOut.model_validate(repo)


@router.delete("/{repo_id}")
async def delete_repository(repo_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    repo_repo = RepositoryRepository(db)
    repo = await repo_repo.get(repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    await repo_repo.delete(repo)
    return {"status": "deleted"}
