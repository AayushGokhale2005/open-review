"""AI provider manager — resolves and configures providers."""

from __future__ import annotations

from openreview.core.config import Settings
from openreview.schemas import ProviderInfo
from openreview.services.ai.base import AIProvider
from openreview.services.ai.providers import (
    AnthropicProvider,
    LMStudioProvider,
    OllamaProvider,
    OpenAIProvider,
    OpenRouterProvider,
    VLLMProvider,
)


class AIProviderManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._api_keys: dict[str, str] = {}
        self._active_provider = settings.default_ai_provider
        self._active_model = "llama3.2"

    def set_api_key(self, provider_id: str, key: str) -> None:
        self._api_keys[provider_id] = key

    def set_active(self, provider_id: str, model: str | None = None) -> None:
        self._active_provider = provider_id
        if model:
            self._active_model = model

    def get_provider(self, provider_id: str | None = None, model: str | None = None) -> AIProvider:
        pid = provider_id or self._active_provider
        mid = model or self._active_model
        return self._build(pid, mid)

    def _build(self, provider_id: str, model: str) -> AIProvider:
        key = self._api_keys.get(provider_id)
        builders: dict[str, AIProvider] = {
            "ollama": OllamaProvider(base_url=self.settings.ollama_base_url, model=model),
            "lmstudio": LMStudioProvider(base_url=self.settings.lmstudio_base_url, model=model),
            "vllm": VLLMProvider(base_url=self.settings.vllm_base_url, model=model),
            "openai": OpenAIProvider(api_key=key or self._api_keys.get("openai"), model=model),
            "anthropic": AnthropicProvider(
                api_key=key or self._api_keys.get("anthropic"), model=model
            ),
            "openrouter": OpenRouterProvider(
                api_key=key or self._api_keys.get("openrouter"), model=model
            ),
        }
        if provider_id not in builders:
            raise ValueError(f"Unknown AI provider: {provider_id}")
        return builders[provider_id]

    async def list_providers(self) -> list[ProviderInfo]:
        catalog = [
            ("ollama", "Ollama", "Run open models locally for free", True, False),
            ("lmstudio", "LM Studio", "Local OpenAI-compatible server", True, False),
            ("vllm", "vLLM", "High-throughput local inference", True, False),
            ("openai", "OpenAI", "GPT-4o and frontier models", False, True),
            ("anthropic", "Anthropic", "Claude models", False, True),
            ("openrouter", "OpenRouter", "Multi-provider gateway", False, True),
        ]
        results: list[ProviderInfo] = []
        for pid, name, desc, local, needs_key in catalog:
            provider = self._build(pid, self._active_model)
            available = await provider.health_check()
            try:
                models = await provider.list_models()
            except Exception:
                models = []
            if not models:
                default_fn = getattr(provider, "_default_models", None)
                models = default_fn() if callable(default_fn) else []
            results.append(
                ProviderInfo(
                    id=pid,
                    name=name,
                    description=desc,
                    local=local,
                    requires_api_key=needs_key,
                    base_url=provider.base_url,
                    models=models,
                    available=available,
                    configured=bool(self._api_keys.get(pid)) if needs_key else True,
                )
            )
        return results
