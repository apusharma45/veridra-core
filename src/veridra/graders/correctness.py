from __future__ import annotations

from veridra.schemas.case import CaseSchema


def grade_correctness(case: CaseSchema, output: str) -> dict[str, object]:
    details: list[str] = []
    passed = True

    normalized_output = output.strip()
    normalized_output_lower = normalized_output.lower()

    if case.expected_equals is not None:
        expected = case.expected_equals.strip()
        equals_ok = normalized_output == expected
        passed = passed and equals_ok
        details.append(
            f"expected_equals: {'passed' if equals_ok else 'failed'} (expected={expected!r})"
        )

    if case.expected_contains is not None:
        for expected_part in case.expected_contains:
            contains_ok = expected_part.lower() in normalized_output_lower
            passed = passed and contains_ok
            details.append(
                f"expected_contains[{expected_part!r}]: {'passed' if contains_ok else 'failed'}"
            )

    if case.forbidden_contains is not None:
        for forbidden_part in case.forbidden_contains:
            forbidden_ok = forbidden_part.lower() not in normalized_output_lower
            passed = passed and forbidden_ok
            details.append(
                f"forbidden_contains[{forbidden_part!r}]: {'passed' if forbidden_ok else 'failed'}"
            )

    return {"grader": "correctness", "pass": passed, "details": details}
