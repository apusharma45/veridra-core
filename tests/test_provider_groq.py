from types import SimpleNamespace

import pytest

from veridra.providers.groq import GroqProviderError, generate


def test_generate_raises_when_api_key_missing(monkeypatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(GroqProviderError, match="GROQ_API_KEY is missing"):
        generate(input_text="hello", model="llama-3.1-8b-instant")


def test_generate_returns_normalized_text(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def _fake_post(url: str, headers: dict, json: dict, timeout: float | None = None):
        assert headers["Authorization"] == "Bearer test-key"
        return SimpleNamespace(
            status_code=200,
            json=lambda: {
                "choices": [{"message": {"content": "  Hello from Groq  "}}],
            },
            text="",
        )

    monkeypatch.setattr("veridra.providers.groq.httpx.post", _fake_post)

    text = generate(input_text="hello", model="llama-3.1-8b-instant")

    assert text == "Hello from Groq"


def test_generate_maps_connection_error(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def _fake_post_connect(url: str, headers: dict, json: dict, timeout: float | None = None):
        import httpx

        raise httpx.ConnectError("cannot connect")

    monkeypatch.setattr("veridra.providers.groq.httpx.post", _fake_post_connect)

    with pytest.raises(GroqProviderError) as exc_info:
        generate(input_text="hello", model="llama-3.1-8b-instant")

    assert exc_info.value.transient is True
    assert exc_info.value.timeout is False


def test_generate_maps_timeout_error(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def _fake_post_timeout(url: str, headers: dict, json: dict, timeout: float | None = None):
        import httpx

        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr("veridra.providers.groq.httpx.post", _fake_post_timeout)

    with pytest.raises(GroqProviderError) as exc_info:
        generate(input_text="hello", model="llama-3.1-8b-instant", timeout_ms=25)

    assert exc_info.value.transient is True
    assert exc_info.value.timeout is True
