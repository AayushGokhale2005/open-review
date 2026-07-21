"""Unit tests for AI provider abstraction."""

from openreview.services.ai.providers import OllamaProvider, OpenAIProvider


def test_provider_ids():
    assert OllamaProvider().id == "ollama"
    assert OllamaProvider().local is True
    assert OllamaProvider().requires_api_key is False
    assert OpenAIProvider().requires_api_key is True


def test_review_prompt_build():
    provider = OllamaProvider()
    from openreview.services.ai.base import ReviewRequest

    req = ReviewRequest(
        title="Add feature",
        description="Does things",
        files=[{"path": "x.py", "patch": "+ x = 1"}],
    )
    prompt = provider._build_review_prompt(req)
    assert "Add feature" in prompt
    assert "x.py" in prompt
