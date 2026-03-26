from __future__ import annotations

import json
from pathlib import Path

from veridra.schemas.result import SuiteResultSchema


def write_json_report(
    result: SuiteResultSchema,
    output_path: Path,
    include_debug: bool = False,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.model_dump(mode="json")
    if include_debug:
        for case_payload in payload.get("results", []):
            grader_details: dict[str, list[str]] = {}
            for grader_result in case_payload.get("grader_results", []):
                grader_name = str(grader_result.get("grader", "unknown"))
                details = grader_result.get("details", [])
                grader_details[grader_name] = list(details) if isinstance(details, list) else []

            case_payload["debug"] = {
                "latency_ms": case_payload.get("latency_ms"),
                "retry_count": case_payload.get("retry_count", 0),
                "grader_details": grader_details,
                "errors": list(case_payload.get("errors", [])),
            }

    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
