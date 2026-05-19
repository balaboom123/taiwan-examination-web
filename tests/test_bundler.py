import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from app.bundler import build_bundles
from app.models import BundleAsset, NormalizedCatalog, NormalizedPaper


class BundlerTests(unittest.TestCase):
    def test_build_bundles_groups_multiple_years_under_one_canonical_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            mirror_dir = root / "mirror"
            bundles_dir = root / "bundles"
            (mirror_dir / "115/115030/101/0101").mkdir(parents=True)
            (mirror_dir / "114/114170/101/0101").mkdir(parents=True)
            (mirror_dir / "115/115030/101/0101/question.pdf").write_bytes(b"%PDF-1.7 latest")
            (mirror_dir / "114/114170/101/0101/question.pdf").write_bytes(b"%PDF-1.7 prior")

            catalog = NormalizedCatalog(
                papers=[
                    NormalizedPaper(
                        canonical_id="nurse",
                        canonical_name="護理師",
                        year_roc=115,
                        exam_name_raw="115年護理師考試",
                        category_raw="高等考試_護理師",
                        category_code="101",
                        source_exam_id="115030",
                        subject_code="0101",
                        subject_name_raw="基礎醫學",
                        paper_code="101-0101-question",
                        file_type="question",
                        download_url_source="https://source.example/115-question.pdf",
                        download_url_mirror="",
                        download_url_bundle="",
                        storage_key="115/115030/101/0101/question.pdf",
                        checksum="abc123",
                    ),
                    NormalizedPaper(
                        canonical_id="nurse",
                        canonical_name="護理師",
                        year_roc=114,
                        exam_name_raw="114年護理師考試",
                        category_raw="專門職業及技術人員高等考試護理師考試",
                        category_code="101",
                        source_exam_id="114170",
                        subject_code="0101",
                        subject_name_raw="基礎醫學",
                        paper_code="101-0101-question",
                        file_type="question",
                        download_url_source="https://source.example/114-question.pdf",
                        download_url_mirror="",
                        download_url_bundle="",
                        storage_key="114/114170/101/0101/question.pdf",
                        checksum="def456",
                    ),
                ],
                review_queue=[],
            )

            result = build_bundles(
                bundle_dir=bundles_dir,
                mirror_dir=mirror_dir,
                normalized=catalog,
                bundle_base_url="https://github.com/example/repo/releases/download/moex-bundles",
            )
            bundles = result.bundles

            self.assertEqual(
                bundles,
                [
                    BundleAsset(
                        canonical_id="nurse",
                        canonical_name="護理師",
                        years=[115, 114],
                        file_count=2,
                        storage_key="bundles/nurse.zip",
                        asset_name="nurse.zip",
                        download_url="https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
                    )
                ],
            )

            bundle_zip = bundles_dir / "nurse.zip"
            self.assertTrue(bundle_zip.exists())
            with zipfile.ZipFile(bundle_zip) as archive:
                names = archive.namelist()
                self.assertIn("115/115030/高等考試_護理師/0101_基礎醫學/question.pdf", names)
                self.assertIn("114/114170/專門職業及技術人員高等考試護理師考試/0101_基礎醫學/question.pdf", names)
                manifest = json.loads(archive.read("bundle.json").decode("utf-8"))
                self.assertEqual(manifest["canonical_id"], "nurse")
                self.assertEqual(manifest["years"], [115, 114])

            self.assertTrue(all(paper.download_url_bundle.endswith("nurse.zip") for paper in catalog.papers))
            self.assertEqual(result.failures, [])

    def test_build_bundles_reuses_existing_bundle_entries_and_skips_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            mirror_dir = root / "mirror"
            bundles_dir = root / "bundles"
            bundles_dir.mkdir()
            existing_bundle = bundles_dir / "nurse.zip"
            with zipfile.ZipFile(existing_bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("114/114170/高等考試_護理師/0101_基礎醫學/question.pdf", b"%PDF-1.7 old")
                archive.writestr("bundle.json", json.dumps({"canonical_id": "nurse"}, ensure_ascii=False))

            (mirror_dir / "115/115030/101/0101").mkdir(parents=True)
            (mirror_dir / "115/115030/101/0101/question.pdf").write_bytes(b"%PDF-1.7 new")

            catalog = NormalizedCatalog(
                papers=[
                    NormalizedPaper(
                        canonical_id="nurse",
                        canonical_name="護理師",
                        year_roc=114,
                        exam_name_raw="114年護理師考試",
                        category_raw="高等考試_護理師",
                        category_code="101",
                        source_exam_id="114170",
                        subject_code="0101",
                        subject_name_raw="基礎醫學",
                        paper_code="101-0101-question",
                        file_type="question",
                        download_url_source="https://source.example/114-question.pdf",
                        storage_key="114/114170/101/0101/question.pdf",
                    ),
                    NormalizedPaper(
                        canonical_id="nurse",
                        canonical_name="護理師",
                        year_roc=115,
                        exam_name_raw="115年護理師考試",
                        category_raw="高等考試_護理師",
                        category_code="101",
                        source_exam_id="115030",
                        subject_code="0101",
                        subject_name_raw="基礎醫學",
                        paper_code="101-0101-question",
                        file_type="question",
                        download_url_source="https://source.example/115-question.pdf",
                        storage_key="115/115030/101/0101/question.pdf",
                    ),
                    NormalizedPaper(
                        canonical_id="nurse",
                        canonical_name="護理師",
                        year_roc=115,
                        exam_name_raw="115年護理師考試",
                        category_raw="高等考試_護理師",
                        category_code="101",
                        source_exam_id="115030",
                        subject_code="0102",
                        subject_name_raw="基本護理學",
                        paper_code="101-0102-question",
                        file_type="question",
                        download_url_source="https://source.example/115-missing-question.pdf",
                        storage_key="115/115030/101/0102/question.pdf",
                    ),
                ],
                review_queue=[],
            )

            result = build_bundles(
                bundle_dir=bundles_dir,
                mirror_dir=mirror_dir,
                normalized=catalog,
                bundle_base_url="https://bundles.example",
            )

            self.assertEqual(len(result.bundles), 1)
            with zipfile.ZipFile(bundles_dir / "nurse.zip") as archive:
                names = archive.namelist()
                self.assertIn("114/114170/高等考試_護理師/0101_基礎醫學/question.pdf", names)
                self.assertIn("115/115030/高等考試_護理師/0101_基礎醫學/question.pdf", names)
                self.assertNotIn("115/115030/高等考試_護理師/0102_基本護理學/question.pdf", names)
            self.assertEqual(len(result.failures), 1)
            self.assertEqual(result.failures[0]["paper_code"], "101-0102-question")


if __name__ == "__main__":
    unittest.main()
