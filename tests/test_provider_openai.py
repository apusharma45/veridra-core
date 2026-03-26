import sys
from types import SimpleNamespace

import pytest

from veridra.providers.openai import OpenAIProviderError, generate


class _FakeResponses:
    def __init__(self, response=None, error: Exception | None = None):
        self._response = response
        self._error = error

    def create(self, model: str, input: str, timeout: float | None = None):
        if self._error is not None:
            raise self._error
        return self._response


class _FakeClient:
    def __init__(self, response=None, error: Exception | None = None):
        self.responses = _FakeResponses(response=response, error=error)


def test_generate_raises_when_api_key_missing(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(OpenAIProviderError, match="OPENAI_API_KEY is missing"):
        generate(input_text="hello", model="gpt-4.1-mini")


def test_generate_returns_normalized_text(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    fake_response = SimpleNamespace(output_text="  Hello from OpenAI  ")

    def _fake_openai(api_key: str):
        assert api_key == "test-key"
        return _FakeClient(response=fake_response)

    fake_module = SimpleNamespace(OpenAI=_fake_openai)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    text = generate(input_text="hello", model="gpt-4.1-mini")

    assert text == "Hello from OpenAI"


def test_generate_maps_sdk_exception(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def _fake_openai(api_key: str):
        return _FakeClient(error=RuntimeError("boom"))

    fake_module = SimpleNamespace(OpenAI=_fake_openai)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    with pytest.raises(OpenAIProviderError, match="OpenAI request failed"):
        generate(input_text="hello", model="gpt-4.1-mini")


def test_generate_classifies_timeout_exception(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def _fake_openai(api_key: str):
        return _FakeClient(error=RuntimeError("request timed out"))

    fake_module = SimpleNamespace(OpenAI=_fake_openai)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    with pytest.raises(OpenAIProviderError) as exc_info:
        generate(input_text="hello", model="gpt-4.1-mini", timeout_ms=50)

    assert exc_info.value.timeout is True
    assert exc_info.value.transient is True
