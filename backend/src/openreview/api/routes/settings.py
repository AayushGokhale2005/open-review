"""Application settings endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from openreview.core.container import get_container
from openreview.core.security import encrypt_token
from openreview.db.session import get_db
from openreview.models import AppSettings
from openreview.repositories import SettingsRepository, UserRepository
from openreview.schemas import SettingsOut, SettingsUpdate

router = APIRouter()


def _to_out(settings: AppSettings) -> SettingsOut:
    return SettingsOut(
        theme=settings.theme,
        ai_provider=settings.ai_provider,
        ai_model=settings.ai_model,
        review_strictness=settings.review_strictness,
        auto_review=settings.auto_review,
        ignored_files=settings.ignored_files or [],
        custom_rules=settings.custom_rules,
        repos_path=settings.repos_path,
        telemetry_enabled=settings.telemetry_enabled,
        has_openai_key=bool(settings.openai_api_key_enc),
        has_anthropic_key=bool(settings.anthropic_api_key_enc),
        has_openrouter_key=bool(settings.openrouter_api_key_enc),
    )


@router.get("", response_model=SettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)) -> SettingsOut:
    users = UserRepository(db)
    user = await users.get_primary()
    if user is None:
        raise HTTPException(status_code=404, detail="No user found")
    settings = await SettingsRepository(db).get_for_user(user.id)
    if settings is None:
        settings = AppSettings(user_id=user.id)
        await SettingsRepository(db).add(settings)
    return _to_out(settings)


@router.patch("", response_model=SettingsOut)
async def update_settings(
    body: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
) -> SettingsOut:
    container = get_container()
    users = UserRepository(db)
    user = await users.get_primary()
    if user is None:
        raise HTTPException(status_code=404, detail="No user found")

    settings_repo = SettingsRepository(db)
    settings = await settings_repo.get_for_user(user.id)
    if settings is None:
        settings = AppSettings(user_id=user.id)
        await settings_repo.add(settings)

    data = body.model_dump(exclude_unset=True)
    onboarding = data.pop("onboarding_completed", None)
    for key in (
        "openai_api_key",
        "anthropic_api_key",
        "openrouter_api_key",
    ):
        if key in data and data[key]:
            enc_attr = f"{key}_enc"
            setattr(settings, enc_attr, encrypt_token(data[key], container.settings))
            container.ai_manager.set_api_key(key.replace("_api_key", ""), data[key])
            del data[key]

    for k, v in data.items():
        if hasattr(settings, k):
            setattr(settings, k, v)

    if settings.ai_provider:
        container.ai_manager.set_active(settings.ai_provider, settings.ai_model)

    if onboarding is not None:
        user.onboarding_completed = onboarding

    await db.flush()
    return _to_out(settings)
