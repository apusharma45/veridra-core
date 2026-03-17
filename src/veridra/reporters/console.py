from __future__ import annotations

from rich import print

from veridra.schemas.result import SuiteResultSchema


def print_suite_report(result: SuiteResultSchema) -> None:
    print(f"[bold]Suite:[/bold] {result.suite}")
    print(f"[bold]Provider:[/bold] {result.provider}")
    print(f"[bold]Model:[/bold] {result.model}")
    print("")

    for case in result.results:
        marker = "[green]PASS[/green]" if case.pass_ else "[red]FAIL[/red]"
        grader_statuses = ", ".join(
            f"{item['grader']}={'pass' if item['pass'] else 'fail'}"
            for item in case.grader_results
        )
        print(f"{marker} {case.id}  {grader_statuses}")

    total = result.passed + result.failed
    score = (result.passed / total * 100.0) if total else 0.0
    print("")
    print(f"[bold]Passed:[/bold] {result.passed}")
    print(f"[bold]Failed:[/bold] {result.failed}")
    print(f"[bold]Score:[/bold] {score:.1f}%")
