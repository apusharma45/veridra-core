from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, Field, model_validator


class CaseResultSchema(BaseModel):
    id: str
    input: str
    output: str
    pass_: bool
    grader_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    latency_ms: int | None = None
    retry_count: int = 0


class SuiteResultSchema(BaseModel):
    SUPPORTED_SCHEMA_VERSIONS: ClassVar[set[str]] = {"1.0"}
    schema_version: str = "1.0"
    suite: str
    provider: str
    model: str
    run_mode: str = "provider"
    fail_fast: bool = False
    stopped_early: bool = False
    started_at: datetime
    ended_at: datetime
    passed: int
    failed: int
    results: list[CaseResultSchema]
    regression: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _validate_schema_version(self) -> "SuiteResultSchema":
        if self.schema_version not in self.SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(
                f"unsupported schema_version '{self.schema_version}'. "
                f"Supported versions: {', '.join(sorted(self.SUPPORTED_SCHEMA_VERSIONS))}"
            )
        return self
