import tempfile
import unittest
from pathlib import Path

from app.crawler import DownloadedFile
from app.models import AliasRule, ExamAttachment, ParsedPaper, SourceExamPage
from app.providers.base import SourceProvider
from app.providers.moex.provider import MoexProvider
from app.storage import MirrorStore
from app.sync import sync_exam_pages


class FakeClient:
    provider_id = "moex"

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="115年專技高考護理師",
            attachments=[ExamAttachment(title="全部答案", file_type="all_answers", download_url_source="https://example.test/all.pdf")],
            papers=[
                ParsedPaper(
                    category_raw="護理師",
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


class ReuseExistingMirrorClient:
    provider_id = "moex"

    def __init__(self) -> None:
        self.downloaded_urls: list[str] = []

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="demo exam",
            attachments=[ExamAttachment(title="全部答案", file_type="all_answers", download_url_source="https://example.test/all.pdf")],
            papers=[
                ParsedPaper(
                    category_raw="nurse raw",
                    category_code="101",
                    subject_code="0101",
                    subject_name_raw="subject",
                    files={
                        "question": "https://example.test/question.pdf",
                        "answer": "https://example.test/answer.pdf",
                    },
                )
            ],
        )

    def download_file(self, url: str) -> DownloadedFile:
        self.downloaded_urls.append(url)
        return DownloadedFile(data=b"%PDF-1.7 demo", content_type="application/pdf", file_name=Path(url).name)


class QuestionOnlyClient:
    provider_id = "moex"

    def __init__(self) -> None:
        self.downloaded_urls: list[str] = []

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="demo exam",
            attachments=[],
            papers=[
                ParsedPaper(
                    category_raw="nurse raw",
                    category_code="101",
                    subject_code="0101",
                    subject_name_raw="subject",
                    files={"question": "https://example.test/question.pdf"},
                )
            ],
        )

    def download_file(self, url: str) -> DownloadedFile:
        self.downloaded_urls.append(url)
        return DownloadedFile(data=b"%PDF-1.7 original payload", content_type="application/pdf", file_name=Path(url).name)


class HtmlPlaceholderClient:
    provider_id = "moex"

    def __init__(self) -> None:
        self.downloaded_urls: list[str] = []

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="demo exam",
            attachments=[],
            papers=[
                ParsedPaper(
                    category_raw="nurse raw",
                    category_code="101",
                    subject_code="0101",
                    subject_name_raw="subject",
                    files={"question": "https://example.test/question.ashx"},
                )
            ],
        )

    def download_file(self, url: str) -> DownloadedFile:
        self.downloaded_urls.append(url)
        return DownloadedFile(
            data=b"\xef\xbb\xbf<!DOCTYPE html><html><title>error</title></html>",
            content_type="text/html; charset=utf-8",
            file_name="wHandExamQandA_File.ashx",
        )


class SyncExamPagesTests(unittest.TestCase):
    def test_moex_provider_implements_source_provider_contract(self) -> None:
        self.assertIsInstance(MoexProvider(), SourceProvider)

    def test_sync_exam_pages_keeps_partial_success_and_records_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            raw_pages, normalized, failures = sync_exam_pages(
                client=FakeClient(),
                exam_codes=[("115030", 2026)],
                mirror_store=MirrorStore(Path(tmp_dir)),
                alias_rules=[AliasRule(match_type="exact", raw_pattern="護理師", canonical_id="nurse", canonical_name="護理師")],
                mirror_base_url="",
            )

        self.assertEqual(len(raw_pages), 1)
        self.assertEqual(len(normalized.papers), 1)
        self.assertEqual(normalized.papers[0].file_type, "question")
        self.assertEqual(len(failures), 2)
        self.assertEqual({failure["file_type"] for failure in failures}, {"all_answers", "answer"})

    def test_sync_exam_pages_reuses_existing_mirror_files_before_downloading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            attachment_path = mirror_root / "providers" / "moex" / "115" / "115030" / "exam" / "all_answers.pdf"
            attachment_path.parent.mkdir(parents=True, exist_ok=True)
            attachment_path.write_bytes(b"%PDF-1.7 cached attachment")
            question_path = mirror_root / "providers" / "moex" / "115" / "115030" / "101" / "0101" / "question.pdf"
            question_path.parent.mkdir(parents=True, exist_ok=True)
            question_path.write_bytes(b"%PDF-1.7 cached question")
            client = ReuseExistingMirrorClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("115030", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[AliasRule(match_type="exact", raw_pattern="nurse raw", canonical_id="nurse", canonical_name="Nurse")],
                mirror_base_url="",
            )

        self.assertEqual(client.downloaded_urls, ["https://example.test/answer.pdf"])
        self.assertEqual(raw_pages[0].attachments[0].storage_key, "providers/moex/115/115030/exam/all_answers.pdf")
        self.assertEqual(
            raw_pages[0].papers[0].mirror_files["question"]["storage_key"],
            "providers/moex/115/115030/101/0101/question.pdf",
        )
        self.assertEqual(sorted(paper.file_type for paper in normalized.papers), ["answer", "question"])
        self.assertEqual(failures, [])

    def test_sync_exam_pages_can_skip_attachment_downloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            client = ReuseExistingMirrorClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("115030", 2026)],
                mirror_store=MirrorStore(Path(tmp_dir)),
                alias_rules=[AliasRule(match_type="exact", raw_pattern="nurse raw", canonical_id="nurse", canonical_name="Nurse")],
                mirror_base_url="",
                download_attachments=False,
            )

        self.assertEqual(client.downloaded_urls, ["https://example.test/question.pdf", "https://example.test/answer.pdf"])
        self.assertEqual(raw_pages[0].attachments[0].download_url_source, "https://example.test/all.pdf")
        self.assertEqual(raw_pages[0].attachments[0].storage_key, "")
        self.assertEqual(sorted(paper.file_type for paper in normalized.papers), ["answer", "question"])
        self.assertEqual(failures, [])

    def test_sync_exam_pages_rejects_html_placeholder_downloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            client = HtmlPlaceholderClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("115030", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[AliasRule(match_type="exact", raw_pattern="nurse raw", canonical_id="nurse", canonical_name="Nurse")],
                mirror_base_url="",
            )

            self.assertFalse(any(mirror_root.rglob("question.*")))

        self.assertEqual(client.downloaded_urls, ["https://example.test/question.ashx"])
        self.assertEqual(len(raw_pages), 1)
        self.assertEqual(normalized.papers, [])
        self.assertEqual(len(failures), 1)
        self.assertIn("HTML placeholder", failures[0].message)

    def test_sync_exam_pages_replaces_invalid_existing_ashx_with_valid_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            file_dir = mirror_root / "providers" / "moex" / "115" / "115030" / "101" / "0101"
            file_dir.mkdir(parents=True, exist_ok=True)
            (file_dir / "question.ashx").write_bytes(b"\xef\xbb\xbf<!DOCTYPE html><html>error</html>")
            client = QuestionOnlyClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("115030", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[AliasRule(match_type="exact", raw_pattern="nurse raw", canonical_id="nurse", canonical_name="Nurse")],
                mirror_base_url="",
            )
            stored_bytes = (file_dir / "question.pdf").read_bytes()

        self.assertEqual(client.downloaded_urls, ["https://example.test/question.pdf"])
        self.assertEqual(stored_bytes, b"%PDF-1.7 original payload")
        self.assertFalse((file_dir / "question.ashx").exists())
        self.assertEqual(
            raw_pages[0].papers[0].mirror_files["question"]["storage_key"],
            "providers/moex/115/115030/101/0101/question.pdf",
        )
        self.assertEqual([paper.file_type for paper in normalized.papers], ["question"])
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
