"""Tests for the tocfl_cert provider."""

import unittest
from datetime import date
from unittest.mock import patch

from app.providers.tocfl_cert.client import TocflCertClient, parse_downloads


TOCFL_DOWNLOAD_HTML = """
<a href="/tocfl/assets/files/vocabulary/8000zhuyin_202409.zip">華語八千詞表</a>
<a href="/tocfl/assets/files/vocabulary/8000_description_202204.pdf">華語八千詞表調整說明</a>
"""


class TocflCertParserTests(unittest.TestCase):
    def test_parse_downloads_extracts_official_pdf_and_zip_assets(self) -> None:
        downloads = parse_downloads(TOCFL_DOWNLOAD_HTML, base_url="https://tocfl.edu.tw/tocfl/index.php/exam/download")

        self.assertEqual(len(downloads), 2)
        self.assertEqual(downloads[0].label, "華語八千詞表")
        self.assertTrue(downloads[0].url.endswith("8000zhuyin_202409.zip"))
        self.assertTrue(downloads[1].url.endswith("8000_description_202204.pdf"))


class TocflCertClientTests(unittest.TestCase):
    def test_materials_year_does_not_follow_runtime_calendar_year(self) -> None:
        class FutureDate:
            @classmethod
            def today(cls) -> date:
                return date(2027, 1, 1)

        with patch("app.providers.tocfl_cert.client.date", FutureDate, create=True):
            client = TocflCertClient()

            self.assertEqual(client.discover_available_years(), [2026])
            self.assertEqual([exam.year_ad for exam in client.discover_exams(2026)], [2026])
            self.assertEqual(client.discover_exams(2027), [])

    def test_fetch_exam_page_builds_reference_material_papers(self) -> None:
        client = TocflCertClient()
        client._fetch_text = lambda url: TOCFL_DOWNLOAD_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("tocfl-cert-materials", 2026)

        self.assertEqual(page.provider_id, "tocfl_cert")
        self.assertEqual(len(page.papers), 2)
        self.assertIn("question", page.papers[0].files)


if __name__ == "__main__":
    unittest.main()
