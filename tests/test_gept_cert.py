"""Tests for the gept_cert provider."""

import unittest
from datetime import date
from unittest.mock import patch

from app.providers.gept_cert.client import GeptCertClient, parse_intro_downloads, parse_practice_audio


INTRO_HTML = """
<a href="../2022/geptpracticee.htm">練習題</a>
<a href="../2022/geptscoreremark/初級作文.pdf">※ 各級分範例 ※</a>
<a href="../WebFile/GEPTCBTPracticeTest.zip">點此下載</a>
"""

PRACTICE_HTML = """
<a href="javascript:playAudio('realplayer/el_web_1.mp3');">播放</a>
<a href="javascript:playAudio('realplayer/el_web_2.mp3');">播放</a>
"""


class GeptCertParserTests(unittest.TestCase):
    def test_parse_intro_downloads_extracts_pdf_zip_and_practice_page(self) -> None:
        downloads, practice_pages = parse_intro_downloads(
            INTRO_HTML,
            base_url="https://www.gept.org.tw/Exam_Intro/t01_introduction.asp",
            level_code="elementary",
        )

        self.assertEqual([download.file_type for download in downloads], ["question", "question"])
        self.assertTrue(downloads[0].url.endswith("%E5%88%9D%E7%B4%9A%E4%BD%9C%E6%96%87.pdf"))
        self.assertTrue(downloads[1].url.endswith("GEPTCBTPracticeTest.zip"))
        self.assertEqual(practice_pages, ["https://www.gept.org.tw/2022/geptpracticee.htm"])

    def test_parse_practice_audio_extracts_mp3_urls(self) -> None:
        downloads = parse_practice_audio(
            PRACTICE_HTML,
            base_url="https://www.gept.org.tw/2022/geptpracticee.htm",
            level_code="elementary",
        )

        self.assertEqual(len(downloads), 2)
        self.assertEqual(downloads[0].file_type, "listening_audio")
        self.assertTrue(downloads[0].url.endswith("realplayer/el_web_1.mp3"))


class GeptCertClientTests(unittest.TestCase):
    def test_materials_year_does_not_follow_runtime_calendar_year(self) -> None:
        class FutureDate:
            @classmethod
            def today(cls) -> date:
                return date(2027, 1, 1)

        with patch("app.providers.gept_cert.client.date", FutureDate, create=True):
            client = GeptCertClient()

            self.assertEqual(client.discover_available_years(), [2026])
            self.assertEqual([exam.year_ad for exam in client.discover_exams(2026)], [2026])
            self.assertEqual(client.discover_exams(2027), [])

    def test_fetch_exam_page_builds_download_papers(self) -> None:
        client = GeptCertClient()

        def fake_fetch(url: str) -> str:
            if url.endswith("geptpracticee.htm"):
                return PRACTICE_HTML
            return INTRO_HTML

        client._fetch_text = fake_fetch  # type: ignore[method-assign]
        client.LEVELS = (("elementary", "初級", "https://www.gept.org.tw/Exam_Intro/t01_introduction.asp"),)

        page = client.fetch_exam_page("gept-cert-materials", 2026)

        self.assertEqual(page.provider_id, "gept_cert")
        self.assertEqual(len(page.papers), 4)
        self.assertIn("listening_audio", page.papers[-1].files)


if __name__ == "__main__":
    unittest.main()
