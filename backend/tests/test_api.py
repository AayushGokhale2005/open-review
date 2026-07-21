"""Backend test suite."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

import openreview.db.session as db_session
from openreview.core.config import Settings, get_settings
from openreview.core.container import init_container
from openreview.db.seed import seed_if_empty
from openreview.main import create_app
from openreview.services.ai.manager import AIProviderManager
from openreview.services.review.agents import SecurityAgent
from openreview.services.review.agents.base import ReviewContext
from openreview.services.review.engine import ReviewEngine


@pytest.fixture
async def client(tmp_path, monkeypatch):
    settings = Settings(
        data_dir=tmp_path / "data",
        repos_dir=tmp_path / "repos",
        debug=True,
    )
    settings.ensure_dirs()
    get_settings.cache_clear()
    monkeypatch.setenv("OPENREVIEW_DATA_DIR", str(settings.data_dir))
    monkeypatch.setenv("OPENREVIEW_REPOS_DIR", str(settings.repos_dir))
    get_settings.cache_clear()

    # Point cached settings at our temp dirs
    monkeypatch.setattr("openreview.core.config.get_settings", lambda: settings)

    db_session.init_db(settings)
    init_container(settings)
    await db_session.create_tables()
    assert db_session.SessionLocal is not None
    async with db_session.SessionLocal() as session:
        await seed_if_empty(session)

    app = create_app()
    # Bypass lifespan re-init — already seeded
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_dashboard(client: AsyncClient):
    resp = await client.get("/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stats"]["repositories"] >= 1
    assert len(data["repositories"]) >= 1


@pytest.mark.asyncio
async def test_list_repositories(client: AsyncClient):
    resp = await client.get("/repositories")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_list_pull_requests(client: AsyncClient):
    resp = await client.get("/pullrequests")
    assert resp.status_code == 200
    prs = resp.json()
    assert len(prs) >= 1


@pytest.mark.asyncio
async def test_start_review(client: AsyncClient):
    prs = (await client.get("/pullrequests")).json()
    pr_id = prs[0]["id"]
    resp = await client.post("/reviews/start", json={"pull_request_id": pr_id})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "completed"
    assert data["score"] is not None
    assert len(data["comments"]) >= 1


@pytest.mark.asyncio
async def test_providers(client: AsyncClient):
    resp = await client.get("/providers")
    assert resp.status_code == 200
    providers = resp.json()
    ids = {p["id"] for p in providers}
    assert {"ollama", "openai", "anthropic", "openrouter", "lmstudio", "vllm"} <= ids


@pytest.mark.asyncio
async def test_settings(client: AsyncClient):
    resp = await client.get("/settings")
    assert resp.status_code == 200
    assert resp.json()["ai_provider"] == "ollama"

    patch = await client.patch(
        "/settings",
        json={"theme": "dark", "review_strictness": "strict", "telemetry_enabled": False},
    )
    assert patch.status_code == 200
    assert patch.json()["review_strictness"] == "strict"
    assert patch.json()["telemetry_enabled"] is False


@pytest.mark.asyncio
async def test_demo_login(client: AsyncClient):
    resp = await client.post("/auth/demo-login")
    assert resp.status_code == 200
    assert resp.json()["display_name"]


@pytest.mark.asyncio
async def test_security_agent_mocked():
    agent = SecurityAgent()
    ctx = ReviewContext(
        title="Test",
        description=None,
        files=[{"path": "auth.py", "language": "python"}],
    )
    result = await agent.run(ctx)
    assert result.agent == "security"
    assert len(result.comments) >= 1


@pytest.mark.asyncio
async def test_review_engine(tmp_path):
    settings = Settings(data_dir=tmp_path / "data", repos_dir=tmp_path / "repos")
    manager = AIProviderManager(settings)
    engine = ReviewEngine(manager)
    result = await engine.run(
        title="Test PR",
        description="desc",
        files=[{"path": "a.py", "additions": 10, "deletions": 1, "language": "python"}],
    )
    assert "summary" in result
    assert result["score"] > 0
    assert len(result["comments"]) >= 1
