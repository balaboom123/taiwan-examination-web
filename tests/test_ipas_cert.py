"""Tests for the ipas_cert provider."""

import unittest
from datetime import date
from unittest.mock import patch

from app.providers.ipas_cert.client import IpasCertClient, parse_certification_codes, parse_pdf_downloads


IPAS_HOME_HTML = """
<a href="/certification/ISE/news">資訊安全工程師</a>
<a href="https://www.ipas.org.tw/certification/AIAP/news">AI應用規劃師</a>
<a href="https://ipd.nat.gov.tw/ipas/certification/BIO/news">生技醫藥</a>
"""

IPAS_DOWNLOAD_HTML = """
<a href="https://www.ipas.org.tw/api/proxy/uploads/certification/ISE/115年度資訊安全工程師能力鑑定簡章.pdf">簡章</a>
<script>var x="https://www.ipas.org.tw/api/proxy/uploads/certification_attachment/a/iPAS疑義考題處理需知.pdf";</script>
"""

IPAS_LEARNING_RESOURCE_HTML = """
<section>歷屆考題</section>
<a href="/ipas/api/proxy/uploads/115-1公告試題_資訊安全管理概論.pdf">下載</a>
<a href="https://ipd.nat.gov.tw/ipas/api/proxy/uploads/iPAS經濟部產業人才能力鑑定_疑義考題處理需知.pdf">下載</a>
<a href="https://ipd.nat.gov.tw/ipas/api/proxy/uploads/iPAS經濟部產業人才能力鑑定_疑義考題處理需知.pdf">重複</a>
"""


class IpasCertParserTests(unittest.TestCase):
    def test_parse_certification_codes_extracts_codes_from_news_links(self) -> None:
        self.assertEqual(parse_certification_codes(IPAS_HOME_HTML), ["AIAP", "BIO", "ISE"])

    def test_parse_pdf_downloads_extracts_direct_pdf_refs(self) -> None:
        downloads = parse_pdf_downloads(IPAS_DOWNLOAD_HTML)

        self.assertEqual(len(downloads), 2)
        self.assertEqual(downloads[0].cert_code, "")
        self.assertIn("ipd.nat.gov.tw/ipas/api/proxy/uploads/", downloads[0].url)

    def test_parse_pdf_downloads_extracts_learning_resource_questions(self) -> None:
        downloads = parse_pdf_downloads(IPAS_LEARNING_RESOURCE_HTML, cert_code="ISE")

        labels = [download.label for download in downloads]
        self.assertEqual(len(downloads), 2)
        self.assertIn("115-1公告試題_資訊安全管理概論.pdf", labels)
        self.assertIn("iPAS經濟部產業人才能力鑑定_疑義考題處理需知.pdf", labels)
        self.assertTrue(all(download.cert_code == "ISE" for download in downloads))


class IpasCertClientTests(unittest.TestCase):
    def test_materials_year_does_not_follow_runtime_calendar_year(self) -> None:
        class FutureDate:
            @classmethod
            def today(cls) -> date:
                return date(2027, 1, 1)

        with patch("app.providers.ipas_cert.client.date", FutureDate, create=True):
            client = IpasCertClient()

            self.assertEqual(client.discover_available_years(), [2026])
            self.assertEqual([exam.year_ad for exam in client.discover_exams(2026)], [2026, 2026, 2026, 2026])
            self.assertEqual(client.discover_exams(2027), [])

    def test_discover_exams_returns_only_it_adjacent_codes(self) -> None:
        client = IpasCertClient()

        exams = client.discover_exams(2026)

        self.assertEqual(
            [exam.code for exam in exams],
            [
                "ipas-cert-ise-2026",
                "ipas-cert-oia-2026",
                "ipas-cert-aiap-2026",
                "ipas-cert-aiot-2026",
            ],
        )

    def test_fetch_exam_page_builds_download_papers(self) -> None:
        client = IpasCertClient()
        client._fetch_text = lambda url: IPAS_LEARNING_RESOURCE_HTML if url.endswith("/learning-resources") else IPAS_DOWNLOAD_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("ipas-cert-ise-2026", 2026)

        self.assertEqual(page.provider_id, "ipas_cert")
        self.assertEqual(page.source_exam_id, "ipas-cert-ise-2026")
        self.assertEqual(len(page.papers), 4)
        self.assertTrue(all(paper.category_code == "ise" for paper in page.papers))
        self.assertIn("question", page.papers[0].files)


if __name__ == "__main__":
    unittest.main()
