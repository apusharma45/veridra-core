from __future__ import annotations

from rich import print

from veridra.schemas.result import SuiteResultSchema


def print_suite_report(result: SuiteResultSchema, verbose: bool = False) -> None:
    print(f"[bold]Suite:[/bold] {result.suite}")
    print(f"[bold]Provider:[/bold] {result.provider}")
    print(f"[bold]Model:[/bold] {result.model}")
    print(f"[bold]Run mode:[/bold] {result.run_mode}")
    print(f"[bold]Fail fast:[/bold] {'on' if result.fail_fast else 'off'}")
    if result.stopped_early:
        print("[yellow]Execution stopped early due to --fail-fast.[/yellow]")
    print("")

    for case in result.results:
        marker = "[green]PASS[/green]" if case.pass_ else "[red]FAIL[/red]"
        grader_statuses = ", ".join(
            f"{item['grader']}={'pass' if item['pass'] else 'fail'}"
            for item in case.grader_results
        )
        print(f"{marker} {case.id}  {grader_statuses}")
        if verbose:
            print(f"  latency_ms: {case.latency_ms}")
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
