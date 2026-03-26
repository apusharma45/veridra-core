from __future__ import annotations

from pathlib import Path

from veridra.schemas.result import SuiteResultSchema


def compare_with_baseline(
    baseline: SuiteResultSchema,
    current: SuiteResultSchema,
    baseline_file: Path,
    fail_on_drift: bool = False,
) -> dict[str, object]:
    baseline_by_id = {case.id: case for case in baseline.results}
    current_by_id = {case.id: case for case in current.results}

    findings: list[dict[str, str]] = []
    pass_to_fail_count = 0
    output_drift_count = 0

    for case_id, baseline_case in baseline_by_id.items():
        current_case = current_by_id.get(case_id)
        if current_case is None:
            findings.append(
                {
                    "type": "missing_in_current",
                    "case_id": case_id,
                    "severity": "hard",
                    "message": "Case exists in baseline but is missing in current run.",
                }
            )
            continue

        if baseline_case.pass_ and not current_case.pass_:
            pass_to_fail_count += 1
            findings.append(
                {
                    "type": "pass_to_fail",
                    "case_id": case_id,
                    "severity": "hard",
                    "message": "Case regressed from pass to fail.",
                }
            )

        if (
            baseline_case.pass_
            and current_case.pass_
            and baseline_case.output != current_case.output
        ):
            output_drift_count += 1
            findings.append(
                {
                    "type": "output_drift",
                    "case_id": case_id,
                    "severity": "hard" if fail_on_drift else "soft",
                    "message": "Case output changed while still passing.",
                }
            )

    new_case_ids = sorted(set(current_by_id) - set(baseline_by_id))
    for case_id in new_case_ids:
        findings.append(
            {
                "type": "new_in_current",
                "case_id": case_id,
                "severity": "soft",
                "message": "Case exists in current run but not in baseline.",
            }
        )

    missing_case_ids = sorted(set(baseline_by_id) - set(current_by_id))
    regression_failed = bool(
        pass_to_fail_count > 0 or missing_case_ids or (fail_on_drift and output_drift_count > 0)
    )

    return {
        "baseline_file": str(baseline_file),
        "fail_on_drift": fail_on_drift,
        "regression_failed": regression_failed,
        "compared_count": len(set(baseline_by_id) & set(current_by_id)),
        "missing_in_current_count": len(missing_case_ids),
        "new_in_current_count": len(new_case_ids),
        "output_drift_count": output_drift_count,
        "pass_to_fail_count": pass_to_fail_count,
        "findings": findings,
    }
