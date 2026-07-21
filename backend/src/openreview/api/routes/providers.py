"""AI provider endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from openreview.core.container import get_container
from openreview.core.security import encrypt_token
from openreview.db.session import get_db
from openreview.repositories import SettingsRepository, UserRepository
from openreview.schemas import ProviderInfo, ProviderUpdate, SettingsOut

router = APIRouter()


@router.get("", response_model=list[ProviderInfo])
async def list_providers() -> list[ProviderInfo]:
    container = get_container()
    return await container.ai_manager.list_providers()


@router.patch("", response_model=SettingsOut)
async def update_provider(
    body: ProviderUpdate,
    db: AsyncSession = Depends(get_db),
) -> SettingsOut:
    container = get_container()
    users = UserRepository(db)
    user = await users.get_primary()
    settings_repo = SettingsRepository(db)
    settings = await settings_repo.get_for_user(user.id) if user else None

    if body.openai_api_key:
        container.ai_manager.set_api_key("openai", body.openai_api_key)
    if body.anthropic_api_key:
        container.ai_manager.set_api_key("anthropic", body.anthropic_api_key)
    if body.openrouter_api_key:
        container.ai_manager.set_api_key("openrouter", body.openrouter_api_key)

    if body.provider:
        container.ai_manager.set_active(body.provider, body.model)
        if settings:
            settings.ai_provider = body.provider
            if body.model:
                settings.ai_model = body.model

    if settings:
        if body.openai_api_key:
            settings.openai_api_key_enc = encrypt_token(
                body.openai_api_key, container.settings
            )
        if body.anthropic_api_key:
            settings.anthropic_api_key_enc = encrypt_token(
                body.anthropic_api_key, container.settings
            )
        if body.openrouter_api_key:
            settings.openrouter_api_key_enc = encrypt_token(
                body.openrouter_api_key, container.settings
            )
        await db.flush()
        return SettingsOut(
            theme=settings.theme,
            ai_provider=settings.ai_provider,
            ai_model=settings.ai_model,
            review_strictness=settings.review_strictness,
            auto_review=settings.auto_review,
            ignored_files=settings.ignored_files,
            custom_rules=settings.custom_rules,
            repos_path=settings.repos_path,
            telemetry_enabled=settings.telemetry_enabled,
            has_openai_key=bool(settings.openai_api_key_enc),
            has_anthropic_key=bool(settings.anthropic_api_key_enc),
            has_openrouter_key=bool(settings.openrouter_api_key_enc),
        )

    return SettingsOut(
        theme="dark",
        ai_provider=body.provider or "ollama",
        ai_model=body.model or "llama3.2",
        review_strictness="balanced",
        auto_review=False,
        ignored_files=[],
        custom_rules=None,
        repos_path=None,
        telemetry_enabled=False,
    )
