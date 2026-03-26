from __future__ import annotations

from pydantic import BaseModel, field_validator, model_validator

from veridra.schemas.case import CaseSchema

KNOWN_PROVIDERS = {"openai", "ollama"}


class SuiteSchema(BaseModel):
    suite: str
    provider: str
    model: str
    cases: list[CaseSchema]

    @field_validator("suite", "provider", "model")
    @classmethod
    def _required_non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must be a non-empty string")
        return value

    @field_validator("provider")
    @classmethod
    def _provider_must_be_supported(cls, value: str) -> str:
        if value not in KNOWN_PROVIDERS:
            raise ValueError(f"unsupported provider: {value}")
        return value

    @field_validator("cases")
    @classmethod
    def _require_at_least_one_case(cls, value: list[CaseSchema]) -> list[CaseSchema]:
        if not value:
            raise ValueError("must include at least one case")
        return value

    @model_validator(mode="after")
    def _case_ids_must_be_unique(self) -> SuiteSchema:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for case in self.cases:
            if case.id in seen:
                duplicates.add(case.id)
            seen.add(case.id)
        if duplicates:
            raise ValueError(f"duplicate case id(s): {', '.join(sorted(duplicates))}")
        return self
