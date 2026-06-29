"""Tests for the teacher_recruit_taipei_junior provider."""

import unittest

from app.providers.teacher_recruit_taipei_junior.client import (
    TaipeiJuniorRecruitClient,
    parse_downloads,
)


ARTICLE_HTML = """
<html>
  <body>
    <h1>公告114學年度市立國民中學正式教師聯合甄選 各類科初試試題、答案及試題答案疑義表</h1>
    <a href="https://www-ws.gov.taipei/Download.ashx?u=question-token&n=5ZyL5paH6Kmm6aGMLnBkZg%3d%3d&icon=..pdf">pdf(569.23 KB)</a>
    <a href="https://www-ws.gov.taipei/Download.ashx?u=answer-token&n=5ZyL5paH562U5qGILnBkZg%3d%3d&icon=..pdf">pdf(72.66 KB)</a>
    <a href="https://www-ws.gov.taipei/Download.ashx?u=appeal-token&n=6Kmm6aGM562U5qGI55aR576p6KGoLm9kdA%3d%3d&icon=..odt">odt(9.44 KB)</a>
  </body>
</html>
"""


class TaipeiJuniorRecruitParserTests(unittest.TestCase):
    def test_parse_downloads_decodes_official_question_and_answer_pdfs(self) -> None:
        downloads = parse_downloads(ARTICLE_HTML, page_url="https://www.doe.gov.taipei/News_Content.aspx?s=example")

        self.assertEqual([download.file_type for download in downloads], ["question", "answer"])
        self.assertEqual([download.subject_name for download in downloads], ["國文", "國文"])
        self.assertEqual(downloads[0].url, "https://www-ws.gov.taipei/Download.ashx?u=question-token&n=5ZyL5paH6Kmm6aGMLnBkZg%3d%3d&icon=..pdf")


class TaipeiJuniorRecruitClientTests(unittest.TestCase):
    def test_fetch_exam_page_builds_subject_paper_pairs(self) -> None:
        client = TaipeiJuniorRecruitClient(article_html_by_year={2025: ARTICLE_HTML})

        page = client.fetch_exam_page("teacher-recruit-taipei-junior-114", 2025)

        self.assertEqual(page.provider_id, "teacher_recruit_taipei_junior")
        self.assertEqual(page.source_exam_id, "teacher-recruit-taipei-junior-114")
        self.assertEqual(page.exam_name_raw, "114學年度臺北市國中教師甄試")
        self.assertEqual(len(page.papers), 1)
        self.assertEqual(page.papers[0].category_raw, "臺北市國中教師甄試")
        self.assertEqual(page.papers[0].subject_code, "guo-wen")
        self.assertEqual(page.papers[0].subject_name_raw, "國文")
        self.assertEqual(
            page.papers[0].files,
            {
                "question": "https://www-ws.gov.taipei/Download.ashx?u=question-token&n=5ZyL5paH6Kmm6aGMLnBkZg%3d%3d&icon=..pdf",
                "answer": "https://www-ws.gov.taipei/Download.ashx?u=answer-token&n=5ZyL5paH562U5qGILnBkZg%3d%3d&icon=..pdf",
            },
        )

    def test_discover_years_uses_official_article_map(self) -> None:
        client = TaipeiJuniorRecruitClient(article_html_by_year={2025: ARTICLE_HTML, 2024: ARTICLE_HTML})

        self.assertEqual(client.discover_available_years(), [2025, 2024])
        self.assertEqual(client.discover_exams(2025)[0].code, "teacher-recruit-taipei-junior-114")


if __name__ == "__main__":
    unittest.main()
