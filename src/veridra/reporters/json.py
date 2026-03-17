from __future__ import annotations

import json
from pathlib import Path

from veridra.schemas.result import SuiteResultSchema


def write_json_report(result: SuiteResultSchema, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.model_dump(mode="json")
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
