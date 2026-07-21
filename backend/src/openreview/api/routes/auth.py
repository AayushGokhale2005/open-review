"""Authentication endpoints — OAuth PKCE with localhost callback."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from openreview.core.container import get_container
from openreview.core.security import encrypt_token
from openreview.db.session import get_db
from openreview.models import GitProvider, OAuthAccount, User
from openreview.repositories import OAuthAccountRepository, UserRepository
from openreview.schemas import LoginRequest, LoginResponse, OAuthCallbackRequest, UserOut

router = APIRouter()

# In-memory session for local-first single-user mode
_current_user_id: str | None = None


def get_current_user_id() -> str | None:
    return _current_user_id


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    container = get_container()
    url, state, _verifier = container.oauth_manager.start_login(body.provider)
    return LoginResponse(authorization_url=url, state=state)


@router.post("/callback", response_model=UserOut)
async def oauth_callback(
    body: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    global _current_user_id
    container = get_container()
    try:
        result = await container.oauth_manager.exchange_code(
            body.provider, body.code, body.state, body.code_verifier
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"OAuth exchange failed: {exc}") from exc

    users = UserRepository(db)
    user = await users.get_primary()
    if user is None:
        user = User(
            display_name=result["user"]["display_name"],
            email=result["user"].get("email"),
            avatar_url=result["user"].get("avatar_url"),
        )
        await users.add(user)
    else:
        user.display_name = result["user"]["display_name"]
        user.email = result["user"].get("email") or user.email
        user.avatar_url = result["user"].get("avatar_url") or user.avatar_url

    oauth_repo = OAuthAccountRepository(db)
    account = OAuthAccount(
        user_id=user.id,
        provider=GitProvider(body.provider),
        provider_user_id=result["user"]["id"],
        username=result["user"]["username"],
        access_token_enc=encrypt_token(result["access_token"], container.settings),
        refresh_token_enc=(
            encrypt_token(result["refresh_token"], container.settings)
            if result.get("refresh_token")
            else None
        ),
        token_expires_at=result.get("expires_at"),
        scopes=str(result.get("scopes", "")),
    )
    await oauth_repo.add(account)
    _current_user_id = user.id

    refreshed = await users.get_with_accounts(user.id)
    return UserOut.model_validate(refreshed)


@router.get("/callback")
async def oauth_callback_get(code: str = "", state: str = "", error: str = "") -> HTMLResponse:
    """Browser redirect landing page — posts message back to the desktop app."""
    if error:
        body = f"<h1>Authentication failed</h1><p>{error}</p>"
    else:
        body = f"""
        <h1>Authentication successful</h1>
        <p>You can close this window and return to Open Review.</p>
        <script>
          window.opener && window.opener.postMessage({{
            type: 'openreview-oauth',
            code: {code!r},
            state: {state!r}
          }}, '*');
        </script>
        """
    return HTMLResponse(f"<html><body style='font-family:system-ui;padding:2rem'>{body}</body></html>")


@router.post("/logout")
async def logout() -> dict[str, str]:
    global _current_user_id
    _current_user_id = None
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
async def me(db: AsyncSession = Depends(get_db)) -> UserOut:
    users = UserRepository(db)
    user = await users.get_primary()
    if user is None:
        raise HTTPException(status_code=404, detail="No user found. Complete onboarding first.")
    return UserOut.model_validate(user)


@router.post("/demo-login", response_model=UserOut)
async def demo_login(db: AsyncSession = Depends(get_db)) -> UserOut:
    """Local demo login without real OAuth — useful for offline / first-run."""
    global _current_user_id
    users = UserRepository(db)
    user = await users.get_primary()
    if user is None:
        raise HTTPException(status_code=404, detail="Database not seeded")
    user.display_name = user.display_name or "Local Developer"
    _current_user_id = user.id
    return UserOut.model_validate(user)
