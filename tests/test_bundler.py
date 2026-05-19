import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from app.bundler import build_bundles
from app.models import BundleAsset, NormalizedCatalog, NormalizedPaper


def make_paper(
    *,
    canonical_id: str,
    canonical_name: str,
    year_roc: int,
    source_exam_id: str,
    subject_code: str,
    file_type: str = "question",
    storage_key: str,
    subject_name_raw: str = "subject",
    category_raw: str = "category",
) -> NormalizedPaper:
    return NormalizedPaper(
        canonical_id=canonical_id,
        canonical_name=canonical_name,
        year_roc=year_roc,
        exam_name_raw=f"exam-{year_roc}",
        category_raw=category_raw,
        subject_name_raw=subject_name_raw,
        paper_code=f"101-{subject_code}-{file_type}",
        file_type=file_type,
        download_url_source=f"https://source.example/{source_exam_id}-{subject_code}-{file_type}.pdf",
        category_code="101",
        source_exam_id=source_exam_id,
        subject_code=subject_code,
        download_url_mirror="",
        download_url_bundle="",
        storage_key=storage_key,
        checksum=f"sum-{year_roc}-{subject_code}-{file_type}",
    )


class BundlerTests(unittest.TestCase):
    def test_build_bundles_groups_multiple_years_under_one_canonical_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            mirror_dir = root / "mirror"
            bundles_dir = root / "bundles"
            (mirror_dir / "115/exam-new/101/0101").mkdir(parents=True)
            (mirror_dir / "114/exam-old/101/0101").mkdir(parents=True)
            (mirror_dir / "115/exam-new/101/0101/question.pdf").write_bytes(b"%PDF-1.7 latest")
            (mirror_dir / "114/exam-old/101/0101/question.pdf").write_bytes(b"%PDF-1.7 prior")

            catalog = NormalizedCatalog(
                papers=[
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=115,
                        source_exam_id="exam-new",
                        subject_code="0101",
                        storage_key="115/exam-new/101/0101/question.pdf",
                    ),
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=114,
                        source_exam_id="exam-old",
                        subject_code="0101",
                        storage_key="114/exam-old/101/0101/question.pdf",
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

            self.assertEqual(
                result.bundles,
                [
                    BundleAsset(
                        canonical_id="nurse",
                        canonical_name="Nurse",
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
                self.assertIn("115/exam-new/category/0101_subject/question.pdf", names)
                self.assertIn("114/exam-old/category/0101_subject/question.pdf", names)
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
                archive.writestr("114/exam-old/category/0101_subject/question.pdf", b"%PDF-1.7 old")
                archive.writestr("bundle.json", json.dumps({"canonical_id": "nurse"}, ensure_ascii=False))

            (mirror_dir / "115/exam-new/101/0101").mkdir(parents=True)
            (mirror_dir / "115/exam-new/101/0101/question.pdf").write_bytes(b"%PDF-1.7 new")

            catalog = NormalizedCatalog(
                papers=[
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=114,
                        source_exam_id="exam-old",
                        subject_code="0101",
                        storage_key="114/exam-old/101/0101/question.pdf",
                    ),
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=115,
                        source_exam_id="exam-new",
                        subject_code="0101",
                        storage_key="115/exam-new/101/0101/question.pdf",
                    ),
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=115,
                        source_exam_id="exam-new",
                        subject_code="0102",
                        subject_name_raw="missing-subject",
                        storage_key="115/exam-new/101/0102/question.pdf",
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
                self.assertIn("114/exam-old/category/0101_subject/question.pdf", names)
                self.assertIn("115/exam-new/category/0101_subject/question.pdf", names)
                self.assertNotIn("115/exam-new/category/0102_missing-subject/question.pdf", names)
            self.assertEqual(len(result.failures), 1)
            self.assertEqual(result.failures[0]["paper_code"], "101-0102-question")
            self.assertTrue(catalog.papers[0].download_url_bundle.endswith("nurse.zip"))
            self.assertTrue(catalog.papers[1].download_url_bundle.endswith("nurse.zip"))
            self.assertEqual(catalog.papers[2].download_url_bundle, "")

    def test_build_bundles_reuses_matching_legacy_bundle_after_asset_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            mirror_dir = root / "mirror"
            bundles_dir = root / "bundles"
            bundles_dir.mkdir()
            legacy_bundle = bundles_dir / "legacy-nurse.zip"
            with zipfile.ZipFile(legacy_bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("114/exam-old/category/0101_subject/question.pdf", b"%PDF-1.7 old")
                archive.writestr(
                    "bundle.json",
                    json.dumps(
                        {
                            "canonical_id": "canonical-nurse",
                            "canonical_name": "Legacy Nurse",
                            "years": [114],
                            "file_count": 1,
                            "papers": [],
                        },
                        ensure_ascii=False,
                    ),
                )

            (mirror_dir / "115/exam-new/101/0101").mkdir(parents=True)
            (mirror_dir / "115/exam-new/101/0101/question.pdf").write_bytes(b"%PDF-1.7 new")

            catalog = NormalizedCatalog(
                papers=[
                    make_paper(
                        canonical_id="canonical-nurse",
                        canonical_name="Nurse Bundle",
                        year_roc=114,
                        source_exam_id="exam-old",
                        subject_code="0101",
                        storage_key="114/exam-old/101/0101/question.pdf",
                    ),
                    make_paper(
                        canonical_id="canonical-nurse",
                        canonical_name="Nurse Bundle",
                        year_roc=115,
                        source_exam_id="exam-new",
                        subject_code="0101",
                        storage_key="115/exam-new/101/0101/question.pdf",
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

            self.assertEqual(result.failures, [])
            rebuilt_bundle = bundles_dir / "Nurse Bundle.zip"
            self.assertTrue(rebuilt_bundle.exists())
            with zipfile.ZipFile(rebuilt_bundle) as archive:
                names = archive.namelist()
                self.assertIn("114/exam-old/category/0101_subject/question.pdf", names)
                self.assertIn("115/exam-new/category/0101_subject/question.pdf", names)
                manifest = json.loads(archive.read("bundle.json").decode("utf-8"))
                self.assertEqual(manifest["years"], [115, 114])


if __name__ == "__main__":
    unittest.main()
