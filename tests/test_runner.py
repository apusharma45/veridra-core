from veridra.engine.runner import run_suite
from veridra.schemas.case import CaseSchema
from veridra.schemas.suite import SuiteSchema


def test_runner_preserves_case_order_and_counts() -> None:
    suite = SuiteSchema(
        suite="order-check",
        provider="openai",
        model="gpt-4.1-mini",
        cases=[
            CaseSchema(
                id="fact-pass",
                input="Who discovered gravity?",
                graders=["correctness"],
                expected_contains=["newton"],
            ),
            CaseSchema(
                id="fact-fail",
                input="Who discovered gravity?",
                graders=["correctness"],
                expected_contains=["galileo"],
            ),
        ],
    )

    result = run_suite(suite)

    assert [case.id for case in result.results] == ["fact-pass", "fact-fail"]
    assert result.passed == 1
    assert result.failed == 1
