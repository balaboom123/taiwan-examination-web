import json
import tempfile
import unittest
from pathlib import Path

from app.audit import audit_exit_code, build_catalog_audit
from app.models import NormalizedCatalog, NormalizedPaper, ReviewItem
from app.paths import provider_paths
from app.publisher import write_provider_state


def paper(category: str, event: str, year: int, source: str) -> NormalizedPaper:
    return NormalizedPaper(
        provider_id="moex",
        canonical_id="一般行政",
        canonical_name="一般行政",
        year_roc=year,
        exam_name_raw=event,
        category_raw=category,
        subject_name_raw="一般行政",
        paper_code=f"101-0101-{source}",
        file_type="question",
        download_url_source=f"https://source.example/{source}.pdf",
        category_code="101",
        source_exam_id=source,
        subject_code="0101",
        storage_key=f"115/{source}/101/0101/question.pdf",
    )


class CatalogAuditTests(unittest.TestCase):
    def test_audit_detects_review_queue_rows_not_present_in_current_papers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            current_paper = paper("一般行政", "公務人員高等考試三級", 115, "high-115")
            write_provider_state(
                provider_paths(root, "moex"),
                raw_pages=[],
                normalized=NormalizedCatalog(
                    papers=[current_paper],
                    review_queue=[
                        ReviewItem(
                            raw_category=current_paper.category_raw,
                            normalized_candidate=current_paper.canonical_name,
                            source_exam_id=current_paper.source_exam_id,
                            year_roc=current_paper.year_roc,
                            provider_id="moex",
                            reason="stale",
                        )
                    ],
                ),
                aliases=[],
                failures=[],
                manifest=None,
            )

            report = build_catalog_audit(root)

            self.assertEqual(report["review_queue_stale_entries"], 1)
            self.assertEqual(report["review_queue_missing_entries"], 0)
            self.assertEqual(audit_exit_code(report, strict=True), 1)

    def test_audit_scans_all_registered_provider_slots_and_reports_projected_split(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            write_provider_state(
                provider_paths(root, "moex"),
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[
                    paper("一般行政", "公務人員高等考試三級", 115, "high-115"),
                    paper("一般行政", "公務人員高等考試三級", 114, "high-114"),
                    paper("一般行政", "公務人員普通考試", 114, "ordinary-114"),
                ], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )

            report = build_catalog_audit(root)

            self.assertEqual(report["provider_count"], 35)
            self.assertEqual(report["paper_records_scanned"], 3)
            self.assertEqual(report["records_with_identity"], 3)
            self.assertTrue(report["all_records_covered"])
            self.assertEqual(report["records_needing_review"], 0)
            self.assertGreaterEqual(report["planned_bundle_count"], 1)
            self.assertGreaterEqual(report["planned_release_shards"], 1)
            self.assertIn("planned_release_asset_counts", report)
            self.assertIn("current_release_capacity_ok", report)

    def test_audit_report_is_json_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            report = build_catalog_audit(Path(tmp_dir))
            json.dumps(report, ensure_ascii=False)

    def test_release_plan_uses_v2_namespace_and_counts_aliases(self) -> None:
        from app.audit import build_release_plan
        from app.models import BundleAsset
        from app.paths import site_paths
        from app.publisher import write_site_state

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            bundle = BundleAsset(
                canonical_id="一般行政",
                canonical_name="一般行政",
                years=[115, 114],
                file_count=2,
                storage_key="bundles/sites/default/general.zip",
                asset_name="general.zip",
                release_tag="default-bundles-001",
                legacy_asset_names=["general-legacy.zip"],
            )
            write_site_state(
                site_paths(root, "default"),
                bundles=[bundle],
                frontend_bundles=[],
            )

            plan = build_release_plan(root)

            self.assertEqual(plan["schema_version"], 2)
            self.assertEqual(plan["shards"][0]["release_tag"], "default-bundles-v2-001")
            self.assertEqual(plan["shards"][0]["asset_count"], 2)
            self.assertEqual(plan["bundles"][0]["bundle_id"], "一般行政")


if __name__ == "__main__":
    unittest.main()
