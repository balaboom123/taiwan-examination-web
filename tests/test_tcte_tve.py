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


ANCHOR_YEAR_HTML = """
<html><body>
<table>
  <tr>
    <td rowspan="3">共同科目</td>
    <td>數學科</td>
    <td><a href="math-question.pdf">試題</a></td>
    <td>
      <table>
        <tr><td><a href="math-a-answer.pdf">數學(A)答案</a></td></tr>
        <tr><td><a href="math-b-answer.pdf">數學(B)答案</a></td></tr>
        <tr><td><a href="math-c-answer.pdf">數學(C)答案</a></td></tr>
      </table>
    </td>
  </tr>
  <tr>
    <td rowspan="2">01機械類</td>
    <td>專業科目(一)</td>
    <td><a href="pro-question.pdf">試題</a></td>
    <td><a href="pro-answer.pdf">標準答案</a></td>
  </tr>
</table>
</body></html>
"""


HISTORICAL_90_HTML = """
<html><body><table>
  <tr><td><a href="answer.htm">各類科試題解答</a></td></tr>
  <tr><td>◎ 共同科數學 <a href="math/p1.jpg">p.1</a>/<a href="math/p2.jpg">p.2</a></td></tr>
  <tr><td>◎化工類專一 <a href="chem/p1.jpg">p.1</a>/<a href="chem/p2.jpg">p.2</a></td></tr>
  <tr><td><a href="202114_2.pdf">◎商業類專二</a></td></tr>
  <tr><td><a href="202114_2.pdf">◎語文類英文組專二</a></td></tr>
</table></body></html>
"""

HISTORICAL_91_HTML = """
<html><body>
<table><tr><td>各類科標準答案
  <a href="91-4y-answer-new.xls">Excel檔案格式</a>
  <a href="91-4y-answer-new.pdf">PDF檔案格式</a>
</td></tr>
<tr><td>◎ 共同科目
  <a href="91-c.pdf">國文</a>
  <a href="91-e.pdf">英文(update)</a>
  <a href="91-m.pdf">數學</a>
  <table><tr><td>◎ 01機械類
    <a href="91-01-1.pdf">專業科目一</a>
    <a href="91-01-2.pdf">專業科目二</a>
  </td></tr></table>
</td></tr></table>
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
        self.assertNotIn("question_alt", papers[0].files)
        self.assertEqual(papers[0].files["answer"], "https://web1.tcte.edu.tw/EXAM/115_4y/downloader.php?obj=answer-pdf")
        self.assertNotIn("feature", papers[0].files)
        self.assertEqual(papers[1].category_code, "01")
        self.assertEqual(papers[1].subject_code, "professional-1")


    def test_parse_year_page_supports_historical_anchor_links_and_shared_math_answers(self) -> None:
        papers = parse_year_page(ANCHOR_YEAR_HTML, "https://web1.tcte.edu.tw/EXAM/094_4y/")

        self.assertEqual(len(papers), 4)
        math_papers = [paper for paper in papers if paper.subject_code.startswith("math-")]
        self.assertEqual([paper.subject_code for paper in math_papers], ["math-a", "math-b", "math-c"])
        self.assertEqual({paper.files["question"] for paper in math_papers}, {"https://web1.tcte.edu.tw/EXAM/094_4y/math-question.pdf"})
        self.assertEqual(
            [paper.files["answer"] for paper in math_papers],
            [
                "https://web1.tcte.edu.tw/EXAM/094_4y/math-a-answer.pdf",
                "https://web1.tcte.edu.tw/EXAM/094_4y/math-b-answer.pdf",
                "https://web1.tcte.edu.tw/EXAM/094_4y/math-c-answer.pdf",
            ],
        )
        self.assertEqual(papers[-1].subject_code, "professional-1")
        self.assertEqual(papers[-1].files["answer"], "https://web1.tcte.edu.tw/EXAM/094_4y/pro-answer.pdf")

    def test_parse_roc_90_page_keeps_multipart_images_html_answers_and_shared_questions(self) -> None:
        papers = parse_year_page(HISTORICAL_90_HTML, "https://web1.tcte.edu.tw/EXAM/090_4y/")
        by_key = {(paper.category_code, paper.subject_code): paper for paper in papers}

        self.assertEqual(
            list(by_key[("common", "math")].files),
            ["question_page_01", "question_page_02"],
        )
        self.assertEqual(
            by_key[("05", "professional-1")].files["question_page_02"],
            "https://web1.tcte.edu.tw/EXAM/090_4y/chem/p2.jpg",
        )
        self.assertEqual(
            by_key[("14", "professional-2")].files["question"],
            by_key[("20", "professional-2")].files["question"],
        )
        self.assertEqual(
            by_key[("common", "all")].files,
            {"answer_table": "https://web1.tcte.edu.tw/EXAM/090_4y/answer.htm"},
        )

    def test_parse_roc_91_page_keeps_questions_and_preferred_pdf_answer(self) -> None:
        papers = parse_year_page(HISTORICAL_91_HTML, "https://web1.tcte.edu.tw/EXAM/091_4y/")
        by_key = {(paper.category_code, paper.subject_code): paper for paper in papers}

        self.assertEqual(
            {key for key in by_key},
            {
                ("common", "chinese"),
                ("common", "english"),
                ("common", "math"),
                ("common", "all"),
                ("01", "professional-1"),
                ("01", "professional-2"),
            },
        )
        self.assertEqual(
            by_key[("common", "all")].files,
            {"all_answers": "https://web1.tcte.edu.tw/EXAM/091_4y/91-4y-answer-new.pdf"},
        )
        self.assertNotIn("91-4y-answer-new.xls", {url for paper in papers for url in paper.files.values()})

    def test_discovery_builders_reuse_one_listing_fetch(self) -> None:
        with patch.object(TcteTveClient, "_fetch_text", return_value=LISTING_HTML) as fetch:
            client = TcteTveClient()

            self.assertEqual(client.discover_available_years(), [2026])
            self.assertEqual(client.build_discovery_year_url(2026), "https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y")
            self.assertEqual(
                client.build_discovery_exam_url("tcte-tve-115", 2026),
                "https://web1.tcte.edu.tw/EXAM/115_4y/",
            )
            self.assertEqual(client.discover_exams(2026)[0].code, "tcte-tve-115")

        self.assertEqual(fetch.call_count, 1)

    def test_discovery_builders_reject_unknown_year_and_exam(self) -> None:
        with patch.object(TcteTveClient, "_fetch_text", return_value=LISTING_HTML):
            client = TcteTveClient()
            with self.assertRaisesRegex(ValueError, "Unknown TCTE TVE year"):
                client.build_discovery_year_url(2025)
            with self.assertRaisesRegex(ValueError, "Unknown TCTE TVE exam"):
                client.build_discovery_exam_url("tcte-tve-114", 2026)

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
