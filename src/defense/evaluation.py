import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from src.sandbox import Sandbox


VALID_MODES = frozenset({"weak", "normal", "strict"})
DEFAULT_CASES_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "evaluation_cases.json"
)


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    message: str
    expected_mode: str


@dataclass(frozen=True)
class EvaluationSuite:
    version: int
    cases: tuple[EvaluationCase, ...]


@dataclass(frozen=True)
class ScenarioResult:
    case_id: str
    expected_mode: str
    actual_mode: str
    risk_score: int
    expected_blocked: bool
    actual_blocked: bool
    signals: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.expected_mode == self.actual_mode


@dataclass(frozen=True)
class EvaluationReport:
    suite_version: int
    scenarios: tuple[ScenarioResult, ...]
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    mode_accuracy: float

    @property
    def total(self) -> int:
        return len(self.scenarios)

    @property
    def passed(self) -> int:
        return sum(result.passed for result in self.scenarios)

    @property
    def accuracy(self) -> float:
        return _ratio(self.true_positive + self.true_negative, self.total)

    @property
    def precision(self) -> float:
        return _ratio(self.true_positive, self.true_positive + self.false_positive)

    @property
    def recall(self) -> float:
        return _ratio(self.true_positive, self.true_positive + self.false_negative)

    @property
    def specificity(self) -> float:
        return _ratio(self.true_negative, self.true_negative + self.false_positive)

    def to_dict(self) -> dict:
        return {
            "suite_version": self.suite_version,
            "total": self.total,
            "passed": self.passed,
            "mode_accuracy": self.mode_accuracy,
            "blocking_metrics": {
                "accuracy": self.accuracy,
                "precision": self.precision,
                "recall": self.recall,
                "specificity": self.specificity,
            },
            "confusion_matrix": {
                "true_positive": self.true_positive,
                "false_positive": self.false_positive,
                "true_negative": self.true_negative,
                "false_negative": self.false_negative,
            },
            "scenarios": [
                {
                    "id": result.case_id,
                    "expected_mode": result.expected_mode,
                    "actual_mode": result.actual_mode,
                    "risk_score": result.risk_score,
                    "expected_blocked": result.expected_blocked,
                    "actual_blocked": result.actual_blocked,
                    "signals": list(result.signals),
                    "passed": result.passed,
                }
                for result in self.scenarios
            ],
        }


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def load_suite(path: Path = DEFAULT_CASES_PATH) -> EvaluationSuite:
    """Load and validate a versioned evaluation suite from JSON."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Evaluation suite must be a JSON object.")

    version = data.get("version")
    raw_cases = data.get("cases")
    if type(version) is not int or version < 1:
        raise ValueError("Evaluation suite version must be a positive integer.")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("Evaluation suite must contain a non-empty cases list.")

    cases = []
    seen_ids = set()
    for index, raw_case in enumerate(raw_cases):
        if not isinstance(raw_case, dict):
            raise ValueError(f"Case {index + 1} must be a JSON object.")

        case_id = raw_case.get("id")
        message = raw_case.get("message")
        expected_mode = raw_case.get("expected_mode")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"Case {index + 1} must have a non-empty id.")
        case_id = case_id.strip()
        if case_id in seen_ids:
            raise ValueError(f"Duplicate evaluation case id: {case_id}")
        if not isinstance(message, str) or not message.strip():
            raise ValueError(f"Case {case_id} must have a non-empty message.")
        if not isinstance(expected_mode, str) or expected_mode not in VALID_MODES:
            raise ValueError(
                f"Case {case_id} expected_mode must be one of: "
                f"{', '.join(sorted(VALID_MODES))}."
            )

        cases.append(EvaluationCase(case_id, message, expected_mode))
        seen_ids.add(case_id)

    return EvaluationSuite(version, tuple(cases))


def evaluate_suite(suite: EvaluationSuite) -> EvaluationReport:
    """Evaluate each case in a fresh local sandbox session."""
    results = []
    true_positive = false_positive = true_negative = false_negative = 0

    for case in suite.cases:
        record = Sandbox().run_detailed(case.message)
        expected_blocked = case.expected_mode == "strict"
        actual_blocked = record.blocked

        if expected_blocked and actual_blocked:
            true_positive += 1
        elif not expected_blocked and actual_blocked:
            false_positive += 1
        elif not expected_blocked and not actual_blocked:
            true_negative += 1
        else:
            false_negative += 1

        results.append(
            ScenarioResult(
                case_id=case.case_id,
                expected_mode=case.expected_mode,
                actual_mode=record.mode,
                risk_score=record.risk_score,
                expected_blocked=expected_blocked,
                actual_blocked=actual_blocked,
                signals=record.signals,
            )
        )

    mode_accuracy = _ratio(
        sum(result.passed for result in results), len(results)
    )
    return EvaluationReport(
        suite_version=suite.version,
        scenarios=tuple(results),
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
        mode_accuracy=mode_accuracy,
    )


def format_report(report: EvaluationReport) -> str:
    lines = [
        f"Evaluation suite v{report.suite_version}: {report.passed}/{report.total} mode checks passed",
        f"Mode accuracy: {report.mode_accuracy:.1%}",
        (
            "Blocking: "
            f"accuracy {report.accuracy:.1%}, "
            f"precision {report.precision:.1%}, "
            f"recall {report.recall:.1%}, "
            f"specificity {report.specificity:.1%}"
        ),
        (
            "Confusion matrix: "
            f"TP={report.true_positive} FP={report.false_positive} "
            f"TN={report.true_negative} FN={report.false_negative}"
        ),
        "Scenarios:",
    ]

    for result in report.scenarios:
        status = "PASS" if result.passed else "FAIL"
        lines.append(
            f"  {status} {result.case_id}: expected={result.expected_mode} "
            f"actual={result.actual_mode} risk={result.risk_score}"
        )

    false_positives = [
        result.case_id for result in report.scenarios
        if not result.expected_blocked and result.actual_blocked
    ]
    false_negatives = [
        result.case_id for result in report.scenarios
        if result.expected_blocked and not result.actual_blocked
    ]
    lines.append("False positives: " + (", ".join(false_positives) or "none"))
    lines.append("False negatives: " + (", ".join(false_negatives) or "none"))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the local sandbox heuristics.")
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to a versioned evaluation suite in JSON format.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Write the detailed report to this JSON file.",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit with status 1 when any scenario has an unexpected mode.",
    )
    args = parser.parse_args(argv)

    try:
        report = evaluate_suite(load_suite(args.cases))
        print(format_report(report))
        if args.json_output:
            args.json_output.write_text(
                json.dumps(report.to_dict(), indent=2) + "\n",
                encoding="utf-8",
            )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    if args.fail_on_mismatch and report.passed != report.total:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())