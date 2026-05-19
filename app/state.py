from __future__ import annotations

import json
from pathlib import Path

from app.models import (
    AliasRule,
    BundleAsset,
    ExamAttachment,
    NormalizedCatalog,
    NormalizedPaper,
    ParsedPaper,
    ReviewItem,
    SourceExamPage,
    SyncFailure,
)


def load_existing_state(data_dir: Path) -> tuple[list[SourceExamPage], NormalizedCatalog, list[BundleAsset], list[SyncFailure]]:
    if not data_dir.exists():
        return [], NormalizedCatalog(papers=[], review_queue=[]), [], []
    return (
        _load_raw_pages(data_dir / "exams.raw.json"),
        _load_catalog(data_dir / "papers.json", data_dir / "review-queue.json"),
        _load_bundles(data_dir / "bundles.json"),
        _load_failures(data_dir / "sync-failures.json"),
    )


def merge_incremental_state(
    existing_raw_pages: list[SourceExamPage],
    existing_catalog: NormalizedCatalog,
    existing_bundles: list[BundleAsset],
    refreshed_raw_pages: list[SourceExamPage],
    refreshed_catalog: NormalizedCatalog,
    refreshed_year_rocs: set[int],
) -> tuple[list[SourceExamPage], NormalizedCatalog, list[BundleAsset], set[str]]:
    refreshed_exam_ids = {page.source_exam_id for page in refreshed_raw_pages}
    merged_raw_pages = [page for page in existing_raw_pages if page.source_exam_id not in refreshed_exam_ids] + refreshed_raw_pages
    merged_papers = [paper for paper in existing_catalog.papers if paper.source_exam_id not in refreshed_exam_ids] + refreshed_catalog.papers
    merged_review_queue = [item for item in existing_catalog.review_queue if item.source_exam_id not in refreshed_exam_ids] + refreshed_catalog.review_queue

    affected_canonical_ids = {paper.canonical_id for paper in existing_catalog.papers if paper.source_exam_id in refreshed_exam_ids}
    affected_canonical_ids.update(paper.canonical_id for paper in refreshed_catalog.papers)
    active_canonical_ids = {paper.canonical_id for paper in merged_papers}
    preserved_bundles = [
        bundle
        for bundle in existing_bundles
        if bundle.canonical_id in active_canonical_ids and bundle.canonical_id not in affected_canonical_ids
    ]
    return (
        merged_raw_pages,
        NormalizedCatalog(papers=merged_papers, review_queue=merged_review_queue),
        preserved_bundles,
        affected_canonical_ids,
    )


def filter_catalog_by_canonical_ids(catalog: NormalizedCatalog, canonical_ids: set[str]) -> NormalizedCatalog:
    return NormalizedCatalog(
        papers=[paper for paper in catalog.papers if paper.canonical_id in canonical_ids],
        review_queue=[item for item in catalog.review_queue if item.normalized_candidate in canonical_ids or item.raw_category in canonical_ids],
    )


def _load_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _load_raw_pages(path: Path) -> list[SourceExamPage]:
    pages = []
    for item in _load_json(path):
        pages.append(
            SourceExamPage(
                source_exam_id=item["source_exam_id"],
                year_ad=item["year_ad"],
                year_roc=item["year_roc"],
                exam_name_raw=item["exam_name_raw"],
                attachments=[ExamAttachment(**attachment) for attachment in item.get("attachments", [])],
                papers=[
                    ParsedPaper(
                        category_raw=paper["category_raw"],
                        category_code=paper["category_code"],
                        subject_code=paper["subject_code"],
                        subject_name_raw=paper["subject_name_raw"],
                        files=paper.get("files", {}),
                        mirror_files=paper.get("mirror_files", {}),
                    )
                    for paper in item.get("papers", [])
                ],
            )
        )
    return pages


def _load_catalog(papers_path: Path, review_queue_path: Path) -> NormalizedCatalog:
    papers = [NormalizedPaper(**paper) for paper in _load_json(papers_path)]
    review_queue = [ReviewItem(**item) for item in _load_json(review_queue_path)]
    return NormalizedCatalog(papers=papers, review_queue=review_queue)


def _load_bundles(path: Path) -> list[BundleAsset]:
    return [BundleAsset(**bundle) for bundle in _load_json(path)]


def _load_failures(path: Path) -> list[SyncFailure]:
    return [SyncFailure(**failure) for failure in _load_json(path)]
