from __future__ import annotations

import os
from typing import Any


class OpenAIProviderError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        transient: bool = False,
        timeout: bool = False,
    ) -> None:
        super().__init__(message)
        self.transient = transient
        self.timeout = timeout


def _extract_text_from_response(response: Any) -> str:
    # Responses API style output
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    # Fallback: try nested output/content items defensively
    output = getattr(response, "output", None)
    if isinstance(output, list):
        chunks: list[str] = []
        for item in output:
            content = getattr(item, "content", None)
            if not isinstance(content, list):
                continue
            for part in content:
                text_value = getattr(part, "text", None)
                if isinstance(text_value, str):
                    chunks.append(text_value)
        joined = "".join(chunks).strip()
        if joined:
            return joined

    raise OpenAIProviderError("OpenAI returned an empty or unsupported response shape")


def _is_timeout_message(message: str) -> bool:
    lowered = message.lower()
    timeout_markers = ("timeout", "timed out", "time out")
    return any(marker in lowered for marker in timeout_markers)


def _is_transient_message(message: str) -> bool:
    lowered = message.lower()
    transient_markers = (
        "429",
        "500",
        "502",
        "503",
        "504",
        "rate limit",
        "connection",
        "temporarily unavailable",
        "service unavailable",
    )
    return any(marker in lowered for marker in transient_markers)


def generate(input_text: str, model: str, timeout_ms: int | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise OpenAIProviderError("OPENAI_API_KEY is missing")

    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover - dependency/import edge case
        raise OpenAIProviderError(f"OpenAI SDK import failed: {exc}") from exc

    try:
        client = OpenAI(api_key=api_key)
        timeout_seconds: float | None = None
        if timeout_ms is not None:
            timeout_seconds = timeout_ms / 1000.0
        response = client.responses.create(
            model=model,
            input=input_text,
            timeout=timeout_seconds,
        )
    except Exception as exc:
        message = str(exc)
        is_timeout = _is_timeout_message(message)
        is_transient = is_timeout or _is_transient_message(message)
        raise OpenAIProviderError(
            f"OpenAI request failed: {exc}",
            transient=is_transient,
            timeout=is_timeout,
        ) from exc

    return _extract_text_from_response(response)
