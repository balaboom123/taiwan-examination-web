"""Tests for the teacher_qual provider."""

import unittest

from app.providers.teacher_qual.client import (
    TeacherQualClient,
    parse_available_years,
    parse_downloads,
    parse_subject_options,
)


TEACHER_LISTING_HTML = """
<select name="ctl00$ContentPlaceHolder1$schyy" id="ctl00_ContentPlaceHolder1_schyy">
  <option selected="selected" value=""></option>
  <option value="115">115</option>
  <option value="114">114</option>
  <option value="094">094</option>
</select>
<select name="ctl00$ContentPlaceHolder1$exid" id="ctl00_ContentPlaceHolder1_exid">
  <option selected="selected" value=""></option>
  <option value="10">幼兒園師資類科</option>
  <option value="99">全部類科</option>
</select>
<table>
  <tr><td>樣卷</td></tr>
  <tr><td>01_選擇題答案卡樣張<br><a href="ShowPicOut2.aspx?ASParam=sample">文件下載</a></td></tr>
  <tr><td>115年試題及參考答案</td></tr>
  <tr><td>考題及參考答案</td><td>全部下載<br><a href="ShowPicOut2.aspx?ASParam=all">文件下載</a></td></tr>
</table>
"""


class TeacherQualParserTests(unittest.TestCase):
    def test_parse_available_years(self) -> None:
        self.assertEqual(parse_available_years(TEACHER_LISTING_HTML), [2026, 2025, 2005])

    def test_parse_subject_options(self) -> None:
        self.assertEqual(parse_subject_options(TEACHER_LISTING_HTML), [("10", "幼兒園師資類科"), ("99", "全部類科")])

    def test_parse_downloads_keeps_historical_all_bundle(self) -> None:
        downloads = parse_downloads(TEACHER_LISTING_HTML, year_roc=115)

        self.assertEqual(len(downloads), 1)
        self.assertEqual(downloads[0].label, "115年試題及參考答案 考題及參考答案 全部下載")
        self.assertTrue(downloads[0].url.endswith("ASParam=all"))


class TeacherQualClientTests(unittest.TestCase):
    def test_fetch_exam_page_builds_single_bundle_paper(self) -> None:
        client = TeacherQualClient()
        client._listing_for_year = lambda year_roc: TEACHER_LISTING_HTML  # type: ignore[method-assign]

        page = client.fetch_exam_page("teacher-qual-115", 2026)

        self.assertEqual(page.provider_id, "teacher_qual")
        self.assertEqual(page.source_exam_id, "teacher-qual-115")
        self.assertEqual(len(page.papers), 1)
        self.assertIn("question", page.papers[0].files)


if __name__ == "__main__":
    unittest.main()
