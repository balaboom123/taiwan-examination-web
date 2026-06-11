from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote

from app.crawler import MoexClient
from app.models import AliasRule, ExamAttachment, NormalizedCatalog, ParsedPaper, SourceExamPage, StoredFile, SyncFailure
from app.normalizer import normalize_papers
from app.storage import MirrorStore

EXTENSION_OVERRIDES = {
    "application/pdf": ".pdf",
    "application/zip": ".zip",
}
EXPECTED_EXTENSIONS = {
    "question": ".pdf",
    "answer": ".pdf",
    "corrected_answer": ".pdf",
    "all_answers": ".pdf",
    "accessible_bundle": ".zip",
}
ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")


def _extension_for(content_type: str, file_name: str) -> str:
    suffix = Path(unquote(file_name)).suffix
    if suffix:
        return suffix
    return EXTENSION_OVERRIDES.get(content_type.split(";")[0].strip(), ".bin")


def _asset_name_for(storage_key: str) -> str:
    return storage_key.replace("/", "__")


def _mirror_prefix_for_attachment(page: SourceExamPage, attachment: ExamAttachment) -> str:
    return f"{page.year_roc}/{page.source_exam_id}/exam/{attachment.file_type}"


def _mirror_prefix_for_paper(page: SourceExamPage, paper: ParsedPaper, file_type: str) -> str:
    return f"{page.year_roc}/{page.source_exam_id}/{paper.category_code}/{paper.subject_code}/{file_type}"


def _strip_bom_prefix(data: bytes) -> bytes:
    return data[3:] if data.startswith(b"\xef\xbb\xbf") else data


def _looks_like_html(data: bytes) -> bool:
    head = _strip_bom_prefix(data[:256]).lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html") or head.startswith(b"<!doctype")


def _matches_expected_binary(data: bytes, expected_extension: str) -> bool:
    head = _strip_bom_prefix(data[:8])
    if expected_extension == ".pdf":
        return head.startswith(b"%PDF")
    if expected_extension == ".zip":
        return any(head.startswith(signature) for signature in ZIP_SIGNATURES)
    return False


def _validated_extension(file_type: str, data: bytes, content_type: str, file_name: str) -> str:
    expected_extension = EXPECTED_EXTENSIONS.get(file_type)
    if expected_extension and _matches_expected_binary(data, expected_extension):
        return expected_extension
    if expected_extension:
        if _looks_like_html(data):
            raise RuntimeError(f"Downloaded HTML placeholder instead of {expected_extension} for {file_type}")
        raise RuntimeError(f"Downloaded file does not match expected {expected_extension} payload for {file_type}")
    return _extension_for(content_type, file_name)


def _is_valid_stored_file(path: Path, file_type: str) -> bool:
    expected_extension = EXPECTED_EXTENSIONS.get(file_type)
    if expected_extension is None or path.suffix.lower() != expected_extension:
        return False
    return _matches_expected_binary(path.read_bytes()[:8], expected_extension)


def _ensure_mirrored(client: MoexClient, mirror_store: MirrorStore, prefix: str, file_type: str, download_url: str) -> StoredFile:
    stored = mirror_store.find_existing(prefix)
    if stored is not None and not _is_valid_stored_file(stored.path, file_type):
        stored = None
    if stored is None:
        downloaded = client.download_file(download_url)
        extension = _validated_extension(file_type, downloaded.data, downloaded.content_type, downloaded.file_name)
        stored = mirror_store.write_bytes(f"{prefix}{extension}", downloaded.data, overwrite=True)
        mirror_store.delete_matching_except(prefix, stored.storage_key)
    return stored


def sync_exam_pages(
    client: MoexClient,
    exam_codes: list[tuple[str, int]],
    mirror_store: MirrorStore,
    alias_rules: list[AliasRule],
    mirror_base_url: str,
    download_attachments: bool = True,
) -> tuple[list[SourceExamPage], NormalizedCatalog, list[SyncFailure]]:
    raw_pages: list[SourceExamPage] = []
    normalized_papers = []
    review_queue = []
    failures: list[SyncFailure] = []

    for exam_code, year_ad in exam_codes:
        try:
            page = client.fetch_exam_page(exam_code, year_ad)
        except Exception as exc:
            failures.append(
                SyncFailure(
                    stage="fetch",
                    source_exam_id=exam_code,
                    year_roc=year_ad - 1911,
                    paper_code="",
                    file_type="",
                    url="",
                    message=f"Failed to fetch exam page: {exc}",
                )
            )
            continue
        mirror_metadata: dict[tuple[str, str, str], dict[str, str]] = {}

        if download_attachments:
            for attachment in page.attachments:
                try:
                    stored = _ensure_mirrored(
                        client,
                        mirror_store,
                        _mirror_prefix_for_attachment(page, attachment),
                        attachment.file_type,
                        attachment.download_url_source,
                    )
                    attachment.storage_key = stored.storage_key
                    attachment.asset_name = _asset_name_for(stored.storage_key)
                    attachment.checksum = stored.checksum
                    attachment.download_url_mirror = f"{mirror_base_url.rstrip('/')}/{attachment.asset_name}" if mirror_base_url else ""
                except Exception as exc:
                    failures.append(
                        SyncFailure(
                            stage="download",
                            source_exam_id=page.source_exam_id,
                            year_roc=page.year_roc,
                            paper_code=f"exam-{attachment.file_type}",
                            file_type=attachment.file_type,
                            url=attachment.download_url_source,
                            message=str(exc),
                        )
                    )

        for paper in page.papers:
            for file_type, download_url in paper.files.items():
                try:
                    stored = _ensure_mirrored(client, mirror_store, _mirror_prefix_for_paper(page, paper, file_type), file_type, download_url)
                    paper.mirror_files[file_type] = {
                        "storage_key": stored.storage_key,
                        "asset_name": _asset_name_for(stored.storage_key),
                        "checksum": stored.checksum,
                    }
                    mirror_metadata[(paper.category_code, paper.subject_code, file_type)] = paper.mirror_files[file_type]
                except Exception as exc:
                    failures.append(
                        SyncFailure(
                            stage="download",
                            source_exam_id=page.source_exam_id,
                            year_roc=page.year_roc,
                            paper_code=f"{paper.category_code}-{paper.subject_code}-{file_type}",
                            file_type=file_type,
                            url=download_url,
                            message=str(exc),
                        )
                    )

        normalized_input_papers = [
            ParsedPaper(
                category_raw=paper.category_raw,
                category_code=paper.category_code,
                subject_code=paper.subject_code,
                subject_name_raw=paper.subject_name_raw,
                files={file_type: paper.files[file_type] for file_type in paper.mirror_files},
                mirror_files=paper.mirror_files,
            )
            for paper in page.papers
            if paper.mirror_files
        ]

        normalized = normalize_papers(
            source_exam_id=page.source_exam_id,
            year_ad=page.year_ad,
            exam_name_raw=page.exam_name_raw,
            papers=normalized_input_papers,
            alias_rules=alias_rules,
            mirror_base_url=mirror_base_url,
            mirror_metadata=mirror_metadata,
        )
        raw_pages.append(page)
        normalized_papers.extend(normalized.papers)
        review_queue.extend(normalized.review_queue)

    return raw_pages, NormalizedCatalog(papers=normalized_papers, review_queue=review_queue), failures
