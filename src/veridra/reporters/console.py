from __future__ import annotations

from typing import Any

from rich import print
from rich.table import Table

from veridra.schemas.result import SuiteResultSchema


def print_regression_summary(regression: dict[str, object], verbose: bool = False) -> None:
    state = "FAILED" if regression.get("regression_failed") else "PASSED"
    state_color = "red" if regression.get("regression_failed") else "green"
    print(f"[bold]Regression:[/bold] [{state_color}]{state}[/{state_color}]")
    print(f"  baseline: {regression.get('baseline_file')}")
    if "fail_on_drift" in regression:
        print(f"  fail_on_drift: {regression.get('fail_on_drift')}")
    print(f"  compared: {regression.get('compared_count')}")
    print(f"  missing_in_current: {regression.get('missing_in_current_count')}")
    print(f"  new_in_current: {regression.get('new_in_current_count')}")
    print(f"  output_drift: {regression.get('output_drift_count')}")
    print(f"  pass_to_fail: {regression.get('pass_to_fail_count')}")
    if verbose:
        findings_obj = regression.get("findings", [])
        findings: list[dict[str, Any]]
        if isinstance(findings_obj, list):
            findings = [item for item in findings_obj if isinstance(item, dict)]
        else:
            findings = []
        if findings:
            print("  findings:")
            for finding in findings:
                print(
                    f"    - {finding.get('severity')} {finding.get('type')} "
                    f"{finding.get('case_id')}: {finding.get('message')}"
                )


def print_suite_report(result: SuiteResultSchema, verbose: bool = False) -> None:
    def _failure_reason(case: Any) -> str:
        if case.errors:
            return str(case.errors[0])
        for grader_result in case.grader_results:
            if grader_result.get("pass") is False:
                details = grader_result.get("details", [])
                if isinstance(details, list) and details:
                    return str(details[0])
                return f"{grader_result.get('grader', 'grader')} failed"
        return "case failed"

    print(f"[bold]Suite:[/bold] {result.suite}")
    print(f"[bold]Provider:[/bold] {result.provider}")
    print(f"[bold]Model:[/bold] {result.model}")
    print(f"[bold]Run mode:[/bold] {result.run_mode}")
    print(f"[bold]Fail fast:[/bold] {'on' if result.fail_fast else 'off'}")
    if result.stopped_early:
        print("[yellow]Execution stopped early due to --fail-fast.[/yellow]")
    print("")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Case")
    table.add_column("Status")
    table.add_column("Graders")
    table.add_column("Latency (ms)", justify="right")
    table.add_column("Retries", justify="right")
    table.add_column("Reason")

    for case in result.results:
        status = "[green]PASS[/green]" if case.pass_ else "[red]FAIL[/red]"
        grader_statuses = ", ".join(
            f"{item['grader']}={'pass' if item['pass'] else 'fail'}" for item in case.grader_results
        )
        reason = "" if case.pass_ else _failure_reason(case)
        table.add_row(
            case.id,
            status,
            grader_statuses or "-",
            str(case.latency_ms if case.latency_ms is not None else "-"),
            str(case.retry_count),
            reason,
        )

    print(table)
    for case in result.results:
        if not case.pass_:
            print(f"[red]✗ {case.id}[/red]")
            print(f"[red]Reason:[/red] {_failure_reason(case)}")
        if verbose:
            print(f"  latency_ms: {case.latency_ms}")
            print(f"  retry_count: {case.retry_count}")
            for grader_result in case.grader_results:
                details = grader_result.get("details", [])
                if details:
                    print(f"  {grader_result['grader']} details:")
                    for detail in details:
                        print(f"    - {detail}")
            if case.errors:
                print("  errors:")
                for error in case.errors:
                    print(f"    - {error}")

    total = result.passed + result.failed
    score = (result.passed / total * 100.0) if total else 0.0
    print("")
    print(f"[bold]Passed:[/bold] {result.passed}")
    print(f"[bold]Failed:[/bold] {result.failed}")
    print(f"[bold]Score:[/bold] {score:.1f}%")
    if result.regression:
        print("")
        print_regression_summary(result.regression, verbose=verbose)
