"""Concrete AI provider implementations."""

from __future__ import annotations

from typing import Any

import httpx

from openreview.core.logging import get_logger
from openreview.services.ai.base import AIProvider, ChatMessage

logger = get_logger(__name__)


class OpenAICompatibleProvider(AIProvider):
    """Shared implementation for OpenAI-compatible chat APIs."""

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = self._headers()
                url = f"{self.base_url.rstrip('/')}/models"
                resp = await client.get(url, headers=headers)
                return resp.status_code < 500
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url.rstrip('/')}/models",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception as exc:
            logger.warning("list_models_failed", provider=self.id, error=str(exc))
            return self._default_models()

    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.2) -> str:
        payload: dict[str, Any] = {
            "model": self.model or self._default_models()[0],
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _default_models(self) -> list[str]:
        return ["default"]


class OllamaProvider(OpenAICompatibleProvider):
    id = "ollama"
    name = "Ollama"
    local = True
    requires_api_key = False

    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "llama3.2") -> None:
        # Ollama native API; also expose OpenAI-compatible /v1
        super().__init__(base_url=f"{base_url.rstrip('/')}/v1", model=model)

    async def health_check(self) -> bool:
        try:
            root = self.base_url.replace("/v1", "")
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{root}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        try:
            root = self.base_url.replace("/v1", "")
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{root}/api/tags")
                resp.raise_for_status()
                return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return self._default_models()

    def _default_models(self) -> list[str]:
        return ["llama3.2", "codellama", "qwen2.5-coder", "deepseek-coder-v2"]


class LMStudioProvider(OpenAICompatibleProvider):
    id = "lmstudio"
    name = "LM Studio"
    local = True
    requires_api_key = False

    def __init__(
        self, base_url: str = "http://127.0.0.1:1234/v1", model: str = "local-model"
    ) -> None:
        super().__init__(base_url=base_url, model=model)

    def _default_models(self) -> list[str]:
        return ["local-model"]


class VLLMProvider(OpenAICompatibleProvider):
    id = "vllm"
    name = "vLLM"
    local = True
    requires_api_key = False

    def __init__(
        self, base_url: str = "http://127.0.0.1:8000/v1", model: str = "default"
    ) -> None:
        super().__init__(base_url=base_url, model=model)


class OpenAIProvider(OpenAICompatibleProvider):
    id = "openai"
    name = "OpenAI"
    local = False
    requires_api_key = True

    def __init__(
        self, api_key: str | None = None, model: str = "gpt-4o", base_url: str = "https://api.openai.com/v1"
    ) -> None:
        super().__init__(base_url=base_url, api_key=api_key, model=model)

    def _default_models(self) -> list[str]:
        return ["gpt-4o", "gpt-4o-mini", "o3-mini", "gpt-4.1"]


class AnthropicProvider(AIProvider):
    id = "anthropic"
    name = "Anthropic"
    local = False
    requires_api_key = True

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        base_url: str = "https://api.anthropic.com",
    ) -> None:
        super().__init__(base_url=base_url, api_key=api_key, model=model)

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def list_models(self) -> list[str]:
        return self._default_models()

    def _default_models(self) -> list[str]:
        return [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3-5-haiku-latest",
        ]

    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.2) -> str:
        if not self.api_key:
            raise RuntimeError("Anthropic API key not configured")

        system = next((m.content for m in messages if m.role == "system"), None)
        user_messages = [
            {"role": m.role, "content": m.content} for m in messages if m.role != "system"
        ]
        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": temperature,
            "messages": user_messages,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url.rstrip('/')}/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]


class OpenRouterProvider(OpenAICompatibleProvider):
    id = "openrouter"
    name = "OpenRouter"
    local = False
    requires_api_key = True

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "anthropic/claude-sonnet-4",
        base_url: str = "https://openrouter.ai/api/v1",
    ) -> None:
        super().__init__(base_url=base_url, api_key=api_key, model=model)

    def _default_models(self) -> list[str]:
        return [
            "anthropic/claude-sonnet-4",
            "openai/gpt-4o",
            "google/gemini-2.5-pro",
            "meta-llama/llama-4-maverick",
        ]

    def _headers(self) -> dict[str, str]:
        headers = super()._headers()
        headers["HTTP-Referer"] = "https://github.com/openreview/open-review"
        headers["X-Title"] = "Open Review"
        return headers
