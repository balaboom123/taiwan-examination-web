import unittest
from urllib.parse import quote

from app.models import BundleAsset, NormalizedCatalog, NormalizedPaper, ReviewItem, SourceExamPage
from app.state import merge_incremental_state, merge_targeted_state


class IncrementalStateTests(unittest.TestCase):
    def test_merge_incremental_state_preserves_older_years_and_marks_affected_canonicals(self) -> None:
        existing_raw_pages = [
            SourceExamPage(
                source_exam_id="113180",
                year_ad=2024,
                year_roc=113,
                exam_name_raw="113年第三次專門職業及技術人員高等考試護理師考試",
                attachments=[],
                papers=[],
            ),
            SourceExamPage(
                source_exam_id="115030",
                year_ad=2026,
                year_roc=115,
                exam_name_raw="115年第一次專門職業及技術人員高等考試營養師、護理師、社會工作師考試",
                attachments=[],
                papers=[],
            ),
        ]
        existing_catalog = NormalizedCatalog(
            papers=[
                NormalizedPaper(
                    canonical_id="nurse",
                    canonical_name="護理師",
                    year_roc=113,
                    exam_name_raw="113年第三次專門職業及技術人員高等考試護理師考試",
                    category_raw="專門職業及技術人員高等考試護理師考試",
                    category_code="101",
                    source_exam_id="113180",
                    subject_code="0101",
                    subject_name_raw="基礎醫學",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://source.example/113-question.pdf",
                    storage_key="113/113180/101/0101/question.pdf",
                    checksum="old113",
                ),
                NormalizedPaper(
                    canonical_id="teacher",
                    canonical_name="教育行政",
                    year_roc=115,
                    exam_name_raw="115年公務人員初等考試",
                    category_raw="教育行政",
                    category_code="401",
                    source_exam_id="115010",
                    subject_code="0401",
                    subject_name_raw="教育學大意",
                    paper_code="401-0401-question",
                    file_type="question",
                    download_url_source="https://source.example/teacher-question.pdf",
                    storage_key="115/115010/401/0401/question.pdf",
                    checksum="teacher115",
                ),
            ],
            review_queue=[ReviewItem(raw_category="專門職業及技術人員高等考試護理師考試", normalized_candidate="護理師", source_exam_id="113180", year_roc=113)],
        )
        existing_bundles = [
            BundleAsset(
                canonical_id="nurse",
                canonical_name="護理師",
                years=[115, 113],
                file_count=2,
                storage_key="bundles/護理師__nurse.zip",
                asset_name="護理師__nurse.zip",
                download_url="https://bundles.example/護理師__nurse.zip",
                legacy_asset_names=["nurse.zip"],
            ),
            BundleAsset(
                canonical_id="teacher",
                canonical_name="教育行政",
                years=[115],
                file_count=1,
                storage_key="bundles/教育行政__teacher.zip",
                asset_name="教育行政__teacher.zip",
                download_url="https://bundles.example/教育行政__teacher.zip",
                legacy_asset_names=["teacher.zip"],
            ),
        ]

        refreshed_raw_pages = [
            SourceExamPage(
                source_exam_id="115030",
                year_ad=2026,
                year_roc=115,
                exam_name_raw="115年第一次專門職業及技術人員高等考試營養師、護理師、社會工作師考試",
                attachments=[],
                papers=[],
            )
        ]
        refreshed_catalog = NormalizedCatalog(
            papers=[
                NormalizedPaper(
                    canonical_id="nurse",
                    canonical_name="護理師",
                    year_roc=115,
                    exam_name_raw="115年第一次專門職業及技術人員高等考試營養師、護理師、社會工作師考試",
                    category_raw="高等考試_護理師",
                    category_code="101",
                    source_exam_id="115030",
                    subject_code="0101",
                    subject_name_raw="基礎醫學",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://source.example/115-question.pdf",
                    storage_key="115/115030/101/0101/question.pdf",
                    checksum="new115",
                )
            ],
            review_queue=[],
        )

        merged_raw_pages, merged_catalog, preserved_bundles, affected_canonical_ids, canonical_aliases = merge_incremental_state(
            existing_raw_pages=existing_raw_pages,
            existing_catalog=existing_catalog,
            existing_bundles=existing_bundles,
            refreshed_raw_pages=refreshed_raw_pages,
            refreshed_catalog=refreshed_catalog,
        )

        self.assertEqual({page.year_roc for page in merged_raw_pages}, {113, 115})
        self.assertEqual(
            {(paper.canonical_id, paper.year_roc, paper.checksum) for paper in merged_catalog.papers},
            {
                ("nurse", 113, "old113"),
                ("nurse", 115, "new115"),
                ("teacher", 115, "teacher115"),
            },
        )
        self.assertEqual({bundle.canonical_id for bundle in preserved_bundles}, {"teacher"})
        self.assertEqual(preserved_bundles[0].asset_name, "教育行政__teacher.zip")
        self.assertEqual(preserved_bundles[0].legacy_asset_names, ["teacher.zip"])
        self.assertEqual(affected_canonical_ids, {"nurse"})
        self.assertEqual(canonical_aliases, {})

    def test_merge_incremental_state_migrates_previous_canonical_family_to_refreshed_id(self) -> None:
        existing_raw_pages = [
            SourceExamPage(source_exam_id="114030", year_ad=2025, year_roc=114, exam_name_raw="old 114", attachments=[], papers=[]),
            SourceExamPage(source_exam_id="115030", year_ad=2026, year_roc=115, exam_name_raw="old 115", attachments=[], papers=[]),
        ]
        existing_catalog = NormalizedCatalog(
            papers=[
                NormalizedPaper(
                    canonical_id="canonical-badold",
                    canonical_name="舊亂碼名稱",
                    year_roc=114,
                    exam_name_raw="old 114",
                    category_raw="舊亂碼名稱",
                    category_code="101",
                    source_exam_id="114030",
                    subject_code="0101",
                    subject_name_raw="基礎醫學",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://source.example/114-question.pdf",
                    storage_key="114/114030/101/0101/question.pdf",
                    checksum="old114",
                ),
                NormalizedPaper(
                    canonical_id="canonical-badold",
                    canonical_name="舊亂碼名稱",
                    year_roc=115,
                    exam_name_raw="old 115",
                    category_raw="舊亂碼名稱",
                    category_code="101",
                    source_exam_id="115030",
                    subject_code="0101",
                    subject_name_raw="基礎醫學",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://source.example/115-old-question.pdf",
                    storage_key="115/115030/101/0101/question.pdf",
                    checksum="old115",
                ),
            ],
            review_queue=[],
        )
        existing_bundles = [
            BundleAsset(
                canonical_id="canonical-badold",
                canonical_name="舊亂碼名稱",
                years=[115, 114],
                file_count=2,
                storage_key="bundles/canonical-badold.zip",
                asset_name="canonical-badold.zip",
                download_url=f"https://bundles.example/{quote('canonical-badold.zip')}",
            )
        ]
        refreshed_raw_pages = [
            SourceExamPage(source_exam_id="115030", year_ad=2026, year_roc=115, exam_name_raw="new 115", attachments=[], papers=[])
        ]
        refreshed_catalog = NormalizedCatalog(
            papers=[
                NormalizedPaper(
                    canonical_id="nurse",
                    canonical_name="護理師",
                    year_roc=115,
                    exam_name_raw="new 115",
                    category_raw="高等考試_護理師",
                    category_code="101",
                    source_exam_id="115030",
                    subject_code="0101",
                    subject_name_raw="基礎醫學",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://source.example/115-question.pdf",
                    storage_key="115/115030/101/0101/question.pdf",
                    checksum="new115",
                )
            ],
            review_queue=[],
        )

        _, merged_catalog, preserved_bundles, affected_canonical_ids, canonical_aliases = merge_incremental_state(
            existing_raw_pages=existing_raw_pages,
            existing_catalog=existing_catalog,
            existing_bundles=existing_bundles,
            refreshed_raw_pages=refreshed_raw_pages,
            refreshed_catalog=refreshed_catalog,
        )

        self.assertEqual(
            {(paper.canonical_id, paper.canonical_name, paper.year_roc) for paper in merged_catalog.papers},
            {("nurse", "護理師", 114), ("nurse", "護理師", 115)},
        )
        self.assertEqual(preserved_bundles, [])
        self.assertEqual(affected_canonical_ids, {"canonical-badold", "nurse"})
        self.assertEqual(canonical_aliases, {"nurse": ["canonical-badold"]})

    def test_merge_targeted_state_removes_deleted_exam_and_marks_previous_canonical(self) -> None:
        existing_raw_pages = [
            SourceExamPage(source_exam_id="115040", year_ad=2026, year_roc=115, exam_name_raw="keep", attachments=[], papers=[]),
            SourceExamPage(source_exam_id="115030", year_ad=2026, year_roc=115, exam_name_raw="remove", attachments=[], papers=[]),
        ]
        existing_catalog = NormalizedCatalog(
            papers=[
                NormalizedPaper(
                    canonical_id="nurse",
                    canonical_name="Nurse",
                    year_roc=115,
                    exam_name_raw="keep",
                    category_raw="Nurse",
                    subject_name_raw="Subject",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://source.example/keep.pdf",
                    source_exam_id="115040",
                ),
                NormalizedPaper(
                    canonical_id="doctor",
                    canonical_name="Doctor",
                    year_roc=115,
                    exam_name_raw="remove",
                    category_raw="Doctor",
                    subject_name_raw="Subject",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://source.example/remove.pdf",
                    source_exam_id="115030",
                ),
            ],
            review_queue=[],
        )
        existing_bundles = [
            BundleAsset(canonical_id="nurse", canonical_name="Nurse", years=[115], file_count=1, storage_key="bundles/nurse.zip", asset_name="nurse.zip"),
            BundleAsset(canonical_id="doctor", canonical_name="Doctor", years=[115], file_count=1, storage_key="bundles/doctor.zip", asset_name="doctor.zip"),
        ]

        merged_raw_pages, merged_catalog, preserved_bundles, affected_canonical_ids, canonical_aliases = merge_targeted_state(
            existing_raw_pages=existing_raw_pages,
            existing_catalog=existing_catalog,
            existing_bundles=existing_bundles,
            refreshed_raw_pages=[],
            refreshed_catalog=NormalizedCatalog(papers=[], review_queue=[]),
            removed_exam_ids={"115030"},
        )

        self.assertEqual([page.source_exam_id for page in merged_raw_pages], ["115040"])
        self.assertEqual([paper.source_exam_id for paper in merged_catalog.papers], ["115040"])
        self.assertEqual({bundle.canonical_id for bundle in preserved_bundles}, {"nurse"})
        self.assertEqual(affected_canonical_ids, {"doctor"})
        self.assertEqual(canonical_aliases, {})


if __name__ == "__main__":
    unittest.main()
