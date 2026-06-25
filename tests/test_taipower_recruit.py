import unittest
from unittest.mock import patch

from app.providers.taipower_recruit.client import TaipowerRecruitClient, parse_hiring_page


# Fixture based on the Taipower download listing page structure at
# https://www.taipower.com.tw/tc/download.aspx?mid=262
# The page renders a list of downloadable files inside a <div class="download-list"> container.
# Each entry is a <div class="list-item"> with a <div class="title"> heading and one or more
# <a> links inside a <div class="file"> block.
# NOTE: mid=262 is Taipower's OWN hiring exam; mid=261 is the MOEA joint exam.
HIRING_PAGE_HTML = """
<html>
<head><title>台電下載專區</title></head>
<body>
<div class="download-list">
  <div class="list-item">
    <div class="title">113年新進僱用人員甄試試題解答</div>
    <div class="file">
      <a href="/media/5585/113nian_hiring_questions.pdf">試題</a>
      <a href="/media/5586/113nian_hiring_answers.pdf">解答</a>
    </div>
  </div>
  <div class="list-item">
    <div class="title">112年新進僱用人員甄試試題解答</div>
    <div class="file">
      <a href="/media/5223/112nian_hiring_questions.pdf">試題</a>
      <a href="/media/5224/112nian_hiring_answers.pdf">解答</a>
    </div>
  </div>
  <div class="list-item">
    <div class="title">107年12月新進僱用人員甄試試題解答</div>
    <div class="file">
      <a href="/media/3892/107dec_hiring_questions.pdf">試題</a>
      <a href="/media/3893/107dec_hiring_answers.pdf">解答</a>
    </div>
  </div>
  <div class="list-item">
    <div class="title">107年5月新進僱用人員甄試試題解答</div>
    <div class="file">
      <a href="/media/3790/107may_hiring_questions.pdf">試題</a>
      <a href="/media/3791/107may_hiring_answers.pdf">解答</a>
    </div>
  </div>
  <div class="list-item">
    <div class="title">106年新進僱用人員甄試試題解答</div>
    <div class="file">
      <a href="/media/3600/106nian_hiring_questions.pdf">試題</a>
      <a href="/media/3601/106nian_hiring_answers.pdf">解答</a>
    </div>
  </div>
</div>
</body>
</html>
"""

HIRING_PAGE_HTML_SINGLE_FILE = """
<html><body>
<div class="download-list">
  <div class="list-item">
    <div class="title">111年新進僱用人員甄試試題解答</div>
    <div class="file">
      <a href="/media/4992/111nian_hiring.pdf">試題暨解答</a>
    </div>
  </div>
</div>
</body></html>
"""

HIRING_PAGE_HTML_NESTED_DIVS = """
<html><body>
<div class="download-list">
  <div class="list-item">
    <div class="title">
      <div>Inner nested div</div>
      114年新進僱用人員甄試試題解答
    </div>
    <div class="file">
      <div class="wrapper">
        <a href="/media/5587/114nian_hiring_questions.pdf">試題</a>
      </div>
      <a href="/media/5588/114nian_hiring_answers.pdf">解答</a>
    </div>
  </div>
</div>
</body></html>
"""


class TaipowerRecruitParserTests(unittest.TestCase):
    def test_parse_hiring_page_extracts_entries(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML)

        self.assertEqual(len(entries), 5)

    def test_parse_hiring_page_extracts_year_roc(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML)

        self.assertEqual(entries[0].year_roc, 113)
        self.assertEqual(entries[1].year_roc, 112)
        self.assertEqual(entries[2].year_roc, 107)
        self.assertEqual(entries[3].year_roc, 107)
        self.assertEqual(entries[4].year_roc, 106)

    def test_parse_hiring_page_computes_year_ad(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML)

        self.assertEqual(entries[0].year_ad, 2024)
        self.assertEqual(entries[1].year_ad, 2023)
        self.assertEqual(entries[2].year_ad, 2018)
        self.assertEqual(entries[3].year_ad, 2018)
        self.assertEqual(entries[4].year_ad, 2017)

    def test_parse_hiring_page_extracts_title(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML)

        self.assertEqual(entries[0].title, "113年新進僱用人員甄試試題解答")

    def test_parse_hiring_page_extracts_downloads(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML)

        self.assertEqual(len(entries[0].downloads), 2)
        self.assertEqual(entries[0].downloads[0].label, "試題")
        self.assertEqual(
            entries[0].downloads[0].url,
            "https://www.taipower.com.tw/media/5585/113nian_hiring_questions.pdf",
        )
        self.assertEqual(entries[0].downloads[1].label, "解答")
        self.assertEqual(
            entries[0].downloads[1].url,
            "https://www.taipower.com.tw/media/5586/113nian_hiring_answers.pdf",
        )

    def test_multi_session_year_has_month_in_exam_code(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML)
        year_107_entries = [e for e in entries if e.year_roc == 107]

        self.assertEqual(len(year_107_entries), 2)
        # Month attribute must be set for multi-session year entries
        self.assertIsNotNone(year_107_entries[0].month)
        self.assertIsNotNone(year_107_entries[1].month)

    def test_multi_session_year_detects_month_values(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML)
        year_107_entries = [e for e in entries if e.year_roc == 107]
        months = {e.month for e in year_107_entries}

        self.assertEqual(months, {5, 12})

    def test_single_session_year_has_no_month(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML)
        year_113_entry = next(e for e in entries if e.year_roc == 113)

        self.assertIsNone(year_113_entry.month)

    def test_parse_hiring_page_handles_single_file_entry(self) -> None:
        entries = parse_hiring_page(HIRING_PAGE_HTML_SINGLE_FILE)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].year_roc, 111)
        self.assertEqual(len(entries[0].downloads), 1)
        self.assertEqual(entries[0].downloads[0].label, "試題暨解答")

    def test_parse_hiring_page_handles_nested_divs(self) -> None:
        """Test that nested divs inside title and file sections don't break parsing."""
        entries = parse_hiring_page(HIRING_PAGE_HTML_NESTED_DIVS)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].year_roc, 114)
        self.assertEqual(entries[0].year_ad, 2025)
        self.assertEqual(len(entries[0].downloads), 2)
        self.assertEqual(entries[0].downloads[0].label, "試題")
        self.assertEqual(entries[0].downloads[1].label, "解答")
        self.assertIn("114年新進僱用人員甄試試題解答", entries[0].title)

    def test_parse_hiring_page_empty_html_returns_empty_list(self) -> None:
        entries = parse_hiring_page("<html><body></body></html>")

        self.assertEqual(entries, [])

    def test_fetch_exam_page_builds_source_exam_page(self) -> None:
        with patch.object(TaipowerRecruitClient, "_fetch_text", return_value=HIRING_PAGE_HTML):
            client = TaipowerRecruitClient()
            page = client.fetch_exam_page("taipower-recruit-113", 2024)

        self.assertEqual(page.provider_id, "taipower_recruit")
        self.assertEqual(page.source_exam_id, "taipower-recruit-113")
        self.assertEqual(page.year_ad, 2024)
        self.assertEqual(page.year_roc, 113)
        self.assertEqual(page.exam_name_raw, "113年新進僱用人員甄試試題解答")
        self.assertEqual(len(page.papers), 2)
        self.assertEqual({paper.category_raw for paper in page.papers}, {"台電新進僱用人員甄試"})

    def test_fetch_exam_page_multi_session_year(self) -> None:
        with patch.object(TaipowerRecruitClient, "_fetch_text", return_value=HIRING_PAGE_HTML):
            client = TaipowerRecruitClient()
            page = client.fetch_exam_page("taipower-recruit-107-12", 2018)

        self.assertEqual(page.source_exam_id, "taipower-recruit-107-12")
        self.assertEqual(page.year_roc, 107)

    def test_fetch_exam_page_assigns_question_and_answer_file_types(self) -> None:
        with patch.object(TaipowerRecruitClient, "_fetch_text", return_value=HIRING_PAGE_HTML):
            client = TaipowerRecruitClient()
            page = client.fetch_exam_page("taipower-recruit-113", 2024)

        file_types = {file_type for paper in page.papers for file_type in paper.files}
        self.assertIn("question", file_types)
        self.assertIn("answer", file_types)

    def test_discover_available_years_returns_sorted_descending(self) -> None:
        with patch.object(TaipowerRecruitClient, "_fetch_text", return_value=HIRING_PAGE_HTML):
            client = TaipowerRecruitClient()
            years = client.discover_available_years()

        self.assertEqual(years, [2024, 2023, 2018, 2017])

    def test_discover_exams_returns_exam_options_for_single_session_year(self) -> None:
        with patch.object(TaipowerRecruitClient, "_fetch_text", return_value=HIRING_PAGE_HTML):
            client = TaipowerRecruitClient()
            exams = client.discover_exams(2024)

        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0].code, "taipower-recruit-113")
        self.assertEqual(exams[0].year_ad, 2024)
        self.assertEqual(exams[0].year_roc, 113)

    def test_discover_exams_returns_two_options_for_multi_session_year(self) -> None:
        with patch.object(TaipowerRecruitClient, "_fetch_text", return_value=HIRING_PAGE_HTML):
            client = TaipowerRecruitClient()
            exams = client.discover_exams(2018)

        self.assertEqual(len(exams), 2)
        codes = {e.code for e in exams}
        self.assertIn("taipower-recruit-107-12", codes)
        self.assertIn("taipower-recruit-107-5", codes)

    def test_registry_returns_taipower_recruit_provider(self) -> None:
        from app.providers.registry import get_provider
        from app.providers.base import SourceProvider

        provider = get_provider("taipower_recruit")

        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "taipower_recruit")


if __name__ == "__main__":
    unittest.main()
