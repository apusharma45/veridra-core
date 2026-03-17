from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CaseResultSchema(BaseModel):
    id: str
    input: str
    output: str
    pass_: bool
    grader_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    latency_ms: int | None = None


class SuiteResultSchema(BaseModel):
    suite: str
    provider: str
    model: str
    started_at: datetime
    ended_at: datetime
    passed: int
    failed: int
    results: list[CaseResultSchema]
