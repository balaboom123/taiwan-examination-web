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


class QuestionAltDocxClient:
    provider_id = "ceec_gsat"

    def __init__(self) -> None:
        self.downloaded_urls: list[str] = []

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="115學年度學科能力測驗－國綜",
            attachments=[],
            papers=[
                ParsedPaper(
                    category_raw="摮貊測驗",
                    category_code="115",
                    subject_code="guozong-01",
                    subject_name_raw="國綜 試題內容",
                    files={"question": "https://example.test/question.pdf"},
                ),
                ParsedPaper(
                    category_raw="摮貊測驗",
                    category_code="115",
                    subject_code="guozong-02",
                    subject_name_raw="國綜 試題內容",
                    files={"question_alt": "https://example.test/question-alt.docx"},
                ),
            ],
            provider_id=self.provider_id,
        )

    def download_file(self, url: str) -> DownloadedFile:
        self.downloaded_urls.append(url)
        if url.endswith(".docx"):
            return DownloadedFile(
                data=b"PK\x03\x04docx payload",
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                file_name=Path(url).name,
            )
        return DownloadedFile(data=b"%PDF-1.7 demo", content_type="application/pdf", file_name=Path(url).name)


class QuestionDocClient:
    provider_id = "ceec_gsat"

    def __init__(self) -> None:
        self.downloaded_urls: list[str] = []

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="102摮詨僑摨血飛蝘?葫撽??芰",
            attachments=[],
            papers=[
                ParsedPaper(
                    category_raw="?株?皜祇?",
                    category_code="102",
                    subject_code="science-01",
                    subject_name_raw="?芰 閰阡??批捆",
                    files={"question": "https://example.test/question.doc"},
                ),
                ParsedPaper(
                    category_raw="?株?皜祇?",
                    category_code="102",
                    subject_code="science-02",
                    subject_name_raw="?芰 閰阡??批捆",
                    files={"question_alt": "https://example.test/question-alt.doc"},
                ),
            ],
            provider_id=self.provider_id,
        )

    def download_file(self, url: str) -> DownloadedFile:
        self.downloaded_urls.append(url)
        return DownloadedFile(
            data=b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1legacy doc payload",
            content_type="application/msword",
            file_name=Path(url).name,
        )


class QuestionArchiveClient:
    provider_id = "rcpet_cap"

    def __init__(self, *, url: str, data: bytes, content_type: str, file_name: str) -> None:
        self.url = url
        self.data = data
        self.content_type = content_type
        self.file_name = file_name
        self.downloaded_urls: list[str] = []

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="115 CAP",
            attachments=[],
            papers=[
                ParsedPaper(
                    category_raw="CAP",
                    category_code="115",
                    subject_code="english-listening",
                    subject_name_raw="English listening",
                    files={"question": self.url},
                )
            ],
            provider_id=self.provider_id,
        )

    def download_file(self, url: str) -> DownloadedFile:
        self.downloaded_urls.append(url)
        return DownloadedFile(data=self.data, content_type=self.content_type, file_name=self.file_name)


class AnswerArchiveClient:
    provider_id = "teacher_recruit_tainan"

    def __init__(self) -> None:
        self.downloaded_urls: list[str] = []

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="115學年度臺南市國小教師甄試",
            attachments=[],
            papers=[
                ParsedPaper(
                    category_raw="臺南市國小教師甄試",
                    category_code="115",
                    subject_code="elementary-prek-special-ed",
                    subject_name_raw="國小教師暨學前特教師聯合甄選",
                    files={
                        "answer": "https://example.test/reference-answer.zip",
                        "corrected_answer": "https://example.test/corrected-answer.zip",
                    },
                )
            ],
            provider_id=self.provider_id,
        )

    def download_file(self, url: str) -> DownloadedFile:
        self.downloaded_urls.append(url)
        return DownloadedFile(data=b"PK\x03\x04zip payload", content_type="application/zip", file_name=Path(url).name)


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

    def test_sync_exam_pages_reuses_legacy_unscoped_mirror_files_and_promotes_storage_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            legacy_question_path = mirror_root / "115" / "115030" / "101" / "0101" / "question.pdf"
            legacy_question_path.parent.mkdir(parents=True, exist_ok=True)
            legacy_question_path.write_bytes(b"%PDF-1.7 cached legacy question")
            client = ReuseExistingMirrorClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("115030", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[AliasRule(match_type="exact", raw_pattern="nurse raw", canonical_id="nurse", canonical_name="Nurse")],
                mirror_base_url="",
            )

            promoted_path = mirror_root / "providers" / "moex" / "115" / "115030" / "101" / "0101" / "question.pdf"
            self.assertEqual(sorted(client.downloaded_urls), ["https://example.test/all.pdf", "https://example.test/answer.pdf"])
            self.assertTrue(promoted_path.exists())
            self.assertEqual(promoted_path.read_bytes(), b"%PDF-1.7 cached legacy question")
            self.assertEqual(
                raw_pages[0].papers[0].mirror_files["question"]["storage_key"],
                "providers/moex/115/115030/101/0101/question.pdf",
            )
            question_paper = next(paper for paper in normalized.papers if paper.file_type == "question")
            self.assertEqual(question_paper.storage_key, "providers/moex/115/115030/101/0101/question.pdf")
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

    def test_sync_exam_pages_reuses_valid_legacy_file_when_scoped_placeholder_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            scoped_dir = mirror_root / "providers" / "moex" / "115" / "115030" / "101" / "0101"
            scoped_dir.mkdir(parents=True, exist_ok=True)
            (scoped_dir / "question.ashx").write_bytes(b"\xef\xbb\xbf<!DOCTYPE html><html>error</html>")
            legacy_dir = mirror_root / "115" / "115030" / "101" / "0101"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            (legacy_dir / "question.pdf").write_bytes(b"%PDF-1.7 cached legacy payload")
            client = QuestionOnlyClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("115030", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[AliasRule(match_type="exact", raw_pattern="nurse raw", canonical_id="nurse", canonical_name="Nurse")],
                mirror_base_url="",
            )

            promoted_path = scoped_dir / "question.pdf"
            self.assertEqual(client.downloaded_urls, [])
            self.assertTrue(promoted_path.exists())
            self.assertEqual(promoted_path.read_bytes(), b"%PDF-1.7 cached legacy payload")
            self.assertEqual(
                raw_pages[0].papers[0].mirror_files["question"]["storage_key"],
                "providers/moex/115/115030/101/0101/question.pdf",
            )
            self.assertEqual([paper.file_type for paper in normalized.papers], ["question"])
            self.assertEqual(failures, [])

    def test_sync_exam_pages_accepts_question_alt_docx_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            client = QuestionAltDocxClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("gsat-115-guozong", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[],
                mirror_base_url="",
            )

        self.assertEqual(
            client.downloaded_urls,
            ["https://example.test/question.pdf", "https://example.test/question-alt.docx"],
        )
        self.assertEqual(len(raw_pages), 1)
        self.assertEqual(sorted(paper.file_type for paper in normalized.papers), ["question", "question_alt"])
        self.assertEqual(
            raw_pages[0].papers[1].mirror_files["question_alt"]["storage_key"],
            "providers/ceec_gsat/115/gsat-115-guozong/115/guozong-02/question_alt.docx",
        )
        self.assertEqual(failures, [])

    def test_sync_exam_pages_accepts_legacy_question_doc_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            client = QuestionDocClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("gsat-102-science", 2013)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[],
                mirror_base_url="",
            )

        self.assertEqual(
            client.downloaded_urls,
            ["https://example.test/question.doc", "https://example.test/question-alt.doc"],
        )
        self.assertEqual(len(raw_pages), 1)
        self.assertEqual(sorted(paper.file_type for paper in normalized.papers), ["question", "question_alt"])
        self.assertEqual(
            raw_pages[0].papers[0].mirror_files["question"]["storage_key"],
            "providers/ceec_gsat/102/gsat-102-science/102/science-01/question.doc",
        )
        self.assertEqual(
            raw_pages[0].papers[1].mirror_files["question_alt"]["storage_key"],
            "providers/ceec_gsat/102/gsat-102-science/102/science-02/question_alt.doc",
        )
        self.assertEqual(failures, [])

    def test_sync_exam_pages_accepts_question_zip_payloads_without_filename_extension(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            client = QuestionArchiveClient(
                url="https://drive.google.com/uc?id=demo&export=download",
                data=b"PK\x03\x04zip payload",
                content_type="application/octet-stream",
                file_name="uc",
            )

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("cap-115", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[],
                mirror_base_url="",
            )

        self.assertEqual(client.downloaded_urls, ["https://drive.google.com/uc?id=demo&export=download"])
        self.assertEqual(len(raw_pages), 1)
        self.assertEqual([paper.file_type for paper in normalized.papers], ["question"])
        self.assertEqual(
            raw_pages[0].papers[0].mirror_files["question"]["storage_key"],
            "providers/rcpet_cap/115/cap-115/115/english-listening/question.zip",
        )
        self.assertEqual(failures, [])

    def test_sync_exam_pages_accepts_question_rar_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            client = QuestionArchiveClient(
                url="https://ws.cpc.com.tw/Download.ashx?u=demo&n=demo",
                data=b"Rar!\x1a\x07\x00archive payload",
                content_type="application/octet-stream",
                file_name="old-question.rar",
            )

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("cap-115", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[],
                mirror_base_url="",
            )

        self.assertEqual(client.downloaded_urls, ["https://ws.cpc.com.tw/Download.ashx?u=demo&n=demo"])
        self.assertEqual([paper.file_type for paper in normalized.papers], ["question"])
        self.assertEqual(
            raw_pages[0].papers[0].mirror_files["question"]["storage_key"],
            "providers/rcpet_cap/115/cap-115/115/english-listening/question.rar",
        )
        self.assertEqual(failures, [])

    def test_sync_exam_pages_accepts_answer_zip_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mirror_root = Path(tmp_dir)
            client = AnswerArchiveClient()

            raw_pages, normalized, failures = sync_exam_pages(
                client=client,
                exam_codes=[("teacher-recruit-tainan-115", 2026)],
                mirror_store=MirrorStore(mirror_root),
                alias_rules=[],
                mirror_base_url="",
            )

        self.assertEqual(
            client.downloaded_urls,
            ["https://example.test/reference-answer.zip", "https://example.test/corrected-answer.zip"],
        )
        self.assertEqual(sorted(paper.file_type for paper in normalized.papers), ["answer", "corrected_answer"])
        self.assertEqual(
            raw_pages[0].papers[0].mirror_files["answer"]["storage_key"],
            "providers/teacher_recruit_tainan/115/teacher-recruit-tainan-115/115/elementary-prek-special-ed/answer.zip",
        )
        self.assertEqual(
            raw_pages[0].papers[0].mirror_files["corrected_answer"]["storage_key"],
            "providers/teacher_recruit_tainan/115/teacher-recruit-tainan-115/115/elementary-prek-special-ed/corrected_answer.zip",
        )
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
