"""FastAPI application entrypoint — embedded localhost backend."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from openreview import __version__
from openreview.api import api_router
from openreview.core.config import get_settings
from openreview.core.container import init_container
from openreview.core.logging import configure_logging, get_logger
from openreview.db.seed import seed_if_empty
from openreview.db.session import SessionLocal, create_tables, init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.debug)
    init_db(settings)
    init_container(settings)
    await create_tables()

    assert SessionLocal is not None
    async with SessionLocal() as session:
        await seed_if_empty(session)

    logger.info(
        "openreview_started",
        version=__version__,
        host=settings.host,
        port=settings.port,
        data_dir=str(settings.data_dir),
    )
    yield
    logger.info("openreview_stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Open Review API",
        description=(
            "Local-first AI code review API. Runs entirely on localhost — "
            "no hosted infrastructure required."
        ),
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:1420",
            "http://127.0.0.1:1420",
            "tauri://localhost",
            "https://tauri.localhost",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    return app


app = create_app()


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "openreview.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
