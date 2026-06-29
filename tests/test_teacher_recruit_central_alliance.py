"""Tests for the teacher_recruit_central_alliance provider."""

import unittest

from app.providers.teacher_recruit_central_alliance.client import (
    CentralAllianceRecruitClient,
    parse_final_answer_page,
    parse_subject_page,
)


SUBJECT_HTML = """
<table>
  <tr>
    <td>1</td><td>國語文</td>
    <td>試題：<a href="./download.php?seq=q1&type=question">115中策_國語文_試題.pdf</a></td>
    <td>參考解答：<a href="./download.php?seq=q1&type=referenceanswer">115中策_國語文答案.pdf</a></td>
  </tr>
</table>
"""

FINAL_HTML = """
<table>
  <tr>
    <td>1</td><td>國語文</td>
    <td><a href="./download.php?seq=f1&type=finalanswer">115中策_國語文答案.pdf</a></td>
  </tr>
</table>
"""


class CentralAllianceRecruitParserTests(unittest.TestCase):
    def test_parse_subject_page_pairs_question_and_reference_answer(self) -> None:
        papers = parse_subject_page("https://qa115-tse-cl.twrecruit.com.tw/Subject/news.php?cate=B", "elementary", "國小", SUBJECT_HTML)

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].level_code, "elementary")
        self.assertEqual(papers[0].level_name, "國小")
        self.assertEqual(papers[0].subject_name, "國語文")
        self.assertTrue(papers[0].downloads["question"].endswith("type=question"))
        self.assertTrue(papers[0].downloads["answer"].endswith("type=referenceanswer"))

    def test_parse_final_answer_page_adds_corrected_answer(self) -> None:
        final_answers = parse_final_answer_page("https://qa115-tse-cl.twrecruit.com.tw/Ans2/news.php?cate=B", FINAL_HTML)

        self.assertTrue(final_answers["國語文"].endswith("type=finalanswer"))


class CentralAllianceRecruitClientTests(unittest.TestCase):
    def test_fetch_exam_page_merges_subject_and_final_answer_downloads(self) -> None:
        client = CentralAllianceRecruitClient(subject_html_by_level={"elementary": SUBJECT_HTML}, final_html_by_level={"elementary": FINAL_HTML})

        page = client.fetch_exam_page("teacher-recruit-central-alliance-115-elementary", 2026)

        self.assertEqual(page.provider_id, "teacher_recruit_central_alliance")
        self.assertEqual(page.exam_name_raw, "115學年度中區策略聯盟教師甄試")
        self.assertEqual(page.papers[0].category_raw, "中區策略聯盟教師甄試")
        self.assertEqual(page.papers[0].subject_name_raw, "國小-國語文")
        self.assertEqual(set(page.papers[0].files), {"question", "answer", "corrected_answer"})


if __name__ == "__main__":
    unittest.main()
