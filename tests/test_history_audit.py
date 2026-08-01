import tempfile
import unittest
from pathlib import Path

from app.history_audit import build_history_coverage_audit, history_audit_exit_code
from app.models import BundleAsset, ExamOption, NormalizedCatalog, NormalizedPaper, SourceExamPage
from app.paths import provider_paths, site_paths
from app.publisher import write_provider_state, write_site_state


class _ProbeClient:
    provider_id = "moex"

    def discover_available_years(self) -> list[int]:
        return [2026]

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        return [
            ExamOption(code="115030", year_ad=year_ad, year_roc=115, label="stored event"),
            ExamOption(code="115040", year_ad=year_ad, year_roc=115, label="source-only event"),
        ]


class HistoryAuditTests(unittest.TestCase):
    def test_audit_explicitly_disposes_single_year_publication_exclusion(self) -> None:
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
            paper = NormalizedPaper(
                provider_id="moex",
                canonical_id="nurse",
                canonical_name="Nurse",
                year_roc=115,
                exam_name_raw="MOEX 115030",
                category_raw="Nurse",
                subject_name_raw="Subject",
                paper_code="101-0101-question",
                file_type="question",
                download_url_source="https://example.test/question.pdf",
                category_code="101",
                source_exam_id="115030",
                subject_code="0101",
                storage_key="115/115030/101/0101/question.pdf",
            )
            write_provider_state(
                provider,
                raw_pages=[raw_page],
                normalized=NormalizedCatalog(papers=[paper], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )
            mirror_path = root / "mirror" / "providers" / "moex" / paper.storage_key
            mirror_path.parent.mkdir(parents=True, exist_ok=True)
            mirror_path.write_bytes(b"paper")
            write_site_state(site_paths(root, "default"), [], [])

            report = build_history_coverage_audit(root, provider_ids=["moex"])

        event = report["providers"][0]["events"][0]
        self.assertEqual(event["status"], "excluded_by_publication_policy")
        self.assertEqual(event["policy_eligible_bundle_ids"], [])
        self.assertEqual(event["policy_excluded_bundle_ids"], ["nurse"])
        self.assertEqual(report["summary"]["excluded_by_publication_policy"], 1)
        self.assertEqual(history_audit_exit_code(report, strict=True), 0)
        self.assertEqual(history_audit_exit_code({"summary": {"normalized_not_published": 1}}, strict=True), 1)
        self.assertEqual(history_audit_exit_code({"summary": {"sync_failure_recorded": 1}}, strict=True), 1)

    def test_audit_reports_missing_mirror_and_authoritative_source_only_event(self) -> None:
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
            paper = NormalizedPaper(
                provider_id="moex",
                canonical_id="nurse",
                canonical_name="Nurse",
                year_roc=115,
                exam_name_raw="MOEX 115030",
                category_raw="Nurse",
                subject_name_raw="Subject",
                paper_code="101-0101-question",
                file_type="question",
                download_url_source="https://example.test/question.pdf",
                category_code="101",
                source_exam_id="115030",
                subject_code="0101",
                storage_key="providers/moex/115/115030/101/0101/question.pdf",
            )
            write_provider_state(
                provider,
                raw_pages=[raw_page],
                normalized=NormalizedCatalog(papers=[paper], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )
            bundle = BundleAsset(
                canonical_id="nurse",
                canonical_name="Nurse",
                years=[115, 114],
                file_count=1,
                storage_key="bundles/sites/default/nurse.zip",
                asset_name="nurse.zip",
            )
            write_site_state(site_paths(root, "default"), [bundle], [])

            report = build_history_coverage_audit(
                root,
                provider_ids=["moex"],
                probe_sources=True,
                clients={"moex": _ProbeClient()},
            )

        provider_report = report["providers"][0]
        event = provider_report["events"][0]
        self.assertEqual(event["status"], "download_gap")
        self.assertEqual(event["published_bundle_ids"], ["nurse"])
        self.assertEqual(event["missing_mirror_files"], ["providers/moex/115/115030/101/0101/question.pdf"])
        self.assertEqual(provider_report["source_probe"]["status"], "ok")
        self.assertEqual(
            provider_report["source_probe"]["source_only_events"],
            [
                {
                    "source_exam_id": "115040",
                    "year_ad": 2026,
                    "year_roc": 115,
                    "label": "source-only event",
                }
            ],
        )
        self.assertEqual(report["summary"]["download_gap"], 1)
        self.assertEqual(report["summary"]["parser_gap"], 1)
        self.assertEqual(history_audit_exit_code(report, strict=True), 1)

    def test_audit_does_not_probe_sources_unless_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            report = build_history_coverage_audit(Path(tmp_dir), provider_ids=["moex"], probe_sources=False)

        self.assertEqual(report["providers"][0]["source_probe"]["status"], "not_requested")
        self.assertEqual(report["summary"]["parser_gap"], 0)


if __name__ == "__main__":
    unittest.main()
