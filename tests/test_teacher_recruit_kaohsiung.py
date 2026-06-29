"""Tests for the teacher_recruit_kaohsiung provider."""

import unittest

from app.providers.teacher_recruit_kaohsiung.client import (
    KaohsiungTeacherRecruitClient,
    parse_elementary_page,
    parse_special_page,
)


ELEMENTARY_HTML = """
<a href="upload/試題.zip">試題.zip</a>
<a href="upload/%E8%A9%A6%E9%A1%8C.zip">試題.zip</a>
<a href="upload/答案.zip">答案.zip</a>
<a href="upload/正確答案.zip">正確答案.zip</a>
<a href="upload/附件1-高雄市115年度國小教師聯合甄選缺額總表.pdf">缺額.pdf</a>
"""

SPECIAL_HTML = """
<a href="upload/身心障礙類試題教育局.pdf">身心障礙類試題教育局.pdf</a>
<a href="upload/身心障礙類參考答案教育局.pdf">身心障礙類參考答案教育局.pdf</a>
<a href="upload/正確答案-身心障礙類.pdf">正確答案-身心障礙類.pdf</a>
<a href="upload/附件2-國中身心障礙類教學演示-試教題目.pdf">試教題目.pdf</a>
"""


class KaohsiungTeacherRecruitParserTests(unittest.TestCase):
    def test_parse_elementary_page_keeps_three_zip_files_once(self) -> None:
        paper = parse_elementary_page("https://exam.kh.edu.tw/teaexam/", ELEMENTARY_HTML)

        self.assertIsNotNone(paper)
        assert paper is not None
        self.assertEqual(paper.subject_name, "國小教師聯合甄選")
        self.assertEqual(paper.downloads["question"], "https://exam.kh.edu.tw/teaexam/upload/試題.zip")
        self.assertEqual(paper.downloads["answer"], "https://exam.kh.edu.tw/teaexam/upload/答案.zip")
        self.assertEqual(paper.downloads["corrected_answer"], "https://exam.kh.edu.tw/teaexam/upload/正確答案.zip")

    def test_parse_special_page_skips_teaching_demo_topics(self) -> None:
        papers = parse_special_page("https://exam.kh.edu.tw/special/", SPECIAL_HTML)

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].subject_name, "身心障礙類")
        self.assertEqual(papers[0].downloads["question"], "https://exam.kh.edu.tw/special/upload/身心障礙類試題教育局.pdf")
        self.assertEqual(papers[0].downloads["answer"], "https://exam.kh.edu.tw/special/upload/身心障礙類參考答案教育局.pdf")
        self.assertEqual(papers[0].downloads["corrected_answer"], "https://exam.kh.edu.tw/special/upload/正確答案-身心障礙類.pdf")


class KaohsiungTeacherRecruitClientTests(unittest.TestCase):
    def test_fetch_elementary_exam_page_builds_one_paper(self) -> None:
        client = KaohsiungTeacherRecruitClient(elementary_html=ELEMENTARY_HTML, special_html=SPECIAL_HTML)

        page = client.fetch_exam_page("teacher-recruit-kaohsiung-115-elementary", 2026)

        self.assertEqual(page.provider_id, "teacher_recruit_kaohsiung")
        self.assertEqual(page.exam_name_raw, "115學年度高雄市教師甄試")
        self.assertEqual(page.papers[0].category_raw, "高雄市教師甄試")
        self.assertEqual(page.papers[0].subject_code, "elementary")

    def test_fetch_special_exam_page_builds_special_papers(self) -> None:
        client = KaohsiungTeacherRecruitClient(elementary_html=ELEMENTARY_HTML, special_html=SPECIAL_HTML)

        page = client.fetch_exam_page("teacher-recruit-kaohsiung-115-special", 2026)

        self.assertEqual(page.papers[0].subject_name_raw, "身心障礙類")
        self.assertEqual(set(page.papers[0].files), {"question", "answer", "corrected_answer"})


if __name__ == "__main__":
    unittest.main()
