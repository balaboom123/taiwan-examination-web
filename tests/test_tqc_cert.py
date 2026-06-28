"""Tests for the tqc_cert provider."""

import unittest

from app.providers.tqc_cert.client import TqcCertClient, parse_exam_papers


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


class TqcCertParserTests(unittest.TestCase):
    def test_parse_exam_papers_extracts_labels_dates_and_urls(self) -> None:
        entries = parse_exam_papers(TQC_EXAM_PAPER_HTML)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].title, "資訊科技Python")
        self.assertEqual(entries[0].category, "專業知識領域類")
        self.assertEqual(entries[0].published_year, 2020)
        self.assertTrue(entries[0].url.endswith("F7647750.pdf"))


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


if __name__ == "__main__":
    unittest.main()
