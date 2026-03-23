from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Literal

from veridra.graders.correctness import grade_correctness
from veridra.graders.safety import grade_safety
from veridra.providers.mock import generate as generate_mock_response
from veridra.providers.openai import generate as generate_openai_response
from veridra.schemas.case import CaseSchema
from veridra.schemas.result import CaseResultSchema, SuiteResultSchema
from veridra.schemas.suite import SuiteSchema


RunMode = Literal["provider", "mock"]


def _generate_output(provider: str, input_text: str, model: str, run_mode: RunMode) -> str:
    if run_mode == "mock":
        return generate_mock_response(input_text=input_text)

    if provider == "openai":
        return generate_openai_response(input_text=input_text, model=model)
    raise RuntimeError(f"unsupported provider at runtime: {provider}")


def _run_case(case: CaseSchema, provider: str, model: str, run_mode: RunMode) -> CaseResultSchema:
    start = perf_counter()
    output = _generate_output(
        provider=provider,
        input_text=case.input,
        model=model,
        run_mode=run_mode,
    )

    grader_results: list[dict[str, object]] = []
    errors: list[str] = []

    for grader_name in case.graders:
        try:
            if grader_name == "correctness":
                grader_results.append(grade_correctness(case, output))
            elif grader_name == "safety":
                grader_results.append(grade_safety(case, output))
            else:
                errors.append(f"unknown grader at runtime: {grader_name}")
        except Exception as exc:  # pragma: no cover - defensive guard
            errors.append(f"{grader_name} grader crashed: {exc}")
            grader_results.append({"grader": grader_name, "pass": False, "details": []})

    pass_ = all(result.get("pass") is True for result in grader_results) and not errors
    latency_ms = int((perf_counter() - start) * 1000)

    return CaseResultSchema(
        id=case.id,
        input=case.input,
        output=output,
        pass_=pass_,
        grader_results=grader_results,
        errors=errors,
        latency_ms=latency_ms,
    )


def run_suite(
    suite: SuiteSchema,
    run_mode: RunMode = "provider",
    fail_fast: bool = False,
) -> SuiteResultSchema:
    started_at = datetime.now(timezone.utc)

    results: list[CaseResultSchema] = []
    stopped_early = False
    for case in suite.cases:
        case_result = _run_case(case, provider=suite.provider, model=suite.model, run_mode=run_mode)
        results.append(case_result)
        if fail_fast and not case_result.pass_:
            stopped_early = True
            break

    passed = sum(1 for result in results if result.pass_)
    failed = len(results) - passed

    ended_at = datetime.now(timezone.utc)
    return SuiteResultSchema(
        suite=suite.suite,
        provider=suite.provider,
        model=suite.model,
        run_mode=run_mode,
        fail_fast=fail_fast,
        stopped_early=stopped_early,
        started_at=started_at,
        ended_at=ended_at,
        passed=passed,
        failed=failed,
        results=results,
    )
