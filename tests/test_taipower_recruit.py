import unittest
from unittest.mock import patch

from app.providers.taipower_recruit.client import TaipowerRecruitClient, _quote_url_for_request, parse_hiring_page


HIRING_PAGE_HTML = """
<html>
<head><title>台電下載專區</title></head>
<body>
<ul>
  <li>
    <p class="title">113年新進僱用人員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5585/113nian_hiring_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5586/113nian_hiring_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
  <li>
    <p class="title">112年新進僱用人員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5223/112nian_hiring_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5224/112nian_hiring_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
  <li>
    <p class="title">107年12月新進僱用人員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/3892/107dec_hiring_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/3893/107dec_hiring_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
  <li>
    <p class="title">107年5月新進僱用人員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/3790/107may_hiring_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/3791/107may_hiring_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
  <li>
    <p class="title">106年新進僱用人員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/3600/106nian_hiring_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/3601/106nian_hiring_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
</ul>
</body>
</html>
"""

HIRING_PAGE_HTML_SINGLE_FILE = """
<html><body>
<ul>
  <li>
    <p class="title">111年新進僱用人員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題暨解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/4992/111nian_hiring.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
</ul>
</body></html>
"""

HIRING_PAGE_HTML_NESTED_DIVS = """
<html><body>
<ul>
  <li>
    <p class="title"><span>Inner nested span</span> 114年新進僱用人員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5587/114nian_hiring_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5588/114nian_hiring_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
</ul>
</body></html>
"""

HIRING_PAGE_HTML_MULTI_SUBJECT = """
<html><body>
<ul>
  <li>
    <p class="title">112年度共同科目</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">共同科目試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/1001/common_q.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">共同科目解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/1002/common_a.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
  <li>
    <p class="title">112年度企業管理概論</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">企業管理概論試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/1003/biz_q.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">企業管理概論解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/1004/biz_a.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
</ul>
</body></html>
"""


class TaipowerRecruitParserTests(unittest.TestCase):
    def test_quote_url_for_request_percent_encodes_non_ascii_path_and_preserves_query(self) -> None:
        url = "https://www.taipower.com.tw/media/demo/115年度新進僱用人員甄試試題.pdf?mediaDL=true"

        quoted = _quote_url_for_request(url)

        self.assertEqual(
            quoted,
            "https://www.taipower.com.tw/media/demo/115%E5%B9%B4%E5%BA%A6%E6%96%B0%E9%80%B2%E5%83%B1%E7%94%A8%E4%BA%BA%E5%93%A1%E7%94%84%E8%A9%A6%E8%A9%A6%E9%A1%8C.pdf?mediaDL=true",
        )

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

    def test_discover_exams_deduplicates_multi_subject_entries(self) -> None:
        with patch.object(TaipowerRecruitClient, "_fetch_text", return_value=HIRING_PAGE_HTML_MULTI_SUBJECT):
            client = TaipowerRecruitClient()
            exams = client.discover_exams(2023)

        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0].code, "taipower-recruit-112")

    def test_fetch_exam_page_aggregates_multi_subject_entries(self) -> None:
        with patch.object(TaipowerRecruitClient, "_fetch_text", return_value=HIRING_PAGE_HTML_MULTI_SUBJECT):
            client = TaipowerRecruitClient()
            page = client.fetch_exam_page("taipower-recruit-112", 2023)

        self.assertEqual(len(page.papers), 4)
        urls = {url for paper in page.papers for url in paper.files.values()}
        self.assertEqual(len(urls), 4)
        codes = [paper.subject_code for paper in page.papers]
        self.assertEqual(codes, ["hiring-01", "hiring-02", "hiring-03", "hiring-04"])
        file_types = [ft for paper in page.papers for ft in paper.files]
        self.assertEqual(file_types, ["question", "answer", "question", "answer"])

    def test_registry_returns_taipower_recruit_provider(self) -> None:
        from app.providers.registry import get_provider
        from app.providers.base import SourceProvider

        provider = get_provider("taipower_recruit")

        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "taipower_recruit")


if __name__ == "__main__":
    unittest.main()
