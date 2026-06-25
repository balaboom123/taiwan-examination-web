import unittest
from unittest.mock import patch

from app.providers.moea_recruit.client import MoeaRecruitClient, parse_download_page


# Fixture based on the Taipower download listing page structure at
# https://www.taipower.com.tw/tc/download.aspx?mid=261
# The page renders a list of downloadable files inside a <div class="download-list"> container.
# Each entry is a <div class="list-item"> with a <div class="title"> heading and one or more
# <a> links inside a <div class="file"> block.
DOWNLOAD_PAGE_HTML = """
<html>
<head><title>台電下載專區</title></head>
<body>
<div class="download-list">
  <div class="list-item">
    <div class="title">113年新進職員甄試試題解答</div>
    <div class="file">
      <a href="/media/5485/113nian_examination_questions.pdf">試題</a>
      <a href="/media/5486/113nian_examination_answers.pdf">解答</a>
    </div>
  </div>
  <div class="list-item">
    <div class="title">112年新進職員甄試試題解答</div>
    <div class="file">
      <a href="/media/5123/112nian_examination_questions.pdf">試題</a>
      <a href="/media/5124/112nian_examination_answers.pdf">解答</a>
    </div>
  </div>
  <div class="list-item">
    <div class="title">111年新進職員甄試試題解答</div>
    <div class="file">
      <a href="/media/4892/111nian_examination_questions.pdf">試題</a>
      <a href="/media/4893/111nian_examination_answers.pdf">解答</a>
    </div>
  </div>
</div>
</body>
</html>
"""

DOWNLOAD_PAGE_HTML_SINGLE_FILE = """
<html><body>
<div class="download-list">
  <div class="list-item">
    <div class="title">110年新進職員甄試試題解答</div>
    <div class="file">
      <a href="/media/4567/110nian_examination.pdf">試題暨解答</a>
    </div>
  </div>
</div>
</body></html>
"""

DOWNLOAD_PAGE_HTML_NESTED_DIVS = """
<html><body>
<div class="download-list">
  <div class="list-item">
    <div class="title">
      <div>Inner nested div</div>
      114年新進職員甄試試題解答
    </div>
    <div class="file">
      <div class="wrapper">
        <a href="/media/5487/114nian_examination_questions.pdf">試題</a>
      </div>
      <a href="/media/5488/114nian_examination_answers.pdf">解答</a>
    </div>
  </div>
</div>
</body></html>
"""


class MoeaRecruitParserTests(unittest.TestCase):
    def test_parse_download_page_extracts_entries(self) -> None:
        entries = parse_download_page(DOWNLOAD_PAGE_HTML)

        self.assertEqual(len(entries), 3)

    def test_parse_download_page_extracts_year_roc(self) -> None:
        entries = parse_download_page(DOWNLOAD_PAGE_HTML)

        self.assertEqual(entries[0].year_roc, 113)
        self.assertEqual(entries[1].year_roc, 112)
        self.assertEqual(entries[2].year_roc, 111)

    def test_parse_download_page_computes_year_ad(self) -> None:
        entries = parse_download_page(DOWNLOAD_PAGE_HTML)

        self.assertEqual(entries[0].year_ad, 2024)
        self.assertEqual(entries[1].year_ad, 2023)
        self.assertEqual(entries[2].year_ad, 2022)

    def test_parse_download_page_extracts_title(self) -> None:
        entries = parse_download_page(DOWNLOAD_PAGE_HTML)

        self.assertEqual(entries[0].title, "113年新進職員甄試試題解答")

    def test_parse_download_page_extracts_downloads(self) -> None:
        entries = parse_download_page(DOWNLOAD_PAGE_HTML)

        self.assertEqual(len(entries[0].downloads), 2)
        self.assertEqual(entries[0].downloads[0].label, "試題")
        self.assertEqual(entries[0].downloads[0].url, "https://www.taipower.com.tw/media/5485/113nian_examination_questions.pdf")
        self.assertEqual(entries[0].downloads[1].label, "解答")
        self.assertEqual(entries[0].downloads[1].url, "https://www.taipower.com.tw/media/5486/113nian_examination_answers.pdf")

    def test_parse_download_page_handles_single_file_entry(self) -> None:
        entries = parse_download_page(DOWNLOAD_PAGE_HTML_SINGLE_FILE)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].year_roc, 110)
        self.assertEqual(len(entries[0].downloads), 1)
        self.assertEqual(entries[0].downloads[0].label, "試題暨解答")

    def test_parse_download_page_handles_nested_divs(self) -> None:
        """Test that nested divs inside title and file sections don't break parsing."""
        entries = parse_download_page(DOWNLOAD_PAGE_HTML_NESTED_DIVS)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].year_roc, 114)
        self.assertEqual(entries[0].year_ad, 2025)
        # Should extract both downloads despite nested divs in file section
        self.assertEqual(len(entries[0].downloads), 2)
        self.assertEqual(entries[0].downloads[0].label, "試題")
        self.assertEqual(entries[0].downloads[1].label, "解答")
        # Title should be extracted correctly despite nested div
        self.assertIn("114年新進職員甄試試題解答", entries[0].title)

    def test_parse_download_page_empty_html_returns_empty_list(self) -> None:
        entries = parse_download_page("<html><body></body></html>")

        self.assertEqual(entries, [])

    def test_fetch_exam_page_builds_source_exam_page(self) -> None:
        with patch.object(MoeaRecruitClient, "_fetch_text", return_value=DOWNLOAD_PAGE_HTML):
            client = MoeaRecruitClient()
            page = client.fetch_exam_page("moea-recruit-113", 2024)

        self.assertEqual(page.provider_id, "moea_recruit")
        self.assertEqual(page.source_exam_id, "moea-recruit-113")
        self.assertEqual(page.year_ad, 2024)
        self.assertEqual(page.year_roc, 113)
        self.assertEqual(page.exam_name_raw, "113年新進職員甄試試題解答")
        self.assertEqual(len(page.papers), 2)
        self.assertEqual({paper.category_raw for paper in page.papers}, {"國營事業聯招（新進職員）"})

    def test_fetch_exam_page_assigns_question_and_answer_file_types(self) -> None:
        with patch.object(MoeaRecruitClient, "_fetch_text", return_value=DOWNLOAD_PAGE_HTML):
            client = MoeaRecruitClient()
            page = client.fetch_exam_page("moea-recruit-113", 2024)

        file_types = {file_type for paper in page.papers for file_type in paper.files}
        self.assertIn("question", file_types)
        self.assertIn("answer", file_types)

    def test_discover_available_years_returns_sorted_descending(self) -> None:
        with patch.object(MoeaRecruitClient, "_fetch_text", return_value=DOWNLOAD_PAGE_HTML):
            client = MoeaRecruitClient()
            years = client.discover_available_years()

        self.assertEqual(years, [2024, 2023, 2022])

    def test_discover_exams_returns_exam_options_for_year(self) -> None:
        with patch.object(MoeaRecruitClient, "_fetch_text", return_value=DOWNLOAD_PAGE_HTML):
            client = MoeaRecruitClient()
            exams = client.discover_exams(2024)

        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0].code, "moea-recruit-113")
        self.assertEqual(exams[0].year_ad, 2024)
        self.assertEqual(exams[0].year_roc, 113)

    def test_registry_returns_moea_recruit_provider(self) -> None:
        from app.providers.registry import get_provider
        from app.providers.base import SourceProvider

        provider = get_provider("moea_recruit")

        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "moea_recruit")


if __name__ == "__main__":
    unittest.main()
