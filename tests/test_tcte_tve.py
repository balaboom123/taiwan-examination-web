import unittest
from unittest.mock import patch

from app.models import NormalizedCatalog
from app.normalizer import normalize_papers
from app.providers.base import SourceProvider
from app.providers.registry import get_provider

from app.providers.tcte_tve.client import TcteTveClient, parse_listing_page, parse_year_page


LISTING_HTML = """
<html><body>
<table>
  <tr>
    <td>115</td>
    <td><a href="/index.php?mod=TVETest/down_exam4y/fn/115Reg_4y.pdf">下載</a></td>
    <td><a href="/index.php?mod=TVETest/majtype/Page/115majtype_4Y">查閱</a></td>
    <td><a href="https://web1.tcte.edu.tw/EXAM/115_4y">查閱(另開新視窗)</a></td>
  </tr>
</table>
</body></html>
"""

YEAR_HTML = """
<html><body>
<div id="tab1" class="tab_content">
<table class="myexam">
  <tr><th>共同科目</th><th>考科</th><th>試題</th><th>標準答案</th></tr>
  <tr>
    <td rowspan="6">共同科目</td>
    <td>國文科</td>
    <td>
      <input type="image" src="images/icon_pdf.jpg" onclick="location.href='downloader.php?obj=question-pdf'">
      <input type="image" src="images/icon_word.jpg" onclick="location.href='downloader.php?obj=question-docx'">
    </td>
    <td><input type="image" src="images/icon_pdf.jpg" onclick="location.href='downloader.php?obj=answer-pdf'"></td>
    <td><input type="image" src="images/icon_pdf.jpg" onclick="location.href='downloader.php?obj=feature-pdf'"></td>
  </tr>
</table>
<table class="myexam">
  <tr><th>群(類)別</th><th>考科</th><th>試題</th><th>標準答案</th></tr>
  <tr>
    <td rowspan="2">01機械群</td>
    <td>專業科目(一)</td>
    <td><input type="image" src="images/icon_pdf.jpg" onclick="location.href='downloader.php?obj=pro-question-pdf'"></td>
    <td><input type="image" src="images/icon_pdf.jpg" onclick="location.href='downloader.php?obj=pro-answer-pdf'"></td>
  </tr>
</table>
</div>
</body></html>
"""


class TcteTveParserTests(unittest.TestCase):
    def test_parse_listing_page_extracts_year_page(self) -> None:
        pages = parse_listing_page(LISTING_HTML)

        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].year_ad, 2026)
        self.assertEqual(pages[0].url, "https://web1.tcte.edu.tw/EXAM/115_4y")

    def test_parse_year_page_extracts_common_and_professional_papers(self) -> None:
        papers = parse_year_page(YEAR_HTML, "https://web1.tcte.edu.tw/EXAM/115_4y/")

        self.assertEqual(len(papers), 2)
        self.assertEqual(papers[0].category_raw, "四技二專統一入學測驗")
        self.assertEqual(papers[0].category_code, "common")
        self.assertEqual(papers[0].subject_code, "chinese")
        self.assertEqual(papers[0].files["question"], "https://web1.tcte.edu.tw/EXAM/115_4y/downloader.php?obj=question-pdf")
        self.assertEqual(papers[0].files["question_alt"], "https://web1.tcte.edu.tw/EXAM/115_4y/downloader.php?obj=question-docx")
        self.assertEqual(papers[0].files["answer"], "https://web1.tcte.edu.tw/EXAM/115_4y/downloader.php?obj=answer-pdf")
        self.assertNotIn("feature", papers[0].files)
        self.assertEqual(papers[1].category_code, "01")
        self.assertEqual(papers[1].subject_code, "professional-1")

    def test_fetch_exam_page_turns_year_page_into_one_source_page(self) -> None:
        def fake_fetch(url: str) -> str:
            if "down_exam4y" in url:
                return LISTING_HTML
            return YEAR_HTML

        with patch.object(TcteTveClient, "_fetch_text", side_effect=fake_fetch):
            client = TcteTveClient()
            page = client.fetch_exam_page("tcte-tve-115", 2026)

        self.assertEqual(page.provider_id, "tcte_tve")
        self.assertEqual(page.source_exam_id, "tcte-tve-115")
        self.assertEqual(page.year_roc, 115)
        self.assertEqual(page.exam_name_raw, "115學年度四技二專統一入學測驗")
        self.assertEqual(len(page.papers), 2)

    def test_registry_returns_tcte_tve_provider(self) -> None:
        provider = get_provider("tcte_tve")

        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "tcte_tve")

    def test_tcte_tve_normalization_uses_stable_canonical_bundle_identity(self) -> None:
        with patch.object(TcteTveClient, "_fetch_text", side_effect=lambda url: LISTING_HTML if "down_exam4y" in url else YEAR_HTML):
            client = TcteTveClient()
            page = client.fetch_exam_page("tcte-tve-115", 2026)

        mirror_metadata = {}
        for paper in page.papers:
            for file_type in paper.files:
                mirror_metadata[(paper.category_code, paper.subject_code, file_type)] = {
                    "checksum": f"{paper.subject_code}-{file_type}",
                    "storage_key": f"providers/tcte_tve/115/{page.source_exam_id}/{paper.category_code}/{paper.subject_code}/{file_type}.pdf",
                }

        normalized = normalize_papers(
            source_exam_id=page.source_exam_id,
            year_ad=page.year_ad,
            exam_name_raw=page.exam_name_raw,
            papers=page.papers,
            alias_rules=[],
            mirror_base_url="",
            mirror_metadata=mirror_metadata,
        )

        self.assertIsInstance(normalized, NormalizedCatalog)
        self.assertEqual({paper.canonical_id for paper in normalized.papers}, {"tcte-tve"})
        self.assertEqual({paper.canonical_name for paper in normalized.papers}, {"四技二專統一入學測驗"})
        self.assertEqual(normalized.review_queue, [])


if __name__ == "__main__":
    unittest.main()
