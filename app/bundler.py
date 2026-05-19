from __future__ import annotations

import json
import zipfile
from pathlib import Path

from app.models import BundleAsset, BundleBuildResult, NormalizedCatalog, NormalizedPaper, SyncFailure, to_plain_data


def _safe_segment(value: str) -> str:
    cleaned = (value or "").strip()
    for token in ('\\', '/', ':', '*', '?', '"', '<', '>', '|'):
        cleaned = cleaned.replace(token, "_")
    return cleaned or "unknown"


def _bundle_arcname(paper: NormalizedPaper) -> str:
    suffix = Path(paper.storage_key).suffix or ".bin"
    return "/".join(
        [
            str(paper.year_roc),
            paper.source_exam_id or "unknown-exam",
            _safe_segment(paper.category_raw or paper.exam_name_raw),
            f"{paper.subject_code}_{_safe_segment(paper.subject_name_raw)}",
            f"{paper.file_type}{suffix}",
        ]
    )


def build_bundles(
    bundle_dir: Path,
    mirror_dir: Path,
    normalized: NormalizedCatalog,
    bundle_base_url: str,
) -> BundleBuildResult:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[NormalizedPaper]] = {}
    for paper in normalized.papers:
        grouped.setdefault(paper.canonical_id, []).append(paper)

    bundle_assets: list[BundleAsset] = []
    failures: list[SyncFailure] = []
    for canonical_id, papers in sorted(grouped.items()):
        canonical_name = papers[0].canonical_name
        bundle_name = canonical_id if not canonical_id.startswith("canonical-") else canonical_name
        asset_name = f"{_safe_segment(bundle_name)}.zip"
        storage_key = f"bundles/{asset_name}"
        bundle_path = bundle_dir / asset_name
        years = sorted({paper.year_roc for paper in papers}, reverse=True)
        ordered = sorted(
            papers,
            key=lambda item: (-item.year_roc, item.source_exam_id, item.category_code, item.subject_code, item.file_type),
        )

        existing_entries: dict[str, bytes] = {}
        if bundle_path.exists():
            with zipfile.ZipFile(bundle_path, "r") as previous_archive:
                for name in previous_archive.namelist():
                    if name != "bundle.json":
                        existing_entries[name] = previous_archive.read(name)

        included_papers: list[NormalizedPaper] = []
        included_years: set[int] = set()
        file_count = 0
        download_url = f"{bundle_base_url.rstrip('/')}/{asset_name}" if bundle_base_url else ""

        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for paper in ordered:
                arcname = _bundle_arcname(paper)
                source_path = mirror_dir / Path(paper.storage_key) if paper.storage_key else None
                if source_path and source_path.exists():
                    archive.write(source_path, arcname=arcname)
                    included_papers.append(paper)
                    included_years.add(paper.year_roc)
                    file_count += 1
                    continue
                if arcname in existing_entries:
                    archive.writestr(arcname, existing_entries[arcname])
                    included_papers.append(paper)
                    included_years.add(paper.year_roc)
                    file_count += 1
                    continue
                failures.append(
                    SyncFailure(
                        stage="bundle",
                        source_exam_id=paper.source_exam_id,
                        year_roc=paper.year_roc,
                        paper_code=paper.paper_code,
                        file_type=paper.file_type,
                        url=paper.download_url_source,
                        message=f"Missing mirrored file for bundle entry: {paper.storage_key}",
                    )
                )

            if not included_papers:
                archive.writestr(
                    "bundle.json",
                    json.dumps(
                        {
                            "canonical_id": canonical_id,
                            "canonical_name": canonical_name,
                            "years": [],
                            "file_count": 0,
                            "papers": [],
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
            else:
                manifest = {
                    "canonical_id": canonical_id,
                    "canonical_name": canonical_name,
                    "years": sorted(included_years, reverse=True),
                    "file_count": file_count,
                    "papers": to_plain_data(included_papers),
                }
                archive.writestr("bundle.json", json.dumps(manifest, ensure_ascii=False, indent=2))

        if not included_papers:
            bundle_path.unlink(missing_ok=True)
            continue

        for paper in papers:
            paper.download_url_bundle = download_url

        bundle_assets.append(
            BundleAsset(
                canonical_id=canonical_id,
                canonical_name=canonical_name,
                years=sorted(included_years, reverse=True),
                file_count=file_count,
                storage_key=storage_key,
                asset_name=asset_name,
                download_url=download_url,
            )
        )
    return BundleBuildResult(bundles=bundle_assets, failures=failures)
