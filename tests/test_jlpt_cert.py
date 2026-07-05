"""Tests for the jlpt_cert provider."""

import unittest

from app.providers.jlpt_cert.client import JlptCertClient, parse_downloads


SAMPLE_HTML = """
<p><img src="img/book2018.gif" alt="JLPT Official Practice Workbook Vol. 2 (published 2018)" /></p>
<table>
<tr><th>N1</th>
<td><a href="../../samples/sample2018/pdf/N1V.pdf"><img alt="PDF" /></a></td>
<td><a href="../../samples/sample2018/pdf/N1answer.pdf"><img alt="PDF" /></a></td>
<td><a href="../../samples/sample2018/mp3/N1Q1.mp3">Q1<img alt="MP3" /></a></td>
</tr>
</table>
<p><img src="img/book2012.gif" alt="JLPT Official Practice Workbook (published 2012)" /></p>
<table>
<tr><th>N2</th>
<td><a href="../../samples/sample2012/pdf/N2L.pdf"><img alt="PDF" /></a></td>
<td><a href="../../samples/sample2017/mp3/N2Q2.mp3">Q2<img alt="MP3" /></a></td>
<td><a href="../../samples/sample2012/pdf/N2script.pdf"><img alt="PDF" /></a></td>
</tr>
</table>
"""


class JlptCertParserTests(unittest.TestCase):
    def test_parse_downloads_keeps_workbook_year_for_sample2017_audio_link(self) -> None:
        downloads = parse_downloads(SAMPLE_HTML, base_url="https://www.jlpt.jp/e/samples/sampleindex.html")

        self.assertEqual([download.year_ad for download in downloads], [2018, 2018, 2018, 2012, 2012, 2012])
        self.assertEqual(downloads[0].level_code, "n1")
        self.assertEqual(downloads[0].file_type, "question")
        self.assertEqual(downloads[1].file_type, "answer")
        self.assertEqual(downloads[2].file_type, "listening_audio")
        self.assertEqual(downloads[4].year_ad, 2012)
        self.assertTrue(downloads[4].url.endswith("/samples/sample2017/mp3/N2Q2.mp3"))
        self.assertEqual(downloads[5].file_type, "question_alt")


class JlptCertClientTests(unittest.TestCase):
    def test_fetch_exam_page_builds_papers_for_requested_workbook_year(self) -> None:
        client = JlptCertClient()
        client._fetch_text = lambda url: SAMPLE_HTML  # type: ignore[method-assign]

        self.assertEqual(client.discover_available_years(), [2018, 2012])
        self.assertEqual([exam.code for exam in client.discover_exams(2018)], ["jlpt-cert-practice-2018"])

        page = client.fetch_exam_page("jlpt-cert-practice-2012", 2012)

        self.assertEqual(page.provider_id, "jlpt_cert")
        self.assertEqual(page.source_exam_id, "jlpt-cert-practice-2012")
        self.assertEqual(len(page.papers), 3)
        self.assertIn("question", page.papers[0].files)
        self.assertIn("listening_audio", page.papers[1].files)
        self.assertEqual(len({paper.subject_code for paper in page.papers}), len(page.papers))


if __name__ == "__main__":
    unittest.main()
