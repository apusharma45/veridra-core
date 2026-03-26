from types import SimpleNamespace

import pytest

from veridra.providers.ollama import OllamaProviderError, generate


def test_generate_returns_normalized_text(monkeypatch) -> None:
    def _fake_post(url: str, json: dict, timeout: float | None = None):
        return SimpleNamespace(
            status_code=200,
            json=lambda: {"response": "  Hello from Ollama  "},
            text="",
        )

    monkeypatch.setattr("veridra.providers.ollama.httpx.post", _fake_post)

    text = generate(input_text="hello", model="llama3.2")

    assert text == "Hello from Ollama"


def test_generate_maps_connection_error(monkeypatch) -> None:
    def _fake_post_connect(url: str, json: dict, timeout: float | None = None):
        import httpx

        raise httpx.ConnectError("cannot connect")

    monkeypatch.setattr("veridra.providers.ollama.httpx.post", _fake_post_connect)

    with pytest.raises(OllamaProviderError) as exc_info:
        generate(input_text="hello", model="llama3.2")

    assert exc_info.value.transient is True
    assert exc_info.value.timeout is False


def test_generate_maps_timeout_error(monkeypatch) -> None:
    def _fake_post_timeout(url: str, json: dict, timeout: float | None = None):
        import httpx

        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr("veridra.providers.ollama.httpx.post", _fake_post_timeout)

    with pytest.raises(OllamaProviderError) as exc_info:
        generate(input_text="hello", model="llama3.2", timeout_ms=25)

    assert exc_info.value.transient is True
    assert exc_info.value.timeout is True
