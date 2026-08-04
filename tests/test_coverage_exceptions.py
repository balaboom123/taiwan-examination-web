import json
import tempfile
import unittest
from pathlib import Path

from app.coverage_exceptions import failure_exception_for, load_coverage_exceptions
from app.history_audit import build_history_coverage_audit, history_audit_exit_code
from app.models import NormalizedCatalog, ParsedPaper, SourceExamPage, SyncFailure
from app.paths import provider_paths, site_paths
from app.publisher import write_provider_state, write_site_state


def _exception(source_exam_id: str = "115030") -> dict:
    return {
        "scope": "event",
        "provider_id": "moex",
        "source_exam_id": source_exam_id,
        "year_ad": 2026,
        "status": "blocked",
        "reason_code": "official_no_result",
        "reason": "The official page returned no downloadable records.",
        "source_url": "https://example.test/event",
        "evidence": {
            "captured_at": "2026-07-29",
            "http_status": 200,
            "response_bytes": 10,
            "response_sha256": "0" * 64,
            "observation": "no result",
        },
    }


class CoverageExceptionTests(unittest.TestCase):
    def test_file_exception_requires_exact_current_download_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            path = root / "catalog" / "source-coverage" / "moex.json"
            path.parent.mkdir(parents=True)
            payload = {
                "schema_version": 1,
                "provider_id": "moex",
                "exceptions": [
                    {
                        **_exception("093170"),
                        "scope": "file",
                        "year_ad": 2004,
                        "paper_code": "104-5011-corrected_answer",
                        "file_type": "corrected_answer",
                        "source_url": "https://example.test/file",
                    }
                ],
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            exceptions = load_coverage_exceptions(root, "moex")

        failure = SyncFailure(
            stage="download",
            source_exam_id="093170",
            year_roc=93,
            paper_code="104-5011-corrected_answer",
            file_type="corrected_answer",
            url="https://example.test/file",
            message="placeholder",
        )
        self.assertIsNotNone(failure_exception_for("moex", failure, exceptions))
        changed_url = SyncFailure(**{**failure.__dict__, "url": "https://example.test/changed"})
        self.assertIsNone(failure_exception_for("moex", changed_url, exceptions))

    def test_audit_accepts_current_blocker_but_flags_conflict_and_orphan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            provider = provider_paths(root, "moex")
            raw_page = SourceExamPage(
                provider_id="moex",
                source_exam_id="115030",
                year_ad=2026,
                year_roc=115,
                exam_name_raw="MOEX 115030",
                attachments=[],
                papers=[],
            )
            write_provider_state(
                provider,
                raw_pages=[raw_page],
                normalized=NormalizedCatalog(papers=[], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )
            write_site_state(site_paths(root, "default"), [], [])
            exception_path = root / "catalog" / "source-coverage" / "moex.json"
            exception_path.parent.mkdir(parents=True)
            exception_path.write_text(
                json.dumps({"schema_version": 1, "provider_id": "moex", "exceptions": [_exception()]}),
                encoding="utf-8",
            )

            report = build_history_coverage_audit(root, provider_ids=["moex"])
            event = report["providers"][0]["events"][0]
            self.assertEqual(event["status"], "blocked")
            self.assertEqual(report["summary"]["blocked"], 1)
            self.assertEqual(history_audit_exit_code(report, strict=True), 0)

            raw_page.papers = [
                ParsedPaper(
                    category_raw="category",
                    category_code="101",
                    subject_code="0101",
                    subject_name_raw="subject",
                    files={"question": "https://example.test/question.pdf"},
                )
            ]
            write_provider_state(
                provider,
                raw_pages=[raw_page],
                normalized=NormalizedCatalog(papers=[], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )
            report = build_history_coverage_audit(root, provider_ids=["moex"])
            self.assertEqual(report["providers"][0]["events"][0]["status"], "coverage_exception_conflict")
            self.assertEqual(history_audit_exit_code(report, strict=True), 1)

            exception_path.write_text(
                json.dumps({"schema_version": 1, "provider_id": "moex", "exceptions": [_exception("missing")]}),
                encoding="utf-8",
            )
            report = build_history_coverage_audit(root, provider_ids=["moex"])
            self.assertEqual(report["summary"]["coverage_exception_orphan"], 1)
            self.assertEqual(history_audit_exit_code(report, strict=True), 1)


if __name__ == "__main__":
    unittest.main()
