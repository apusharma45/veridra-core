from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator, model_validator

KNOWN_GRADERS = {"correctness", "safety"}
KNOWN_SAFETY_BEHAVIORS = {"refuse_or_safe", "answer_normally"}


class CaseSchema(BaseModel):
    id: str
    input: str
    graders: list[str]
    expected_contains: list[str] | None = None
    expected_equals: str | None = None
    forbidden_contains: list[str] | None = None
    expected_behavior: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("id", "input")
    @classmethod
    def _required_non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must be a non-empty string")
        return value

    @field_validator("graders")
    @classmethod
    def _validate_graders(cls, graders: list[str]) -> list[str]:
        if not graders:
            raise ValueError("must include at least one grader")
        unknown = [grader for grader in graders if grader not in KNOWN_GRADERS]
        if unknown:
            raise ValueError(f"unknown grader(s): {', '.join(unknown)}")
        return graders

    @field_validator("expected_contains", "forbidden_contains", "tags")
    @classmethod
    def _strip_list_strings(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        normalized = [item.strip() for item in value if item.strip()]
        if not normalized:
            raise ValueError("must contain at least one non-empty string")
        return normalized

    @field_validator("expected_equals", "expected_behavior")
    @classmethod
    def _strip_optional_string(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must be a non-empty string when provided")
        return cleaned

    @model_validator(mode="after")
    def _validate_field_compatibility(self) -> CaseSchema:
        uses_correctness = "correctness" in self.graders
        uses_safety = "safety" in self.graders

        has_correctness_expectation = any(
            [
                self.expected_equals is not None,
                self.expected_contains is not None,
                self.forbidden_contains is not None,
            ]
        )

        if uses_correctness and not has_correctness_expectation:
            raise ValueError(
                "correctness grader requires at least one of "
                "expected_equals, expected_contains, or forbidden_contains"
            )

        if not uses_correctness and has_correctness_expectation:
            raise ValueError(
                "expected_equals/expected_contains/forbidden_contains require "
                "the correctness grader"
            )

        if uses_safety:
            if self.expected_behavior is None:
                raise ValueError("safety grader requires expected_behavior")
            if self.expected_behavior not in KNOWN_SAFETY_BEHAVIORS:
                raise ValueError(
                    f"expected_behavior must be one of: {', '.join(sorted(KNOWN_SAFETY_BEHAVIORS))}"
                )
        elif self.expected_behavior is not None:
            raise ValueError("expected_behavior requires the safety grader")

        return self
