"""Tests for the ipas_cert provider."""

import unittest
from datetime import date
from unittest.mock import patch

from app.providers.ipas_cert.client import IpasCertClient, parse_certification_codes, parse_pdf_downloads


IPAS_HOME_HTML = """
<a href="/certification/ISE/news">資訊安全工程師</a>
<a href="https://www.ipas.org.tw/certification/AIAP/news">AI應用規劃師</a>
"""

IPAS_DOWNLOAD_HTML = """
<a href="https://www.ipas.org.tw/api/proxy/uploads/certification/ISE/115年度資訊安全工程師能力鑑定簡章.pdf">簡章</a>
<script>var x="https://www.ipas.org.tw/api/proxy/uploads/certification_attachment/a/iPAS疑義考題處理需知.pdf";</script>
"""


class IpasCertParserTests(unittest.TestCase):
    def test_parse_certification_codes_extracts_codes_from_news_links(self) -> None:
        self.assertEqual(parse_certification_codes(IPAS_HOME_HTML), ["AIAP", "ISE"])

    def test_parse_pdf_downloads_extracts_direct_pdf_refs(self) -> None:
        downloads = parse_pdf_downloads(IPAS_DOWNLOAD_HTML)

        self.assertEqual(len(downloads), 2)
        self.assertTrue(downloads[0].url.endswith(".pdf"))


class IpasCertClientTests(unittest.TestCase):
    def test_materials_year_does_not_follow_runtime_calendar_year(self) -> None:
        class FutureDate:
            @classmethod
            def today(cls) -> date:
                return date(2027, 1, 1)

        with patch("app.providers.ipas_cert.client.date", FutureDate, create=True):
            client = IpasCertClient()

            self.assertEqual(client.discover_available_years(), [2026])
            self.assertEqual([exam.year_ad for exam in client.discover_exams(2026)], [2026])
            self.assertEqual(client.discover_exams(2027), [])

    def test_fetch_exam_page_builds_download_papers(self) -> None:
        client = IpasCertClient()
        client._fetch_text = lambda url: IPAS_HOME_HTML if url == client.HOME_URL else IPAS_DOWNLOAD_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("ipas-cert-downloads", 2026)

        self.assertEqual(page.provider_id, "ipas_cert")
        self.assertEqual(len(page.papers), 4)
        self.assertIn("question", page.papers[0].files)


if __name__ == "__main__":
    unittest.main()
