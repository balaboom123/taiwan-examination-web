"""Tests for the taigi_cert provider."""

import unittest

from app.providers.taigi_cert.client import TaigiCertClient, parse_downloads


RESOURCE_HTML = """
<a href="/tmt/src/upload/file/file_1.pdf">A卷 閱讀</a>
<a href="/tmt/src/upload/file/file_6.pdf">A卷 答案</a>
<a href="https://ttg.moe.edu.tw/tmt/src/upload/file/file_2.mp3">A卷 聽力</a>
<a href="/tmt/src/upload/file/file_3.zip">B卷 全部</a>
<a href="https://language.moe.gov.tw/resource.pdf">external guide</a>
<a href="/tmt/src/upload/file/file_1.pdf">duplicate</a>
"""


class TaigiCertParserTests(unittest.TestCase):
    def test_parse_downloads_keeps_official_pdf_mp3_and_zip_assets(self) -> None:
        downloads = parse_downloads(RESOURCE_HTML)

        self.assertEqual([download.file_type for download in downloads], ["question", "question", "listening_audio", "question"])
        self.assertTrue(all(download.url.startswith("https://ttg.moe.edu.tw/") for download in downloads))
        self.assertTrue(downloads[0].url.endswith("/file_1.pdf"))
        self.assertTrue(downloads[1].url.endswith("/file_6.pdf"))
        self.assertTrue(downloads[2].url.endswith("/file_2.mp3"))
        self.assertTrue(downloads[3].url.endswith("/file_3.zip"))


class TaigiCertClientTests(unittest.TestCase):
    def test_discovery_uses_single_materials_exam(self) -> None:
        client = TaigiCertClient()

        self.assertEqual(client.discover_available_years(), [2026])
        self.assertEqual([exam.code for exam in client.discover_exams(2026)], ["taigi-cert-materials"])
        self.assertEqual(client.discover_exams(2027), [])

    def test_fetch_exam_page_builds_download_papers(self) -> None:
        client = TaigiCertClient()
        client._fetch_text = lambda url: RESOURCE_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("taigi-cert-materials", 2026)

        self.assertEqual(page.provider_id, "taigi_cert")
        self.assertEqual(page.exam_name_raw, "臺灣台語語言能力認證官方試題範例")
        self.assertEqual(len(page.papers), 4)
        self.assertIn("listening_audio", page.papers[2].files)
        self.assertEqual(len({paper.subject_code for paper in page.papers}), len(page.papers))


if __name__ == "__main__":
    unittest.main()
