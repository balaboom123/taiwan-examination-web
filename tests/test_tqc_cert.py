"""Tests for the tqc_cert provider."""

import unittest

from app.providers.tqc_cert.client import TqcCertClient, parse_exam_papers, parse_page_requests


TQC_EXAM_PAPER_HTML = """
<table>
  <tr>
    <td>資訊科技Python</td>
    <td>專業知識領域類</td>
    <td>2020/08/13</td>
    <td><a href="http://www.tqc.org.tw/user/Example/F7647750.pdf">範例試卷下載</a></td>
  </tr>
  <tr>
    <td>電子商務與AI應用</td>
    <td>專業知識領域類</td>
    <td>2026/06/09</td>
    <td><a href="http://www.tqc.org.tw/user/Example/6ACCBC4A.pdf">範例試卷下載</a></td>
  </tr>
</table>
"""

TQC_PAGED_EXAM_PAPER_HTML = """
<input type="hidden" name="__VIEWSTATE" value="state" />
<table>
  <tr>
    <td>資訊科技Python</td>
    <td>專業知識領域類</td>
    <td>2020/08/13</td>
    <td><a href="../user/Example/python.pdf">範例試卷下載</a></td>
  </tr>
</table>
<a href="Download.aspx">下載專區</a>
<a href="javascript:__doPostBack('pager','Page$2')">2</a>
"""

TQC_SECOND_PAGE_HTML = """
<table>
  <tr>
    <td>資料庫應用</td>
    <td>資料庫應用類</td>
    <td>2021/09/01</td>
    <td><a href="../user/Example/database.pdf">範例試卷下載</a></td>
  </tr>
</table>
"""


class TqcCertParserTests(unittest.TestCase):
    def test_parse_exam_papers_extracts_labels_dates_and_urls(self) -> None:
        entries = parse_exam_papers(TQC_EXAM_PAPER_HTML)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].title, "資訊科技Python")
        self.assertEqual(entries[0].category, "專業知識領域類")
        self.assertEqual(entries[0].published_year, 2020)
        self.assertTrue(entries[0].url.endswith("F7647750.pdf"))

    def test_parse_exam_papers_keeps_only_sample_pdfs(self) -> None:
        papers = parse_exam_papers(TQC_PAGED_EXAM_PAPER_HTML)

        self.assertEqual([paper.title for paper in papers], ["資訊科技Python"])
        self.assertEqual(papers[0].category, "專業知識領域類")
        self.assertEqual(papers[0].published_year, 2020)
        self.assertTrue(papers[0].url.endswith("/user/Example/python.pdf"))

    def test_parse_exam_papers_rejects_off_domain_sample_pdfs(self) -> None:
        html = """
        <table>
          <tr>
            <td>偽造試卷</td>
            <td>專業知識領域類</td>
            <td>2026/06/09</td>
            <td><a href="https://example.com/user/Example/fake.pdf">範例試卷下載</a></td>
          </tr>
        </table>
        """

        self.assertEqual(parse_exam_papers(html), [])

    def test_parse_page_requests_extracts_postback_pagers(self) -> None:
        requests = parse_page_requests(TQC_PAGED_EXAM_PAPER_HTML)

        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].event_target, "pager")
        self.assertEqual(requests[0].event_argument, "Page$2")

    def test_parse_page_requests_rejects_off_domain_exam_paper_pages(self) -> None:
        html = '<a href="https://example.com/TQCNet/ExamPaper.aspx">2</a>'

        self.assertEqual(parse_page_requests(html), [])


class TqcCertClientTests(unittest.TestCase):
    def test_discovery_uses_published_years_from_sample_rows(self) -> None:
        client = TqcCertClient()
        client._fetch_text = lambda url: TQC_EXAM_PAPER_HTML  # type: ignore[method-assign]

        self.assertEqual(client.discover_available_years(), [2026, 2020])
        self.assertEqual([exam.code for exam in client.discover_exams(2020)], ["tqc-cert-samples-2020"])

    def test_fetch_exam_page_builds_question_papers(self) -> None:
        client = TqcCertClient()
        client._fetch_text = lambda url: TQC_EXAM_PAPER_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("tqc-cert-samples-2026", 2026)

        self.assertEqual(page.provider_id, "tqc_cert")
        self.assertEqual(len(page.papers), 1)
        self.assertEqual(page.papers[0].subject_name_raw, "電子商務與AI應用")
        self.assertIn("question", page.papers[0].files)

    def test_entries_fetches_paginated_sample_rows_once(self) -> None:
        client = TqcCertClient()
        calls: list[tuple[str, dict[str, str] | None]] = []

        def fake_fetch(url: str, form: dict[str, str] | None = None) -> str:
            calls.append((url, form))
            return TQC_SECOND_PAGE_HTML if form else TQC_PAGED_EXAM_PAPER_HTML

        client._fetch_text = fake_fetch  # type: ignore[method-assign]

        self.assertEqual(client.discover_available_years(), [2021, 2020])
        self.assertEqual(calls[1][1]["__EVENTTARGET"], "pager")  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()
