import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from app.bundler import build_bundles
from app.models import NormalizedCatalog, NormalizedPaper


def make_paper(
    *,
    canonical_id: str,
    canonical_name: str,
    year_roc: int,
    source_exam_id: str,
    subject_code: str,
    storage_key: str,
    file_type: str = "question",
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
    def test_build_bundles_groups_multiple_years_under_one_stable_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            mirror_dir = root / "mirror"
            bundles_dir = root / "bundles"
            (mirror_dir / "115/115030/101/0101").mkdir(parents=True)
            (mirror_dir / "114/114030/101/0101").mkdir(parents=True)
            (mirror_dir / "115/115030/101/0101/question.pdf").write_bytes(b"%PDF-1.7 latest")
            (mirror_dir / "114/114030/101/0101/question.pdf").write_bytes(b"%PDF-1.7 prior")

            catalog = NormalizedCatalog(
                papers=[
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=115,
                        source_exam_id="115030",
                        subject_code="0101",
                        subject_name_raw="Anatomy",
                        storage_key="115/115030/101/0101/question.pdf",
                    ),
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=114,
                        source_exam_id="114030",
                        subject_code="0101",
                        subject_name_raw="Anatomy",
                        storage_key="114/114030/101/0101/question.pdf",
                    ),
                ],
                review_queue=[],
            )

            result = build_bundles(
                bundle_dir=bundles_dir,
                mirror_dir=mirror_dir,
                normalized=catalog,
                bundle_base_url="https://ignored.example",
            )

            self.assertEqual(len(result.bundles), 1)
            actual = result.bundles[0]
            self.assertEqual(actual.canonical_id, "nurse")
            self.assertEqual(actual.canonical_name, "Nurse")
            self.assertEqual(actual.years, [115, 114])
            self.assertEqual(actual.file_count, 2)
            self.assertEqual(actual.storage_key, "bundles/nurse.zip")
            self.assertEqual(actual.asset_name, "nurse.zip")
            self.assertEqual(actual.release_tag, "")
            self.assertEqual(actual.download_url, "")
            self.assertEqual(actual.legacy_asset_names, ["Nurse__nurse.zip"])

            bundle_zip = bundles_dir / "nurse.zip"
            self.assertTrue(bundle_zip.exists())
            with zipfile.ZipFile(bundle_zip) as archive:
                names = archive.namelist()
                self.assertIn("115/101_0101_Anatomy_試題.pdf", names)
                self.assertIn("114/101_0101_Anatomy_試題.pdf", names)
                manifest = json.loads(archive.read("bundle.json").decode("utf-8"))
                self.assertEqual(manifest["canonical_id"], "nurse")
                self.assertEqual(manifest["years"], [115, 114])

            self.assertTrue(all(paper.download_url_bundle == "" for paper in catalog.papers))
            self.assertEqual(result.failures, [])

    def test_build_bundles_reuses_existing_bundle_entries_and_skips_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            mirror_dir = root / "mirror"
            bundles_dir = root / "bundles"
            bundles_dir.mkdir()
            existing_bundle = bundles_dir / "nurse.zip"
            with zipfile.ZipFile(existing_bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("114/exam-old/category/0101_Anatomy/question.pdf", b"%PDF-1.7 old")
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
                        subject_name_raw="Anatomy",
                        storage_key="114/exam-old/101/0101/question.pdf",
                    ),
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=115,
                        source_exam_id="exam-new",
                        subject_code="0101",
                        subject_name_raw="Anatomy",
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
                bundle_base_url="https://ignored.example",
            )

            self.assertEqual(len(result.bundles), 1)
            with zipfile.ZipFile(bundles_dir / "nurse.zip") as archive:
                names = archive.namelist()
                self.assertIn("114/101_0101_Anatomy_試題.pdf", names)
                self.assertIn("115/101_0101_Anatomy_試題.pdf", names)
                self.assertNotIn("115/101_0102_missing-subject_試題.pdf", names)
            self.assertEqual(len(result.failures), 1)
            self.assertEqual(result.failures[0]["paper_code"], "101-0102-question")
            self.assertEqual(catalog.papers[0].download_url_bundle, "")
            self.assertEqual(catalog.papers[1].download_url_bundle, "")
            self.assertEqual(catalog.papers[2].download_url_bundle, "")

    def test_build_bundles_preserves_migrated_canonical_alias_asset_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            bundles_dir = root / "bundles"
            bundles_dir.mkdir()
            old_canonical_id = "canonical-old-nurse"
            old_bundle = bundles_dir / f"{old_canonical_id}.zip"
            archive_entry = "114/101_0101_Anatomy_試題.pdf"
            with zipfile.ZipFile(old_bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(archive_entry, b"%PDF-1.7 migrated-old")
                archive.writestr(
                    "bundle.json",
                    json.dumps(
                        {
                            "canonical_id": old_canonical_id,
                            "canonical_name": "Old Nurse",
                            "years": [114],
                            "file_count": 1,
                            "papers": [],
                        },
                        ensure_ascii=False,
                    ),
                )

            catalog = NormalizedCatalog(
                papers=[
                    make_paper(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        year_roc=114,
                        source_exam_id="114030",
                        subject_code="0101",
                        subject_name_raw="Anatomy",
                        storage_key="114/114030/101/0101/question.pdf",
                    ),
                ],
                review_queue=[],
            )

            result = build_bundles(
                bundle_dir=bundles_dir,
                mirror_dir=root / "mirror",
                normalized=catalog,
                bundle_base_url="https://ignored.example",
                canonical_aliases={"nurse": [old_canonical_id]},
            )

            self.assertEqual(result.failures, [])
            self.assertEqual(
                result.bundles[0].legacy_asset_names,
                ["Nurse__nurse.zip", f"{old_canonical_id}.zip"],
            )
            with zipfile.ZipFile(bundles_dir / "nurse.zip") as archive:
                self.assertEqual(archive.read(archive_entry), b"%PDF-1.7 migrated-old")

    def test_build_bundles_uses_explicit_bundle_entry_instead_of_manifest_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            bundles_dir = root / "bundles"
            bundles_dir.mkdir()
            existing_bundle = bundles_dir / "nurse.zip"
            with zipfile.ZipFile(existing_bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("114/exam-old/101_0101_question.pdf", b"%PDF-1.7 first")
                archive.writestr("114/exam-old/101_0102_question.pdf", b"%PDF-1.7 second")
                archive.writestr(
                    "bundle.json",
                    json.dumps(
                        {
                            "canonical_id": "nurse",
                            "canonical_name": "Nurse",
                            "years": [114],
                            "file_count": 2,
                            "papers": [
                                {
                                    "source_exam_id": "exam-old",
                                    "category_code": "101",
                                    "subject_code": "0102",
                                    "file_type": "question",
                                    "bundle_entry": "114/exam-old/101_0102_question.pdf",
                                },
                                {
                                    "source_exam_id": "exam-old",
                                    "category_code": "101",
                                    "subject_code": "0101",
                                    "file_type": "question",
                                    "bundle_entry": "114/exam-old/101_0101_question.pdf",
                                },
                            ],
                        },
                        ensure_ascii=False,
                    ),
                )

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
                        year_roc=114,
                        source_exam_id="exam-old",
                        subject_code="0102",
                        storage_key="114/exam-old/101/0102/question.pdf",
                    ),
                ],
                review_queue=[],
            )

            result = build_bundles(
                bundle_dir=bundles_dir,
                mirror_dir=root / "mirror",
                normalized=catalog,
                bundle_base_url="https://ignored.example",
            )

            self.assertEqual(result.failures, [])
            with zipfile.ZipFile(bundles_dir / "nurse.zip") as archive:
                self.assertEqual(archive.read("114/101_0101_subject_試題.pdf"), b"%PDF-1.7 first")
                self.assertEqual(archive.read("114/101_0102_subject_試題.pdf"), b"%PDF-1.7 second")

    def test_build_bundles_disambiguates_duplicate_arcnames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            mirror_dir = root / "mirror"
            bundles_dir = root / "bundles"
            (mirror_dir / "86/086010/104/2001").mkdir(parents=True)
            (mirror_dir / "86/086020/104/2001").mkdir(parents=True)
            (mirror_dir / "86/086010/104/2001/question.pdf").write_bytes(b"%PDF exam1")
            (mirror_dir / "86/086020/104/2001/question.pdf").write_bytes(b"%PDF exam2")

            catalog = NormalizedCatalog(
                papers=[
                    make_paper(
                        canonical_id="marine",
                        canonical_name="Marine",
                        year_roc=86,
                        source_exam_id="086010",
                        subject_code="2001",
                        subject_name_raw="Navigation",
                        storage_key="86/086010/104/2001/question.pdf",
                    ),
                    make_paper(
                        canonical_id="marine",
                        canonical_name="Marine",
                        year_roc=86,
                        source_exam_id="086020",
                        subject_code="2001",
                        subject_name_raw="Navigation",
                        storage_key="86/086020/104/2001/question.pdf",
                    ),
                ],
                review_queue=[],
            )

            result = build_bundles(
                bundle_dir=bundles_dir,
                mirror_dir=mirror_dir,
                normalized=catalog,
                bundle_base_url="https://ignored.example",
            )

            self.assertEqual(len(result.bundles), 1)
            self.assertEqual(result.bundles[0].file_count, 2)
            with zipfile.ZipFile(bundles_dir / "marine.zip") as archive:
                names = [name for name in archive.namelist() if name != "bundle.json"]
                self.assertEqual(len(names), 2)
                self.assertEqual(len(set(names)), 2, f"Duplicate arcnames found: {names}")
                self.assertIn("86/101_2001_Navigation_試題_086010.pdf", names)
                self.assertIn("86/101_2001_Navigation_試題_086020.pdf", names)
            self.assertEqual(result.failures, [])


if __name__ == "__main__":
    unittest.main()
