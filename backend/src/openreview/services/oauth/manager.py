"""OAuth PKCE manager for GitHub and GitLab."""

from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

from openreview.core.config import Settings
from openreview.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PKCEChallenge:
    state: str
    code_verifier: str
    code_challenge: str
    provider: str


class OAuthManager:
    """Browser-based OAuth with PKCE and localhost callback — no hosted auth server."""

    PROVIDERS = {
        "github": {
            "authorize_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "user_url": "https://api.github.com/user",
            "scopes": "read:user repo",
        },
        "gitlab": {
            "authorize_url": "https://gitlab.com/oauth/authorize",
            "token_url": "https://gitlab.com/oauth/token",
            "user_url": "https://gitlab.com/api/v4/user",
            "scopes": "read_user read_api read_repository",
        },
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._pending: dict[str, PKCEChallenge] = {}

    def _client_id(self, provider: str) -> str:
        if provider == "github":
            return self.settings.github_client_id
        return self.settings.gitlab_client_id

    def _client_secret(self, provider: str) -> str:
        if provider == "github":
            return self.settings.github_client_secret
        return self.settings.gitlab_client_secret

    @staticmethod
    def _create_pkce() -> tuple[str, str]:
        verifier = secrets.token_urlsafe(64)[:128]
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        return verifier, challenge

    def start_login(self, provider: str) -> tuple[str, str, str]:
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        verifier, challenge = self._create_pkce()
        state = secrets.token_urlsafe(32)
        cfg = self.PROVIDERS[provider]
        client_id = self._client_id(provider) or "local-dev-client"

        params = {
            "client_id": client_id,
            "redirect_uri": self.settings.oauth_redirect_uri,
            "response_type": "code",
            "scope": cfg["scopes"],
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        if provider == "github":
            # GitHub apps may not require PKCE params for classic OAuth apps
            pass

        url = f"{cfg['authorize_url']}?{urlencode(params)}"
        self._pending[state] = PKCEChallenge(
            state=state,
            code_verifier=verifier,
            code_challenge=challenge,
            provider=provider,
        )
        return url, state, verifier

    async def exchange_code(
        self,
        provider: str,
        code: str,
        state: str,
        code_verifier: str | None = None,
    ) -> dict[str, Any]:
        pending = self._pending.pop(state, None)
        verifier = code_verifier or (pending.code_verifier if pending else None)
        if not verifier:
            raise ValueError("Missing PKCE code_verifier")

        cfg = self.PROVIDERS[provider]
        data = {
            "client_id": self._client_id(provider) or "local-dev-client",
            "client_secret": self._client_secret(provider) or "",
            "code": code,
            "redirect_uri": self.settings.oauth_redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": verifier,
        }

        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(cfg["token_url"], data=data, headers=headers)
            resp.raise_for_status()
            token_data = resp.json()

        access_token = token_data["access_token"]
        user = await self.fetch_user(provider, access_token)
        expires_in = token_data.get("expires_in")
        expires_at = (
            datetime.now(UTC) + timedelta(seconds=int(expires_in)) if expires_in else None
        )

        return {
            "access_token": access_token,
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": expires_at,
            "scopes": token_data.get("scope", cfg["scopes"]),
            "user": user,
        }

    async def fetch_user(self, provider: str, access_token: str) -> dict[str, Any]:
        cfg = self.PROVIDERS[provider]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(cfg["user_url"], headers=headers)
            resp.raise_for_status()
            data = resp.json()

        if provider == "github":
            return {
                "id": str(data["id"]),
                "username": data["login"],
                "display_name": data.get("name") or data["login"],
                "email": data.get("email"),
                "avatar_url": data.get("avatar_url"),
            }
        return {
            "id": str(data["id"]),
            "username": data["username"],
            "display_name": data.get("name") or data["username"],
            "email": data.get("email"),
            "avatar_url": data.get("avatar_url"),
        }

    async def refresh_token(self, provider: str, refresh_token: str) -> dict[str, Any]:
        if provider == "github":
            # GitHub user-to-server tokens typically don't refresh the same way
            raise NotImplementedError("GitHub token refresh not supported for this flow")

        cfg = self.PROVIDERS[provider]
        data = {
            "client_id": self._client_id(provider),
            "client_secret": self._client_secret(provider),
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "redirect_uri": self.settings.oauth_redirect_uri,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(cfg["token_url"], data=data, headers={"Accept": "application/json"})
            resp.raise_for_status()
            return resp.json()
