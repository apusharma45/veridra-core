from __future__ import annotations

import os

import httpx

from veridra.providers.base import ProviderError


class GroqProviderError(ProviderError):
    pass


def _base_url() -> str:
    return os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()


def _is_transient_status(status_code: int) -> bool:
    return status_code in {408, 429, 500, 502, 503, 504}


def _extract_text(payload: dict) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise GroqProviderError("Groq returned an empty or unsupported response shape")

    first = choices[0]
    if not isinstance(first, dict):
        raise GroqProviderError("Groq returned an empty or unsupported response shape")

    message = first.get("message")
    if not isinstance(message, dict):
        raise GroqProviderError("Groq returned an empty or unsupported response shape")

    content = message.get("content")
    if isinstance(content, str):
        content = content.strip()
        if content:
            return content

    raise GroqProviderError("Groq returned an empty response")


def generate(input_text: str, model: str, timeout_ms: int | None = None) -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise GroqProviderError("GROQ_API_KEY is missing")

    url = _base_url().rstrip("/") + "/chat/completions"
    timeout_seconds = (timeout_ms / 1000.0) if timeout_ms is not None else None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": input_text}],
        "stream": False,
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    except httpx.TimeoutException as exc:
        raise GroqProviderError(
            f"Groq request timed out: {exc}",
            timeout=True,
            transient=True,
        ) from exc
    except httpx.ConnectError as exc:
        raise GroqProviderError(
            f"Groq connection failed: {exc}",
            transient=True,
        ) from exc
    except httpx.HTTPError as exc:
        raise GroqProviderError(
            f"Groq request failed: {exc}",
            transient=True,
        ) from exc

    if response.status_code != 200:
        transient = _is_transient_status(response.status_code)
        raise GroqProviderError(
            f"Groq request failed with status {response.status_code}: {response.text}",
            transient=transient,
        )

    try:
        body = response.json()
    except ValueError as exc:
        raise GroqProviderError(f"Groq returned malformed JSON: {exc}") from exc

    if not isinstance(body, dict):
        raise GroqProviderError("Groq returned malformed JSON payload")

    return _extract_text(body)
