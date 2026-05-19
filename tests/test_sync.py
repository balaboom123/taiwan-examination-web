import tempfile
import unittest
from pathlib import Path

from app.crawler import DownloadedFile
from app.models import AliasRule, ExamAttachment, ParsedPaper, SourceExamPage
from app.storage import MirrorStore
from app.sync import sync_exam_pages


class FakeClient:
    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="115年測試考試",
            attachments=[ExamAttachment(title="所有測驗題標準答案", file_type="all_answers", download_url_source="https://example.test/all.pdf")],
            papers=[
                ParsedPaper(
                    category_raw="高等考試_護理師",
                    category_code="101",
                    subject_code="0101",
                    subject_name_raw="基礎醫學",
                    files={
                        "question": "https://example.test/question.pdf",
                        "answer": "https://example.test/answer.pdf",
                    },
                )
            ],
        )

    def download_file(self, url: str) -> DownloadedFile:
        if url.endswith("all.pdf") or url.endswith("answer.pdf"):
            raise RuntimeError("boom")
        return DownloadedFile(data=b"%PDF-1.7 demo", content_type="application/pdf", file_name=Path(url).name)


class SyncExamPagesTests(unittest.TestCase):
    def test_sync_exam_pages_keeps_partial_success_and_records_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            raw_pages, normalized, failures = sync_exam_pages(
                client=FakeClient(),
                exam_codes=[("115030", 2026)],
                mirror_store=MirrorStore(Path(tmp_dir)),
                alias_rules=[AliasRule(match_type="exact", raw_pattern="高等考試_護理師", canonical_id="nurse", canonical_name="護理師")],
                mirror_base_url="",
            )

        self.assertEqual(len(raw_pages), 1)
        self.assertEqual(len(normalized.papers), 1)
        self.assertEqual(normalized.papers[0].file_type, "question")
        self.assertEqual(len(failures), 2)
        self.assertEqual({failure["file_type"] for failure in failures}, {"all_answers", "answer"})


if __name__ == "__main__":
    unittest.main()
