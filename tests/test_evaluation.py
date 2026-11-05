import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from src.defense.evaluation import (
    DEFAULT_CASES_PATH,
    evaluate_suite,
    format_report,
    load_suite,
    main,
)


class EvaluationTests(unittest.TestCase):
    def test_default_suite_reports_mode_and_blocking_metrics(self):
        report = evaluate_suite(load_suite(DEFAULT_CASES_PATH))

        self.assertEqual(report.total, 8)
        self.assertEqual(report.passed, 7)
        self.assertEqual(report.true_positive, 2)
        self.assertEqual(report.false_positive, 1)
        self.assertEqual(report.true_negative, 5)
        self.assertEqual(report.false_negative, 0)
        self.assertEqual(report.mode_accuracy, 7 / 8)

    def test_report_names_mismatches_without_exposing_message_text(self):
        report = evaluate_suite(load_suite(DEFAULT_CASES_PATH))
        output = format_report(report)
        serialized = report.to_dict()

        self.assertIn("False positives: benign_contextual_help_request", output)
        self.assertIn("False negatives: none", output)
        self.assertEqual(
            serialized["confusion_matrix"]["false_positive"], 1
        )
        self.assertNotIn("Please help me understand", str(serialized))

    def test_loader_rejects_non_string_expected_mode(self):
        invalid_suite = {
            "version": 1,
            "cases": [{"id": "invalid", "message": "Hello", "expected_mode": []}],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(invalid_suite), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "expected_mode"):
                load_suite(path)

    def test_cli_exports_json_and_can_fail_on_mismatches(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"
            with redirect_stdout(StringIO()):
                exit_code = main(["--json-output", str(output_path)])
                strict_exit_code = main(["--fail-on-mismatch"])

            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(strict_exit_code, 1)
            self.assertEqual(report["total"], 8)
            self.assertEqual(report["confusion_matrix"]["false_positive"], 1)


if __name__ == "__main__":
    unittest.main()