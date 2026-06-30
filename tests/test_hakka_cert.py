"""Tests for the hakka_cert provider."""

import unittest

from app.providers.hakka_cert.client import HakkaCertClient, parse_downloads


DOWNLOAD_HTML = """
<a href="/hakka/files/downloads/321.pdf">四縣 初級 題庫</a>
<a href="/hakka/files/downloads/324.pdf">四縣 初級 詞彙</a>
<a href="/hakka/files/downloads/322.zip">海陸 音檔</a>
<a href="/hakka/files/downloads/323.ods">詞彙表</a>
<a href="/hakka/files/downloads/321.pdf">duplicate</a>
"""


class HakkaCertParserTests(unittest.TestCase):
    def test_parse_downloads_keeps_public_pdf_assets_once_with_dialect_code(self) -> None:
        downloads = parse_downloads(DOWNLOAD_HTML)

        self.assertEqual(len(downloads), 2)
        self.assertEqual(downloads[0].category_code, "sixian")
        self.assertEqual(downloads[0].file_type, "question")
        self.assertTrue(downloads[0].url.endswith("/hakka/files/downloads/321.pdf"))
        self.assertEqual(downloads[1].category_code, "sixian")
        self.assertTrue(downloads[1].url.endswith("/hakka/files/downloads/324.pdf"))


class HakkaCertClientTests(unittest.TestCase):
    def test_discovery_uses_single_materials_exam(self) -> None:
        client = HakkaCertClient()

        self.assertEqual(client.discover_available_years(), [2026])
        self.assertEqual([exam.code for exam in client.discover_exams(2026)], ["hakka-cert-materials"])
        self.assertEqual(client.discover_exams(2027), [])

    def test_fetch_exam_page_builds_question_papers(self) -> None:
        client = HakkaCertClient()
        client._fetch_text = lambda url: DOWNLOAD_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("hakka-cert-materials", 2026)

        self.assertEqual(page.provider_id, "hakka_cert")
        self.assertEqual(page.exam_name_raw, "客語能力認證官方教材及試題")
        self.assertEqual(len(page.papers), 2)
        self.assertIn("question", page.papers[0].files)
        self.assertEqual(len({paper.subject_code for paper in page.papers}), len(page.papers))


if __name__ == "__main__":
    unittest.main()
