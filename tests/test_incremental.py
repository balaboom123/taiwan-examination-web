import unittest

from app.models import BundleAsset, NormalizedCatalog, NormalizedPaper, ReviewItem, SourceExamPage
from app.state import merge_incremental_state


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
                storage_key="bundles/nurse.zip",
                asset_name="nurse.zip",
                download_url="https://bundles.example/nurse.zip",
            ),
            BundleAsset(
                canonical_id="teacher",
                canonical_name="教育行政",
                years=[115],
                file_count=1,
                storage_key="bundles/教育行政.zip",
                asset_name="教育行政.zip",
                download_url="https://bundles.example/教育行政.zip",
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

        merged_raw_pages, merged_catalog, preserved_bundles, affected_canonical_ids = merge_incremental_state(
            existing_raw_pages=existing_raw_pages,
            existing_catalog=existing_catalog,
            existing_bundles=existing_bundles,
            refreshed_raw_pages=refreshed_raw_pages,
            refreshed_catalog=refreshed_catalog,
            refreshed_year_rocs={115},
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
        self.assertEqual(affected_canonical_ids, {"nurse"})


if __name__ == "__main__":
    unittest.main()
