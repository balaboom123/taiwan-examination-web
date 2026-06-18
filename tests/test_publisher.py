import json
import tempfile
import unittest
from pathlib import Path

from app.manifest import SourceManifest
from app.models import AliasRule, BundleAsset, NormalizedCatalog, NormalizedPaper, ReviewItem, SourceExamPage
from app.paths import legacy_paths, provider_paths, site_paths
from app.publisher import build_site, publish_site, write_data_files, write_provider_state, write_site_state


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
            lootlabs_manifest = {
                "schema_version": 1,
                "provider": "lootlabs",
                "site_id": "default",
                "links": [{"bundle_id": "nurse", "url": "https://lootlabs.gg/example"}],
            }

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
                lootlabs_manifest=lootlabs_manifest,
                legacy_paths=legacy,
                write_legacy=True,
            )

            self.assertTrue(provider.exams_dir.exists())
            self.assertTrue(site.bundles_path.exists())
            self.assertTrue(legacy.bundles_path.exists())
            self.assertTrue(provider.aliases_path.exists())
            self.assertTrue(site.release_assets_path.exists())
            self.assertEqual(
                json.loads(site.lootlabs_manifest_path.read_text(encoding="utf-8")),
                lootlabs_manifest,
            )
            self.assertEqual(
                json.loads(legacy.lootlabs_manifest_path.read_text(encoding="utf-8")),
                lootlabs_manifest,
            )

    def test_publish_site_aggregates_provider_catalogs_into_default_site(self) -> None:
        moex_paper = NormalizedPaper(
            provider_id="moex",
            canonical_id="nurse",
            canonical_name="Nurse",
            year_roc=115,
            exam_name_raw="115 Nurse Exam",
            category_raw="Nurse",
            subject_name_raw="Medical Basics",
            paper_code="101-0101-question",
            file_type="question",
            download_url_source="https://example.test/moex/nurse.pdf",
            category_code="101",
            source_exam_id="115030",
            subject_code="0101",
            storage_key="providers/moex/115/115030/101/0101/question.pdf",
        )
        ceec_paper = NormalizedPaper(
            provider_id="ceec_gsat",
            canonical_id="ceec-gsat",
            canonical_name="CEEC GSAT",
            year_roc=115,
            exam_name_raw="115 CEEC GSAT",
            category_raw="GSAT",
            subject_name_raw="General Subject",
            paper_code="101-0101-question",
            file_type="question",
            download_url_source="https://example.test/ceec_gsat/ceec-gsat.pdf",
            category_code="101",
            source_exam_id="gsat-115-guozong",
            subject_code="0101",
            storage_key="providers/ceec_gsat/115/gsat-115-guozong/101/0101/question.pdf",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            for paper in (moex_paper, ceec_paper):
                mirror_path = root / "mirror" / paper.storage_key
                mirror_path.parent.mkdir(parents=True, exist_ok=True)
                mirror_path.write_bytes(b"%PDF-1.7 demo")

            write_provider_state(
                provider_paths(root, "moex"),
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[moex_paper], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )
            write_provider_state(
                provider_paths(root, "ceec_gsat"),
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[ceec_paper], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )

            normalized, bundles = publish_site(root, site_id="default", repository="example/repo")

            self.assertEqual({paper.canonical_id for paper in normalized.papers}, {"nurse", "ceec-gsat"})
            self.assertEqual({bundle.canonical_id for bundle in bundles}, {"nurse", "ceec-gsat"})
            self.assertEqual(
                {bundle.storage_key for bundle in bundles},
                {
                    "bundles/sites/default/nurse.zip",
                    "bundles/sites/default/ceec-gsat.zip",
                },
            )
            self.assertTrue(site_paths(root, "default").bundles_path.exists())
            self.assertTrue(legacy_paths(root).bundles_path.exists())
            self.assertTrue((root / "site" / "index.html").exists())
            self.assertTrue((site_paths(root, "default").bundle_dir / "nurse.zip").exists())
            self.assertTrue((site_paths(root, "default").bundle_dir / "ceec-gsat.zip").exists())

            release_assets = json.loads(site_paths(root, "default").release_assets_path.read_text(encoding="utf-8"))
            self.assertEqual(
                {asset["storage_key"] for asset in release_assets["assets"]},
                {
                    "bundles/sites/default/nurse.zip",
                    "bundles/sites/default/ceec-gsat.zip",
                },
            )

    def test_publish_site_fails_closed_when_bundle_build_has_failures(self) -> None:
        broken_paper = NormalizedPaper(
            provider_id="moex",
            canonical_id="nurse",
            canonical_name="Nurse",
            year_roc=115,
            exam_name_raw="115 Nurse Exam",
            category_raw="Nurse",
            subject_name_raw="Medical Basics",
            paper_code="101-0101-question",
            file_type="question",
            download_url_source="https://example.test/moex/nurse.pdf",
            category_code="101",
            source_exam_id="115030",
            subject_code="0101",
            storage_key="providers/moex/115/115030/101/0101/question.pdf",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            write_provider_state(
                provider_paths(root, "moex"),
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[broken_paper], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )
            write_provider_state(
                provider_paths(root, "ceec_gsat"),
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )

            with self.assertRaises(ValueError):
                publish_site(root, site_id="default", repository="example/repo")

            self.assertFalse(site_paths(root, "default").bundles_path.exists())
            self.assertFalse(site_paths(root, "default").release_assets_path.exists())
            self.assertFalse(legacy_paths(root).bundles_path.exists())
            self.assertFalse((root / "site" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
