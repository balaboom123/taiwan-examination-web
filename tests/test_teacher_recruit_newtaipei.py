"""Tests for the teacher_recruit_newtaipei provider."""

import unittest

from app.providers.teacher_recruit_newtaipei.client import (
    NewTaipeiTeacherRecruitClient,
    detail_matches_notice,
    parse_candidate_notices,
    parse_detail_downloads,
)


LIST_ROWS = [
    {
        "opn_title": "【初試試題】新北市立國民中學115學年度教師聯合甄選初試試題及答案",
        "opn_tag": "新北市立國民中學115學年度教師聯合甄選",
        "uuid": "notice-uuid",
    },
    {
        "opn_title": "新北市立國民中學115學年度教師聯合甄選初試試題疑義回覆",
        "opn_tag": "新北市立國民中學115學年度教師聯合甄選",
        "uuid": "appeal-uuid",
    },
]

DETAIL_ROW = {
    "opn_title": "【初試試題】新北市立國民中學115學年度教師聯合甄選初試試題及答案",
    "opn_tag": "新北市立國民中學115學年度教師聯合甄選",
    "attachment2": [
        {
            "fileName": "新北市國民中學教師聯合甄選試題答案.rar",
            "fileSize": "16255KB",
            "fileUuid": "file-uuid",
        },
        {
            "fileName": "新北市國民中學教師聯合甄選試題疑義申請表.pdf",
            "fileSize": "120KB",
            "fileUuid": "appeal-file",
        },
    ],
}


class NewTaipeiTeacherRecruitParserTests(unittest.TestCase):
    def test_parse_candidate_notices_keeps_paper_notices_only(self) -> None:
        notices = parse_candidate_notices(LIST_ROWS)

        self.assertEqual([notice.uuid for notice in notices], ["notice-uuid"])
        self.assertEqual(notices[0].year_ad, 2026)
        self.assertEqual(notices[0].year_roc, 115)
        self.assertEqual(notices[0].scope_code, "junior")

    def test_detail_matches_notice_requires_title_or_tag_overlap(self) -> None:
        notice = parse_candidate_notices(LIST_ROWS)[0]

        self.assertTrue(detail_matches_notice(notice, DETAIL_ROW))
        self.assertFalse(detail_matches_notice(notice, {"opn_title": "其他公告", "opn_tag": "其他甄選"}))

    def test_parse_detail_downloads_keeps_question_answer_attachment(self) -> None:
        downloads = parse_detail_downloads(DETAIL_ROW)

        self.assertEqual(len(downloads), 1)
        self.assertEqual(downloads[0].file_type, "question_answer")
        self.assertEqual(downloads[0].file_name, "新北市國民中學教師聯合甄選試題答案.rar")
        self.assertTrue(downloads[0].url.endswith("/download/file-uuid"))


class NewTaipeiTeacherRecruitClientTests(unittest.TestCase):
    def test_fetch_exam_page_builds_notice_paper(self) -> None:
        client = NewTaipeiTeacherRecruitClient()
        client._fetch_json = lambda url: LIST_ROWS if url.endswith("temopn_newtea_list") else [DETAIL_ROW]  # type: ignore[method-assign]

        exam = client.discover_exams(2026)[0]
        page = client.fetch_exam_page(exam.code, 2026)

        self.assertEqual(page.provider_id, "teacher_recruit_newtaipei")
        self.assertEqual(page.exam_name_raw, "115學年度新北市教師甄試")
        self.assertEqual(len(page.papers), 1)
        self.assertEqual(page.papers[0].category_raw, "新北市教師甄試")
        self.assertEqual(page.papers[0].subject_code, "junior")
        self.assertEqual(page.papers[0].files["question_answer"].split("/")[-1], "file-uuid")

    def test_download_file_exchanges_file_uuid_for_download_token(self) -> None:
        client = NewTaipeiTeacherRecruitClient()
        client._fetch_json = lambda url: [{"token": "download-token"}]  # type: ignore[method-assign]
        client._fetch_bytes = lambda url: (  # type: ignore[method-assign]
            b"Rar!\x1a\x07\x00data",
            {
                "Content-Type": "application/octet-stream",
                "Content-Disposition": "inline; filename = sample.rar",
            },
        )

        downloaded = client.download_file(
            "https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/download/file-uuid"
        )

        self.assertEqual(downloaded.data, b"Rar!\x1a\x07\x00data")
        self.assertEqual(downloaded.content_type, "application/octet-stream")
        self.assertEqual(downloaded.file_name, "sample.rar")


if __name__ == "__main__":
    unittest.main()
