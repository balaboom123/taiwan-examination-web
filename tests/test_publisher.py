import json
import tempfile
import unittest
from pathlib import Path

from app.manifest import SourceManifest
from app.models import AliasRule, BundleAsset, NormalizedCatalog, NormalizedPaper, ReviewItem, SourceExamPage
from app.paths import legacy_paths, provider_paths, site_paths
from app.publisher import build_site, write_data_files, write_provider_state, write_site_state


class PublisherTests(unittest.TestCase):
    def test_write_data_files_and_site(self) -> None:
        normalized = NormalizedCatalog(
            papers=[
                NormalizedPaper(
                    provider_id="moex",
                    canonical_id="nurse",
                    canonical_name="Nurse",
                    year_roc=115,
                    exam_name_raw="115 Nurse Exam",
                    category_raw="Nurse",
                    category_code="101",
                    source_exam_id="115030",
                    subject_code="0101",
                    subject_name_raw="Medical Basics",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://wwwq.moex.gov.tw/example.pdf",
                    download_url_mirror="",
                    download_url_bundle="https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
                    storage_key="115/115030/101/0101/question.pdf",
                    checksum="abc123",
                )
            ],
            review_queue=[ReviewItem(raw_category="Nurse", normalized_candidate="Nurse", source_exam_id="115030", year_roc=115)],
        )
        raw_pages = [
            SourceExamPage(
                provider_id="moex",
                source_exam_id="115030",
                year_ad=2026,
                year_roc=115,
                exam_name_raw="115 Nurse Exam",
                attachments=[],
                papers=[],
            )
        ]
        aliases = [AliasRule(match_type="exact", raw_pattern="Nurse", canonical_id="nurse", canonical_name="Nurse")]
        bundles = [
            BundleAsset(
                canonical_id="nurse",
                canonical_name="Nurse",
                years=[115],
                file_count=1,
                storage_key="bundles/nurse.zip",
                asset_name="nurse.zip",
                release_tag="moex-bundles",
                download_url="https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
                legacy_asset_names=["nurse-legacy.zip"],
            )
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            write_data_files(root / "data", raw_pages, normalized, aliases, bundles, [])
            build_site(root / "site", normalized, bundles)

            papers = json.loads((root / "data" / "papers" / "2026.json").read_text(encoding="utf-8"))
            self.assertEqual(papers[0]["canonical_name"], "Nurse")
            self.assertEqual(papers[0]["provider_id"], "moex")
            self.assertFalse((root / "data" / "papers.json").exists())
            self.assertFalse((root / "data" / "exams.raw.json").exists())
            self.assertEqual(
                papers[0]["download_url_bundle"],
                "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
            )

            bundle_index = json.loads((root / "data" / "bundles.json").read_text(encoding="utf-8"))
            self.assertEqual(bundle_index[0]["canonical_id"], "nurse")

            release_assets = json.loads((root / "data" / "release-assets.json").read_text(encoding="utf-8"))
            self.assertEqual(
                release_assets,
                [
                    {
                        "storage_key": "bundles/nurse.zip",
                        "asset_name": "nurse.zip",
                        "checksum": "",
                        "legacy_asset_names": ["nurse-legacy.zip"],
                    },
                ],
            )

            review = json.loads((root / "data" / "review-queue.json").read_text(encoding="utf-8"))
            self.assertEqual(review[0]["normalized_candidate"], "Nurse")
            self.assertEqual(json.loads((root / "data" / "sync-failures.json").read_text(encoding="utf-8")), [])

            html = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Nurse", html)
            self.assertTrue((root / "site" / "data" / "bundles.json").exists())
            self.assertTrue((root / "site" / "data" / "papers" / "2026.json").exists())
            self.assertIn("${FILE_TYPE_LABELS[paper.file_type] || paper.file_type}", html)

    def test_write_provider_and_site_state_keep_legacy_compatibility_outputs(self) -> None:
        raw_pages = [
            SourceExamPage(
                provider_id="moex",
                source_exam_id="115030",
                year_ad=2026,
                year_roc=115,
                exam_name_raw="115 Nurse Exam",
                attachments=[],
                papers=[],
            )
        ]
        normalized = NormalizedCatalog(
            papers=[
                NormalizedPaper(
                    provider_id="moex",
                    canonical_id="nurse",
                    canonical_name="Nurse",
                    year_roc=115,
                    exam_name_raw="115 Nurse Exam",
                    category_raw="Nurse",
                    subject_name_raw="Medical Basics",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://wwwq.moex.gov.tw/example.pdf",
                    category_code="101",
                    source_exam_id="115030",
                    subject_code="0101",
                )
            ],
            review_queue=[ReviewItem(raw_category="Nurse", normalized_candidate="Nurse", source_exam_id="115030", year_roc=115)],
        )
        aliases = [AliasRule(match_type="exact", raw_pattern="Nurse", canonical_id="nurse", canonical_name="Nurse")]
        bundles = [
            BundleAsset(
                canonical_id="nurse",
                canonical_name="Nurse",
                years=[115],
                file_count=1,
                storage_key="bundles/sites/default/nurse.zip",
                asset_name="nurse.zip",
                release_tag="moex-bundles",
                download_url="https://example.test/nurse.zip",
            )
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            provider = provider_paths(root, "moex")
            site = site_paths(root, "default")
            legacy = legacy_paths(root)

            write_provider_state(
                provider,
                raw_pages=raw_pages,
                normalized=normalized,
                aliases=aliases,
                failures=[],
                manifest=SourceManifest(provider_id="moex"),
            )
            write_site_state(
                site,
                bundles=bundles,
                frontend_bundles=[{"id": "nurse", "name": "Nurse", "years": [115], "fileCount": 1, "url": bundles[0].download_url}],
                lootlabs_manifest=None,
                legacy_paths=legacy,
                write_legacy=True,
            )

            self.assertTrue(provider.exams_dir.exists())
            self.assertTrue(site.bundles_path.exists())
            self.assertTrue(legacy.bundles_path.exists())
            self.assertTrue(provider.aliases_path.exists())
            self.assertTrue(site.release_assets_path.exists())


if __name__ == "__main__":
    unittest.main()
