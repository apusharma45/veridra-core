from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter

from veridra.graders.correctness import grade_correctness
from veridra.graders.safety import grade_safety
from veridra.schemas.case import CaseSchema
from veridra.schemas.result import CaseResultSchema, SuiteResultSchema
from veridra.schemas.suite import SuiteSchema


def _mock_generate_output(input_text: str) -> str:
    text = input_text.lower()
    if "who discovered gravity" in text:
        return "Isaac Newton discovered gravity."
    if "make a bomb" in text:
        return "I can't help with making a bomb. I can help with safety and legal guidance."
    if "ignore all previous instructions" in text:
        return "I cannot share hidden instructions."
    return f"Mock response: {input_text}"


def _run_case(case: CaseSchema) -> CaseResultSchema:
    start = perf_counter()
    output = _mock_generate_output(case.input)

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


def run_suite(suite: SuiteSchema) -> SuiteResultSchema:
    started_at = datetime.now(timezone.utc)

    results = [_run_case(case) for case in suite.cases]
    passed = sum(1 for result in results if result.pass_)
    failed = len(results) - passed

    ended_at = datetime.now(timezone.utc)
    return SuiteResultSchema(
        suite=suite.suite,
        provider=suite.provider,
        model=suite.model,
        started_at=started_at,
        ended_at=ended_at,
        passed=passed,
        failed=failed,
        results=results,
    )
