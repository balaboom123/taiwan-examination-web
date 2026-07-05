"""Tests for the tocfl_cert provider."""

import unittest
from datetime import date
from unittest.mock import patch

from app.providers.tocfl_cert.client import TocflCertClient, parse_downloads


TOCFL_DOWNLOAD_HTML = """
<a href="/tocfl/assets/files/vocabulary/8000zhuyin_202409.zip">華語八千詞表</a>
<a href="/tocfl/assets/files/vocabulary/8000_description_202204.pdf">華語八千詞表調整說明</a>
<a href="/tocfl/assets/files/vocabulary/CCCC_Vocabulary_2022.xls">兒童華語文能力測驗情境詞彙表</a>
"""

TOCFL_MOCK_HTML = """
<div class="section-title-NoB">聽力</div>
<div class="subsection-title-NoB">第一部分</div>
<div class="link-NoB">
  <a href="https://tocfl.edu.tw/tocfl/assets/files/mock_database/N_L_Part%20One_T.rar">[正體試題]</a>
  <a href="https://tocfl.edu.tw/tocfl/assets/files/mock_database/N_L_Part%20One_S.rar">[簡體試題]</a>
  <a href="https://tocfl.edu.tw/tocfl/assets/files/mock_database/N_L_Part%20One_MP3.rar">[音檔]</a>
  <a href="https://tocfl.edu.tw/tocfl/assets/files/mock_database/N_L_Part%20One_Answer.xlsx">[答案]</a>
  <a href="https://tocfl.edu.tw/tocfl/assets/files/mock_database/N_L_Part%20One_Listening%20Script.rar">[聽力腳本]</a>
</div>
"""


class TocflCertParserTests(unittest.TestCase):
    def test_parse_downloads_extracts_official_pdf_and_zip_assets(self) -> None:
        downloads = parse_downloads(TOCFL_DOWNLOAD_HTML, base_url="https://tocfl.edu.tw/tocfl/index.php/exam/download")

        self.assertEqual(len(downloads), 3)
        self.assertEqual(downloads[0].label, "華語八千詞表")
        self.assertTrue(downloads[0].url.endswith("8000zhuyin_202409.zip"))
        self.assertTrue(downloads[1].url.endswith("8000_description_202204.pdf"))
        self.assertTrue(downloads[2].url.endswith("CCCC_Vocabulary_2022.xls"))

    def test_parse_downloads_classifies_mock_test_assets(self) -> None:
        downloads = parse_downloads(TOCFL_MOCK_HTML, base_url="https://tocfl.edu.tw/tocfl/index.php/exam/test/page/1")

        self.assertEqual([download.file_type for download in downloads], ["question", "question", "listening_audio", "answer", "question_alt"])
        self.assertEqual(len({download.label for download in downloads}), 5)
        self.assertTrue(downloads[0].label.startswith("N L Part One T"))


class TocflCertClientTests(unittest.TestCase):
    def test_material_years_come_from_source_filenames_not_runtime_calendar_year(self) -> None:
        class FutureDate:
            @classmethod
            def today(cls) -> date:
                return date(2027, 1, 1)

        with patch("app.providers.tocfl_cert.client.date", FutureDate, create=True):
            client = TocflCertClient()
            client._fetch_text = lambda url: TOCFL_DOWNLOAD_HTML  # type: ignore[method-assign]

            self.assertEqual(client.discover_available_years(), [2024, 2022])
            self.assertEqual([exam.year_ad for exam in client.discover_exams(2024)], [2024])
            self.assertEqual(client.discover_exams(2027), [])

    def test_discovery_uses_years_embedded_in_official_filenames(self) -> None:
        client = TocflCertClient()
        client._fetch_text = lambda url: TOCFL_DOWNLOAD_HTML  # type: ignore[method-assign]

        self.assertEqual(client.discover_available_years(), [2024, 2022])
        self.assertEqual([exam.code for exam in client.discover_exams(2024)], ["tocfl-cert-2024"])

    def test_fetch_exam_page_filters_tocfl_by_filename_year(self) -> None:
        client = TocflCertClient()
        client._fetch_text = lambda url: TOCFL_DOWNLOAD_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("tocfl-cert-2022", 2022)

        self.assertEqual(page.source_exam_id, "tocfl-cert-2022")
        self.assertEqual({paper.subject_name_raw for paper in page.papers}, {"華語八千詞表調整說明", "兒童華語文能力測驗情境詞彙表"})

    def test_fetch_exam_page_builds_reference_material_papers(self) -> None:
        client = TocflCertClient()
        client._fetch_text = lambda url: TOCFL_DOWNLOAD_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("tocfl-cert-materials", 2026)

        self.assertEqual(page.provider_id, "tocfl_cert")
        self.assertEqual(len(page.papers), 3)
        self.assertIn("question", page.papers[0].files)

    def test_fetch_exam_page_uses_unique_subject_codes_for_chinese_labels(self) -> None:
        client = TocflCertClient()
        client._fetch_text = lambda url: TOCFL_DOWNLOAD_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("tocfl-cert-materials", 2026)

        self.assertEqual(len({paper.subject_code for paper in page.papers}), 3)


if __name__ == "__main__":
    unittest.main()
