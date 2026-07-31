import unittest
from unittest.mock import patch

from app.providers.moea_recruit.client import (
    DISCOVERY_PAGE_SIZE,
    DOWNLOAD_URL,
    MoeaRecruitClient,
    _quote_url_for_request,
    parse_download_page,
)


DOWNLOAD_PAGE_HTML = """
<html>
<head><title>台電下載專區</title></head>
<body>
<ul>
  <li>
    <p class="title">113年新進職員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5485/113nian_examination_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5486/113nian_examination_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
  <li>
    <p class="title">112年新進職員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5123/112nian_examination_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5124/112nian_examination_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
  <li>
    <p class="title">111年新進職員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/4892/111nian_examination_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/4893/111nian_examination_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
</ul>
</body>
</html>
"""

DOWNLOAD_PAGE_HTML_SINGLE_FILE = """
<html><body>
<ul>
  <li>
    <p class="title">110年新進職員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題暨解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/4567/110nian_examination.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
</ul>
</body></html>
"""

DOWNLOAD_PAGE_HTML_NESTED_DIVS = """
<html><body>
<ul>
  <li>
    <p class="title"><span>Inner nested span</span> 114年新進職員甄試試題解答</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5487/114nian_examination_questions.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/5488/114nian_examination_answers.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
</ul>
</body></html>
"""

DOWNLOAD_PAGE_HTML_MULTI_SUBJECT = """
<html><body>
<ul>
  <li>
    <p class="title">112年度共同科目</p>
    <div class="drawerBox">
      <ul class="fileDownload">
        <li>
          <span class="name">共同科目試題</span>
          <ul class="downloadFiles">
            <li><a download href="/media/2001/common_q.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">共同科目解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/2002/common_a.pdf">下載</a></li>
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
            <li><a download href="/media/2003/biz_q.pdf">下載</a></li>
          </ul>
        </li>
        <li>
          <span class="name">企業管理概論解答</span>
          <ul class="downloadFiles">
            <li><a download href="/media/2004/biz_a.pdf">下載</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </li>
</ul>
</body></html>
"""


YEAR_TABS_HTML = """
<html><body>
<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4298">113年度</a>
<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4296">112年度</a>
<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4224">111年度</a>
</body></html>
"""


def _year_page_html(year_roc: int, *, next_page: bool = False) -> str:
    pagination = (
        f'<a href="?Page=2&amp;PageSize={DISCOVERY_PAGE_SIZE}&amp;q_attribute=4298">2</a>'
        if next_page
        else ""
    )
    return f"""
<html><body>
<ul><li>
  <p class="title">{year_roc}年度共同科目</p>
  <div class="drawerBox"><ul class="fileDownload">
    <li><span class="name">{year_roc}年度新進職員甄試試題科目_共同科目</span>
      <ul class="downloadFiles"><li><a download href="/media/{year_roc}/question.pdf">下載</a></li></ul>
    </li>
    <li><span class="name">{year_roc}年度新進職員甄試試題解答_共同科目</span>
      <ul class="downloadFiles"><li><a download href="/media/{year_roc}/answer.pdf">下載</a></li></ul>
    </li>
  </ul></div>
</li></ul>
{pagination}
</body></html>
"""


def _fake_archive_fetch(url: str) -> str:
    if url == DOWNLOAD_URL:
        return YEAR_TABS_HTML
    year_by_attribute = {"4298": 113, "4296": 112, "4224": 111}
    for attribute, year_roc in year_by_attribute.items():
        if f"q_attribute={attribute}" in url:
            if f"PageSize={DISCOVERY_PAGE_SIZE}" not in url:
                raise AssertionError(f"unbounded year URL: {url}")
            return _year_page_html(year_roc)
    raise AssertionError(f"unexpected URL: {url}")


class MoeaRecruitParserTests(unittest.TestCase):
    def test_quote_url_for_request_percent_encodes_non_ascii_path_and_preserves_query(self) -> None:
        url = "https://www.taipower.com.tw/media/demo/115年度新進職員甄試試題.pdf?mediaDL=true"

        quoted = _quote_url_for_request(url)

        self.assertEqual(
            quoted,
            "https://www.taipower.com.tw/media/demo/115%E5%B9%B4%E5%BA%A6%E6%96%B0%E9%80%B2%E8%81%B7%E5%93%A1%E7%94%84%E8%A9%A6%E8%A9%A6%E9%A1%8C.pdf?mediaDL=true",
        )

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
        entries = parse_download_page(DOWNLOAD_PAGE_HTML_NESTED_DIVS)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].year_roc, 114)
        self.assertEqual(entries[0].year_ad, 2025)
        self.assertEqual(len(entries[0].downloads), 2)
        self.assertEqual(entries[0].downloads[0].label, "試題")
        self.assertEqual(entries[0].downloads[1].label, "解答")
        self.assertIn("114年新進職員甄試試題解答", entries[0].title)

    def test_parse_download_page_empty_html_returns_empty_list(self) -> None:
        entries = parse_download_page("<html><body></body></html>")

        self.assertEqual(entries, [])

    def test_fetch_exam_page_builds_source_exam_page(self) -> None:
        with patch.object(
            MoeaRecruitClient,
            "_iter_entries",
            return_value=parse_download_page(DOWNLOAD_PAGE_HTML),
        ):
            client = MoeaRecruitClient()
            page = client.fetch_exam_page("moea-recruit-113", 2024)

        self.assertEqual(page.provider_id, "moea_recruit")
        self.assertEqual(page.source_exam_id, "moea-recruit-113")
        self.assertEqual(page.year_ad, 2024)
        self.assertEqual(page.year_roc, 113)
        self.assertEqual(page.exam_name_raw, "113年度經濟部所屬事業機構新進職員甄試")
        self.assertEqual(len(page.papers), 2)
        self.assertEqual({paper.category_raw for paper in page.papers}, {"國營事業聯招（新進職員）"})

    def test_fetch_exam_page_assigns_question_and_answer_file_types(self) -> None:
        with patch.object(
            MoeaRecruitClient,
            "_iter_entries",
            return_value=parse_download_page(DOWNLOAD_PAGE_HTML),
        ):
            client = MoeaRecruitClient()
            page = client.fetch_exam_page("moea-recruit-113", 2024)

        file_types = {file_type for paper in page.papers for file_type in paper.files}
        self.assertIn("question", file_types)
        self.assertIn("answer", file_types)

    def test_discover_available_years_returns_sorted_descending(self) -> None:
        with patch.object(
            MoeaRecruitClient,
            "_iter_entries",
            return_value=parse_download_page(DOWNLOAD_PAGE_HTML),
        ):
            client = MoeaRecruitClient()
            years = client.discover_available_years()

        self.assertEqual(years, [2024, 2023, 2022])

    def test_discover_exams_returns_exam_options_for_year(self) -> None:
        with patch.object(
            MoeaRecruitClient,
            "_iter_entries",
            return_value=parse_download_page(DOWNLOAD_PAGE_HTML),
        ):
            client = MoeaRecruitClient()
            exams = client.discover_exams(2024)

        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0].code, "moea-recruit-113")
        self.assertEqual(exams[0].year_ad, 2024)
        self.assertEqual(exams[0].year_roc, 113)
        self.assertEqual(exams[0].label, "113年度經濟部所屬事業機構新進職員甄試")

    def test_discover_exams_deduplicates_multi_subject_entries(self) -> None:
        with patch.object(
            MoeaRecruitClient,
            "_iter_entries",
            return_value=parse_download_page(DOWNLOAD_PAGE_HTML_MULTI_SUBJECT),
        ):
            client = MoeaRecruitClient()
            exams = client.discover_exams(2023)

        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0].code, "moea-recruit-112")

    def test_fetch_exam_page_aggregates_multi_subject_entries(self) -> None:
        with patch.object(
            MoeaRecruitClient,
            "_iter_entries",
            return_value=parse_download_page(DOWNLOAD_PAGE_HTML_MULTI_SUBJECT),
        ):
            client = MoeaRecruitClient()
            page = client.fetch_exam_page("moea-recruit-112", 2023)

        self.assertEqual(len(page.papers), 4)
        urls = {url for paper in page.papers for url in paper.files.values()}
        self.assertEqual(len(urls), 4)
        codes = [paper.subject_code for paper in page.papers]
        self.assertEqual(codes, ["joint-01", "joint-02", "joint-03", "joint-04"])
        file_types = [ft for paper in page.papers for ft in paper.files]
        self.assertEqual(file_types, ["question", "answer", "question", "answer"])

    def test_archive_discovery_fetches_every_year_at_bounded_page_size(self) -> None:
        with patch.object(
            MoeaRecruitClient,
            "_fetch_text",
            side_effect=_fake_archive_fetch,
        ) as fetch:
            client = MoeaRecruitClient()
            years = client.discover_available_years()
            year_url = client.build_discovery_year_url(2024)
            exam_url = client.build_discovery_exam_url("moea-recruit-113", 2024)
            page = client.fetch_exam_page("moea-recruit-113", 2024)

        self.assertEqual(years, [2024, 2023, 2022])
        self.assertEqual(
            year_url,
            "https://www.taipower.com.tw/2289/2544/2554/2556/"
            "?Page=1&PageSize=200&q_attribute=4298",
        )
        self.assertEqual(exam_url, year_url)
        self.assertEqual(len(page.papers), 2)
        self.assertEqual(fetch.call_count, 4)

    def test_archive_discovery_rejects_missing_year_tabs(self) -> None:
        with patch.object(MoeaRecruitClient, "_fetch_text", return_value="<html></html>"):
            with self.assertRaisesRegex(ValueError, "no official year tabs"):
                MoeaRecruitClient().discover_available_years()

    def test_archive_discovery_rejects_residual_pagination(self) -> None:
        one_tab = YEAR_TABS_HTML.replace(
            '<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4296">112年度</a>',
            "",
        ).replace(
            '<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4224">111年度</a>',
            "",
        )

        def fake_fetch(url: str) -> str:
            return one_tab if url == DOWNLOAD_URL else _year_page_html(113, next_page=True)

        with patch.object(MoeaRecruitClient, "_fetch_text", side_effect=fake_fetch):
            with self.assertRaisesRegex(ValueError, "still paginates"):
                MoeaRecruitClient().discover_available_years()

    def test_archive_discovery_rejects_duplicate_asset_urls(self) -> None:
        one_tab = YEAR_TABS_HTML.replace(
            '<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4296">112年度</a>',
            "",
        ).replace(
            '<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4224">111年度</a>',
            "",
        )

        def fake_fetch(url: str) -> str:
            if url == DOWNLOAD_URL:
                return one_tab
            return _year_page_html(113).replace(
                "/media/113/answer.pdf",
                "/media/113/question.pdf",
            )

        with patch.object(MoeaRecruitClient, "_fetch_text", side_effect=fake_fetch):
            with self.assertRaisesRegex(ValueError, "repeats download URL"):
                MoeaRecruitClient().discover_available_years()

    def test_archive_discovery_rejects_cross_year_entries(self) -> None:
        one_tab = YEAR_TABS_HTML.replace(
            '<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4296">112年度</a>',
            "",
        ).replace(
            '<a href="/2289/2544/2554/2556/?Page=1&amp;PageSize=10&amp;q_attribute=4224">111年度</a>',
            "",
        )

        def fake_fetch(url: str) -> str:
            return one_tab if url == DOWNLOAD_URL else _year_page_html(112)

        with patch.object(MoeaRecruitClient, "_fetch_text", side_effect=fake_fetch):
            with self.assertRaisesRegex(ValueError, "cross-year entries"):
                MoeaRecruitClient().discover_available_years()

    def test_discovery_urls_reject_unknown_year_and_exam(self) -> None:
        with patch.object(MoeaRecruitClient, "_fetch_text", side_effect=_fake_archive_fetch):
            client = MoeaRecruitClient()
            with self.assertRaisesRegex(ValueError, "Unknown MOEA recruitment discovery year"):
                client.build_discovery_year_url(2025)
            with self.assertRaisesRegex(ValueError, "Unknown MOEA recruitment discovery exam"):
                client.build_discovery_exam_url("moea-recruit-112", 2024)

    def test_registry_returns_moea_recruit_provider(self) -> None:
        from app.providers.registry import get_provider
        from app.providers.base import SourceProvider

        provider = get_provider("moea_recruit")

        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "moea_recruit")


if __name__ == "__main__":
    unittest.main()
