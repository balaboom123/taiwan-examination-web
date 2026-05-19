import json
import tempfile
import unittest
from pathlib import Path

from app.models import AliasRule, BundleAsset, NormalizedCatalog, NormalizedPaper, ReviewItem, SourceExamPage
from app.publisher import build_site, write_data_files


class PublisherTests(unittest.TestCase):
    def test_write_data_files_and_site(self) -> None:
        normalized = NormalizedCatalog(
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
                    download_url_source="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?t=Q&code=115030&c=101&s=0101&q=1",
                    download_url_mirror="",
                    download_url_bundle="https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
                    storage_key="115/115030/101/0101/question.pdf",
                    checksum="abc123",
                )
            ],
            review_queue=[ReviewItem(raw_category="高等考試_護理師", normalized_candidate="護理師", source_exam_id="115030", year_roc=115)],
        )
        raw_pages = [
            SourceExamPage(
                source_exam_id="115030",
                year_ad=2026,
                year_roc=115,
                exam_name_raw="115年第一次專門職業及技術人員高等考試營養師、護理師、社會工作師考試",
                attachments=[],
                papers=[],
            )
        ]
        aliases = [AliasRule(match_type="exact", raw_pattern="高等考試_護理師", canonical_id="nurse", canonical_name="護理師")]
        bundles = [
            BundleAsset(
                canonical_id="nurse",
                canonical_name="護理師",
                years=[115],
                file_count=1,
                storage_key="bundles/nurse.zip",
                asset_name="nurse.zip",
                download_url="https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
            )
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            write_data_files(root / "data", raw_pages, normalized, aliases, bundles, [])
            build_site(root / "site", normalized, bundles)

            papers = json.loads((root / "data" / "papers.json").read_text(encoding="utf-8"))
            self.assertEqual(papers[0]["canonical_name"], "護理師")
            self.assertTrue(papers[0]["download_url_bundle"].endswith("nurse.zip"))

            bundle_index = json.loads((root / "data" / "bundles.json").read_text(encoding="utf-8"))
            self.assertEqual(bundle_index[0]["canonical_id"], "nurse")

            release_assets = json.loads((root / "data" / "release-assets.json").read_text(encoding="utf-8"))
            self.assertEqual(release_assets, [{"storage_key": "bundles/nurse.zip", "asset_name": "nurse.zip"}])

            review = json.loads((root / "data" / "review-queue.json").read_text(encoding="utf-8"))
            self.assertEqual(review[0]["normalized_candidate"], "護理師")
            self.assertEqual(json.loads((root / "data" / "sync-failures.json").read_text(encoding="utf-8")), [])

            html = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn("護理師", html)
            self.assertIn("基礎醫學", html)
            self.assertIn("nurse.zip", html)


if __name__ == "__main__":
    unittest.main()
