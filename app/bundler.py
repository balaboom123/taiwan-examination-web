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


def _load_existing_entries_by_canonical(bundle_dir: Path) -> dict[str, dict[str, bytes]]:
    existing_entries: dict[str, dict[str, bytes]] = {}
    for archive_path in sorted(bundle_dir.glob("*.zip")):
        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                if "bundle.json" not in archive.namelist():
                    continue
                manifest = json.loads(archive.read("bundle.json").decode("utf-8"))
                canonical_id = manifest.get("canonical_id")
                if not canonical_id:
                    continue
                entries = existing_entries.setdefault(canonical_id, {})
                for name in archive.namelist():
                    if name != "bundle.json":
                        entries[name] = archive.read(name)
        except (OSError, ValueError, zipfile.BadZipFile):
            continue
    return existing_entries


def build_bundles(
    bundle_dir: Path,
    mirror_dir: Path,
    normalized: NormalizedCatalog,
    bundle_base_url: str,
) -> BundleBuildResult:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    existing_entries_by_canonical = _load_existing_entries_by_canonical(bundle_dir)
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

        existing_entries = dict(existing_entries_by_canonical.get(canonical_id, {}))

        included_papers: list[NormalizedPaper] = []
        included_years: set[int] = set()
        file_count = 0
        download_url = f"{bundle_base_url.rstrip('/')}/{asset_name}" if bundle_base_url else ""
        for paper in papers:
            paper.download_url_bundle = ""

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

        for paper in included_papers:
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
