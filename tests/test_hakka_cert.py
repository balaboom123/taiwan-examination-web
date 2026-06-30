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

PAGED_BASIC_HTML = """
<a href="/hakka/files/downloads/527.pdf">114 年度客語能力認證基礎級暨初級題庫 ( 四縣腔 ) PDF 下載</a>
<a href="/hakka/download-files?c=2&page=2">2</a>
"""

PAGED_BASIC_HTML_PAGE_2 = """
<a href="/hakka/files/downloads/352.pdf">112 年度客語能力認證基礎級暨初級題庫 ( 四縣腔 ) PDF 下載</a>
"""

PAGED_INTERMEDIATE_HTML = """
<a href="/hakka/files/downloads/548.pdf">114 年度客語能力認證中級暨中高級詞彙（海陸腔-上）PDF 下載</a>
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
    def test_discovery_uses_material_year_for_labels_without_year(self) -> None:
        client = HakkaCertClient()

        def fake_fetch(url: str) -> str:
            if "c=3" in url or "c=5" in url:
                return ""
            return DOWNLOAD_HTML

        client._fetch_text = fake_fetch  # type: ignore[method-assign]

        self.assertEqual(client.discover_available_years(), [2026])
        self.assertEqual([exam.code for exam in client.discover_exams(2026)], ["hakka-cert-basic-elementary-2026"])
        self.assertEqual(client.discover_exams(2027), [])

    def test_discovery_uses_official_level_category_and_label_years(self) -> None:
        client = HakkaCertClient()

        def fake_fetch(url: str) -> str:
            if "page=2" in url:
                return PAGED_BASIC_HTML_PAGE_2
            if "c=3" in url:
                return PAGED_INTERMEDIATE_HTML
            if "c=5" in url:
                return ""
            return PAGED_BASIC_HTML

        client._fetch_text = fake_fetch  # type: ignore[method-assign]

        self.assertEqual(client.discover_available_years(), [2025, 2023])
        self.assertEqual(
            [exam.code for exam in client.discover_exams(2025)],
            ["hakka-cert-basic-elementary-2025", "hakka-cert-intermediate-high-intermediate-2025"],
        )

    def test_fetch_exam_page_filters_hakka_by_level_category_and_year(self) -> None:
        client = HakkaCertClient()

        def fake_fetch(url: str) -> str:
            if "page=2" in url:
                return PAGED_BASIC_HTML_PAGE_2
            if "c=3" in url:
                return PAGED_INTERMEDIATE_HTML
            if "c=5" in url:
                return ""
            return PAGED_BASIC_HTML

        client._fetch_text = fake_fetch  # type: ignore[method-assign]

        page = client.fetch_exam_page("hakka-cert-basic-elementary-2023", 2023)

        self.assertEqual(page.source_exam_id, "hakka-cert-basic-elementary-2023")
        self.assertEqual(len(page.papers), 1)
        self.assertEqual(page.papers[0].subject_name_raw, "112 年度客語能力認證基礎級暨初級題庫 ( 四縣腔 ) PDF 下載")

    def test_fetch_exam_page_builds_question_papers(self) -> None:
        client = HakkaCertClient()
        client._fetch_text = lambda url: "" if "c=3" in url or "c=5" in url else DOWNLOAD_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("hakka-cert-basic-elementary-2026", 2026)

        self.assertEqual(page.provider_id, "hakka_cert")
        self.assertEqual(page.exam_name_raw, "客語能力認證官方教材及試題 基礎級暨初級")
        self.assertEqual(len(page.papers), 2)
        self.assertIn("question", page.papers[0].files)
        self.assertEqual(len({paper.subject_code for paper in page.papers}), len(page.papers))


if __name__ == "__main__":
    unittest.main()
