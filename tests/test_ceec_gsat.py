import unittest
from unittest.mock import patch

from app.providers.base import SourceProvider
from app.providers.registry import get_provider

from app.providers.ceec_gsat.client import CeecGsatClient, parse_listing_page


LISTING_HTML = """
<html><body>
<h2>\u4e00\u822c\u8a66\u984c</h2>
<div>\u5171 19 \u9801 / 189 \u7b46</div>
<div>115-02-23 115\u5b78\u5e74\u5ea6\u5b78\u79d1\u80fd\u529b\u6e2c\u9a57\uff0d\u570b\u7d9c
  <a href="/files/a-question.pdf">\u8a66\u984c\u5167\u5bb9</a>
  <a href="/files/a-question-2.pdf">\u8a66\u984c\u5167\u5bb9</a>
  <a href="/files/a-sheet.pdf">\u7b54\u984c\u5377</a>
  <a href="/files/a-answer.pdf">\u9078\u64c7\u984c\u7b54\u6848</a>
  <a href="/files/a-guideline.pdf">\u975e\u9078\u64c7\u984c\u8a55\u5206\u539f\u5247</a>
</div>
<a href="/xmfile?page=2&amp;xsmsid=0J052424829869345634">\u4e0b\u4e00\u9801</a>
</body></html>
"""


class CeecParserTests(unittest.TestCase):
    def test_parse_listing_page_extracts_total_pages_and_exam_row(self) -> None:
        page = parse_listing_page(LISTING_HTML)

        self.assertEqual(page.total_pages, 19)
        self.assertEqual(page.entries[0].year_ad, 2026)
        self.assertEqual(page.entries[0].source_exam_id, "gsat-115-guozong")
        self.assertEqual(page.entries[0].title, "115\u5b78\u5e74\u5ea6\u5b78\u79d1\u80fd\u529b\u6e2c\u9a57\uff0d\u570b\u7d9c")
        self.assertEqual(
            [item.label for item in page.entries[0].downloads],
            [
                "\u8a66\u984c\u5167\u5bb9",
                "\u8a66\u984c\u5167\u5bb9",
                "\u7b54\u984c\u5377",
                "\u9078\u64c7\u984c\u7b54\u6848",
                "\u975e\u9078\u64c7\u984c\u8a55\u5206\u539f\u5247",
            ],
        )

    def test_fetch_exam_page_turns_one_listing_row_into_many_single_file_papers(self) -> None:
        with patch.object(CeecGsatClient, "_fetch_text", return_value=LISTING_HTML):
            client = CeecGsatClient()
            page = client.fetch_exam_page("gsat-115-guozong", 2026)

        self.assertEqual(page.provider_id, "ceec_gsat")
        self.assertEqual(page.exam_name_raw, "115\u5b78\u5e74\u5ea6\u5b78\u79d1\u80fd\u529b\u6e2c\u9a57\uff0d\u570b\u7d9c")
        self.assertEqual({paper.category_raw for paper in page.papers}, {"\u5b78\u79d1\u80fd\u529b\u6e2c\u9a57"})
        self.assertEqual(
            {file_type for paper in page.papers for file_type in paper.files},
            {"question", "question_alt", "answer_sheet", "answer", "corrected_answer"},
        )

    def test_registry_returns_ceec_provider(self) -> None:
        provider = get_provider("ceec_gsat")

        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "ceec_gsat")


if __name__ == "__main__":
    unittest.main()
