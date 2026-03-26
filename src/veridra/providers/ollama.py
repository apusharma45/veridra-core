from __future__ import annotations

import os

import httpx

from veridra.providers.base import ProviderError


class OllamaProviderError(ProviderError):
    pass


def _base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()


def _is_transient_status(status_code: int) -> bool:
    return status_code in {408, 429, 500, 502, 503, 504}


def generate(input_text: str, model: str, timeout_ms: int | None = None) -> str:
    url = _base_url().rstrip("/") + "/api/generate"
    timeout_seconds = (timeout_ms / 1000.0) if timeout_ms is not None else None

    try:
        response = httpx.post(
            url,
            json={"model": model, "prompt": input_text, "stream": False},
            timeout=timeout_seconds,
        )
    except httpx.TimeoutException as exc:
        raise OllamaProviderError(
            f"Ollama request timed out: {exc}",
            timeout=True,
            transient=True,
        ) from exc
    except httpx.ConnectError as exc:
        raise OllamaProviderError(
            f"Ollama connection failed: {exc}",
            transient=True,
        ) from exc
    except httpx.HTTPError as exc:
        raise OllamaProviderError(
            f"Ollama request failed: {exc}",
            transient=True,
        ) from exc

    if response.status_code != 200:
        transient = _is_transient_status(response.status_code)
        raise OllamaProviderError(
            f"Ollama request failed with status {response.status_code}: {response.text}",
            transient=transient,
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise OllamaProviderError(f"Ollama returned malformed JSON: {exc}") from exc

    output = payload.get("response")
    if isinstance(output, str):
        output = output.strip()
        if output:
            return output

    raise OllamaProviderError("Ollama returned an empty response")
