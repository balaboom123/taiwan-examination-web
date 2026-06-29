"""Tests for the teacher_recruit_tainan provider."""

import unittest

from app.providers.teacher_recruit_tainan.client import (
    TainanTeacherRecruitClient,
    parse_announcement_links,
    parse_available_years,
    parse_downloads,
)


LISTING_HTML = """
<html>
  <h1><span id="lblTitle">臺南市115學年度市立國民小學教師暨學前特教師聯合甄選</span></h1>
  <table>
    <tr><td><a href="view.aspx?id=10">公告甄選試題正確答案</a></td></tr>
    <tr><td><a href="view.aspx?id=9">公告複試試教題目</a></td></tr>
    <tr><td><a href="view.aspx?id=8">公告甄選試題及參考答案</a></td></tr>
    <tr><td><a href="view.aspx?id=1">公告簡章及臺南文史題庫</a></td></tr>
  </table>
</html>
"""


DETAIL_HTML = """
<html>
  <body>
    <a href="Default.aspx">首頁</a>
    <a href="./upload/TrJh70115學年度市立國民小學教師暨學前特教師聯合甄選試題.zip">
      TrJh70115學年度市立國民小學教師暨學前特教師聯合甄選試題.zip
    </a>
    <a href="./upload/TrJh71115學年度市立國民小學教師暨學前特教師聯合甄選試題參考答案.zip">
      TrJh71115學年度市立國民小學教師暨學前特教師聯合甄選試題參考答案.zip
    </a>
  </body>
</html>
"""


CORRECTED_DETAIL_HTML = """
<html>
  <body>
    <a href="./upload/TrJh90115學年度市立國民小學教師暨學前特教師聯合甄選試題答案.zip">
      TrJh90115學年度市立國民小學教師暨學前特教師聯合甄選試題答案.zip
    </a>
  </body>
</html>
"""


class TainanTeacherRecruitParserTests(unittest.TestCase):
    def test_parse_available_years_from_current_school_year_title(self) -> None:
        self.assertEqual(parse_available_years(LISTING_HTML), [2026])

    def test_parse_announcement_links_keeps_question_and_answer_notices(self) -> None:
        links = parse_announcement_links(
            LISTING_HTML,
            page_url="https://qualify.tn.edu.tw/trexamps/",
        )

        self.assertEqual([link.title for link in links], ["公告甄選試題正確答案", "公告甄選試題及參考答案"])
        self.assertEqual(links[0].url, "https://qualify.tn.edu.tw/trexamps/view.aspx?id=10")
        self.assertEqual(links[1].url, "https://qualify.tn.edu.tw/trexamps/view.aspx?id=8")

    def test_parse_announcement_links_keeps_answer_only_notice_titles(self) -> None:
        links = parse_announcement_links(
            """
            <a href="view.aspx?id=12">公告甄選正確答案</a>
            <a href="view.aspx?id=13">公告錄取名單</a>
            """,
            page_url="https://qualify.tn.edu.tw/trexamps/",
        )

        self.assertEqual([link.title for link in links], ["公告甄選正確答案"])
        self.assertEqual(links[0].url, "https://qualify.tn.edu.tw/trexamps/view.aspx?id=12")

    def test_parse_downloads_classifies_official_upload_zip_links(self) -> None:
        downloads = parse_downloads(
            DETAIL_HTML,
            page_url="https://qualify.tn.edu.tw/trexamps/view.aspx?id=8",
        )

        self.assertEqual([download.file_type for download in downloads], ["question", "answer"])
        self.assertEqual(
            downloads[0].url,
            "https://qualify.tn.edu.tw/trexamps/upload/TrJh70115學年度市立國民小學教師暨學前特教師聯合甄選試題.zip",
        )

    def test_parse_downloads_keeps_answer_only_zip_labels(self) -> None:
        downloads = parse_downloads(
            """
            <a href="./upload/TrJh90115學年度市立國民小學教師暨學前特教師聯合甄選答案.zip">
              TrJh90115學年度市立國民小學教師暨學前特教師聯合甄選答案.zip
            </a>
            """,
            page_url="https://qualify.tn.edu.tw/trexamps/view.aspx?id=12",
        )

        self.assertEqual([download.file_type for download in downloads], ["corrected_answer"])


class TainanTeacherRecruitClientTests(unittest.TestCase):
    def test_fetch_exam_page_builds_current_year_recruitment_paper(self) -> None:
        client = TainanTeacherRecruitClient()
        pages = {
            "https://qualify.tn.edu.tw/trexamps/": LISTING_HTML,
            "https://qualify.tn.edu.tw/trexamps/view.aspx?id=8": DETAIL_HTML,
            "https://qualify.tn.edu.tw/trexamps/view.aspx?id=10": CORRECTED_DETAIL_HTML,
        }
        client._fetch_text = lambda url: pages[url]  # type: ignore[method-assign]

        page = client.fetch_exam_page("teacher-recruit-tainan-115", 2026)

        self.assertEqual(page.provider_id, "teacher_recruit_tainan")
        self.assertEqual(page.source_exam_id, "teacher-recruit-tainan-115")
        self.assertEqual(page.exam_name_raw, "115學年度臺南市國小教師甄試")
        self.assertEqual(len(page.papers), 1)
        self.assertEqual(page.papers[0].category_raw, "臺南市國小教師甄試")
        self.assertEqual(
            page.papers[0].files,
            {
                "corrected_answer": "https://qualify.tn.edu.tw/trexamps/upload/TrJh90115學年度市立國民小學教師暨學前特教師聯合甄選試題答案.zip",
                "question": "https://qualify.tn.edu.tw/trexamps/upload/TrJh70115學年度市立國民小學教師暨學前特教師聯合甄選試題.zip",
                "answer": "https://qualify.tn.edu.tw/trexamps/upload/TrJh71115學年度市立國民小學教師暨學前特教師聯合甄選試題參考答案.zip",
            },
        )


if __name__ == "__main__":
    unittest.main()
