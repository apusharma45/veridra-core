from __future__ import annotations

import os
from typing import Any


class OpenAIProviderError(RuntimeError):
    pass


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


def generate(input_text: str, model: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise OpenAIProviderError("OPENAI_API_KEY is missing")

    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover - dependency/import edge case
        raise OpenAIProviderError(f"OpenAI SDK import failed: {exc}") from exc

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(model=model, input=input_text)
    except Exception as exc:
        raise OpenAIProviderError(f"OpenAI request failed: {exc}") from exc

    return _extract_text_from_response(response)
