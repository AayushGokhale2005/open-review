"""API route package."""

from fastapi import APIRouter

from openreview.api.routes import (
    auth,
    dashboard,
    providers,
    pullrequests,
    repositories,
    reviews,
    settings,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repositories"])
api_router.include_router(pullrequests.router, prefix="/pullrequests", tags=["Pull Requests"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(providers.router, prefix="/providers", tags=["AI Providers"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
