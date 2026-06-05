import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote

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
                    exam_name_raw="115年專技高考護理師",
                    category_raw="護理師",
                    category_code="101",
                    source_exam_id="115030",
                    subject_code="0101",
                    subject_name_raw="基礎醫學",
                    paper_code="101-0101-question",
                    file_type="question",
                    download_url_source="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?t=Q&code=115030&c=101&s=0101&q=1",
                    download_url_mirror="",
                    download_url_bundle=f"https://github.com/example/repo/releases/download/moex-bundles/{quote('護理師__nurse.zip')}",
                    storage_key="115/115030/101/0101/question.pdf",
                    checksum="abc123",
                )
            ],
            review_queue=[ReviewItem(raw_category="護理師", normalized_candidate="護理師", source_exam_id="115030", year_roc=115)],
        )
        raw_pages = [
            SourceExamPage(
                source_exam_id="115030",
                year_ad=2026,
                year_roc=115,
                exam_name_raw="115年專技高考護理師",
                attachments=[],
                papers=[],
            )
        ]
        aliases = [AliasRule(match_type="exact", raw_pattern="護理師", canonical_id="nurse", canonical_name="護理師")]
        bundles = [
            BundleAsset(
                canonical_id="nurse",
                canonical_name="護理師",
                years=[115],
                file_count=1,
                storage_key="bundles/護理師__nurse.zip",
                asset_name="護理師__nurse.zip",
                download_url=f"https://github.com/example/repo/releases/download/moex-bundles/{quote('護理師__nurse.zip')}",
                legacy_asset_names=["nurse.zip"],
            )
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            write_data_files(root / "data", raw_pages, normalized, aliases, bundles, [])
            build_site(root / "site", normalized, bundles)

            papers = json.loads((root / "data" / "papers" / "2026.json").read_text(encoding="utf-8"))
            self.assertEqual(papers[0]["canonical_name"], "護理師")
            self.assertFalse((root / "data" / "papers.json").exists())
            self.assertFalse((root / "data" / "exams.raw.json").exists())
            self.assertEqual(
                papers[0]["download_url_bundle"],
                f"https://github.com/example/repo/releases/download/moex-bundles/{quote('護理師__nurse.zip')}",
            )

            bundle_index = json.loads((root / "data" / "bundles.json").read_text(encoding="utf-8"))
            self.assertEqual(bundle_index[0]["canonical_id"], "nurse")

            release_assets = json.loads((root / "data" / "release-assets.json").read_text(encoding="utf-8"))
            self.assertEqual(
                release_assets,
                [
                    {"storage_key": "bundles/護理師__nurse.zip", "asset_name": "護理師__nurse.zip", "checksum": ""},
                ],
            )

            review = json.loads((root / "data" / "review-queue.json").read_text(encoding="utf-8"))
            self.assertEqual(review[0]["normalized_candidate"], "護理師")
            self.assertEqual(json.loads((root / "data" / "sync-failures.json").read_text(encoding="utf-8")), [])

            html = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn("護理師", html)
            self.assertTrue((root / "site" / "data" / "bundles.json").exists())
            self.assertTrue((root / "site" / "data" / "papers" / "2026.json").exists())
            self.assertIn("<title>考選部歷屆試題下載</title>", html)
            self.assertIn("<h1>考選部歷屆試題下載</h1>", html)
            self.assertIn("下載整理好的中文壓縮檔", html)
            self.assertIn('<label>考試名稱<select id="canonicalFilter">', html)
            self.assertIn('<label>年度<select id="yearFilter">', html)
            for header in ("考試名稱", "年度", "科目", "分類", "下載整理包", "原始來源"):
                self.assertIn(f"<th>{header}</th>", html)
            self.assertIn("下載壓縮檔", html)
            self.assertNotIn("<th>Canonical</th>", html)
            self.assertNotIn("${paper.canonical_id}", html)
            self.assertNotIn("${paper.file_type}", html)
            self.assertIn("${FILE_TYPE_LABELS[paper.file_type] || paper.file_type}", html)


if __name__ == "__main__":
    unittest.main()
