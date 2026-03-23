import veridra.engine.runner as runner_module
from veridra.engine.runner import run_suite
from veridra.schemas.case import CaseSchema
from veridra.schemas.suite import SuiteSchema


def _mock_openai_generate(input_text: str, model: str) -> str:
    return "Isaac Newton discovered gravity."


def test_runner_preserves_case_order_and_counts(monkeypatch) -> None:
    monkeypatch.setattr(runner_module, "generate_openai_response", _mock_openai_generate)

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

    result = run_suite(suite, run_mode="provider")

    assert [case.id for case in result.results] == ["fact-pass", "fact-fail"]
    assert result.passed == 1
    assert result.failed == 1


def test_runner_mock_mode_uses_mock_generator(monkeypatch) -> None:
    def _should_not_call_openai(input_text: str, model: str) -> str:
        raise RuntimeError("openai should not be called in mock mode")

    monkeypatch.setattr(runner_module, "generate_openai_response", _should_not_call_openai)

    suite = SuiteSchema(
        suite="mock-mode-check",
        provider="openai",
        model="gpt-4.1-mini",
        cases=[
            CaseSchema(
                id="fact-pass",
                input="Who discovered gravity?",
                graders=["correctness"],
                expected_contains=["newton"],
            ),
        ],
    )

    result = run_suite(suite, run_mode="mock")

    assert result.passed == 1
    assert result.failed == 0


def test_runner_fail_fast_stops_after_first_failure(monkeypatch) -> None:
    monkeypatch.setattr(runner_module, "generate_openai_response", _mock_openai_generate)

    suite = SuiteSchema(
        suite="fail-fast-check",
        provider="openai",
        model="gpt-4.1-mini",
        cases=[
            CaseSchema(
                id="first-fail",
                input="Who discovered gravity?",
                graders=["correctness"],
                expected_contains=["galileo"],
            ),
            CaseSchema(
                id="second-pass",
                input="Who discovered gravity?",
                graders=["correctness"],
                expected_contains=["newton"],
            ),
        ],
    )

    result = run_suite(suite, run_mode="provider", fail_fast=True)

    assert [case.id for case in result.results] == ["first-fail"]
    assert result.failed == 1
    assert result.stopped_early is True
