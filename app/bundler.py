from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from collections.abc import Callable
from pathlib import Path

from app.normalizer import hashed_fallback_canonical_id, legacy_fallback_canonical_id
from app.models import BundleAsset, BundleBuildResult, FILE_TYPE_LABELS, NormalizedCatalog, NormalizedPaper, SyncFailure, to_plain_data

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def _safe_segment(value: str, max_length: int | None = None) -> str:
    cleaned = (value or "").strip()
    cleaned = "".join("_" if char in '\\/:*?"<>|' or ord(char) < 32 else char for char in cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.rstrip(" .")
    if max_length is not None:
        cleaned = cleaned[:max_length].rstrip(" .")
    if not cleaned or not cleaned.strip(" ._-"):
        return "unknown"
    stem = Path(cleaned).stem.upper()
    if stem in WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned


def _bundle_arcname(paper: NormalizedPaper) -> str:
    suffix = Path(paper.storage_key).suffix or ".bin"
    file_name = "_".join(
        [
            _safe_segment(paper.category_code or "category", max_length=24),
            _safe_segment(paper.subject_code or "subject", max_length=24),
            _safe_segment(paper.subject_name_raw or "subject", max_length=60),
            _safe_segment(FILE_TYPE_LABELS.get(paper.file_type, paper.file_type or "file"), max_length=20),
        ]
    )
    return f"{paper.year_roc}/{file_name}{suffix}"


def _resolve_arcnames(ordered: list[NormalizedPaper]) -> list[str]:
    base = [_bundle_arcname(p) for p in ordered]
    counts: dict[str, int] = {}
    for name in base:
        counts[name] = counts.get(name, 0) + 1
    resolved: list[str] = []
    for i, paper in enumerate(ordered):
        name = base[i]
        if counts[name] > 1:
            suffix = Path(paper.storage_key).suffix or ".bin"
            stem = name[: -len(suffix)]
            exam_tag = _safe_segment(paper.source_exam_id or "unknown", max_length=20)
            name = f"{stem}_{exam_tag}{suffix}"
        resolved.append(name)
    used: set[str] = set()
    final: list[str] = []
    for name in resolved:
        if name not in used:
            used.add(name)
            final.append(name)
        else:
            counter = 2
            while True:
                dot = name.rfind(".")
                candidate = f"{name[:dot]}_{counter}{name[dot:]}" if dot > 0 else f"{name}_{counter}"
                if candidate not in used:
                    used.add(candidate)
                    final.append(candidate)
                    break
                counter += 1
    return final


def _code_bundle_arcname(paper: NormalizedPaper) -> str:
    suffix = Path(paper.storage_key).suffix or ".bin"
    file_name = "_".join(
        [
            _safe_segment(paper.category_code or "category"),
            _safe_segment(paper.subject_code or "subject"),
            _safe_segment(paper.file_type or "file"),
        ]
    )
    return "/".join([str(paper.year_roc), _safe_segment(paper.source_exam_id or "unknown-exam"), f"{file_name}{suffix}"])


def _legacy_bundle_arcname(paper: NormalizedPaper) -> str:
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


def _paper_bundle_key(paper: NormalizedPaper | dict[str, object]) -> tuple[str, str, str, str]:
    if isinstance(paper, dict):
        return tuple(str(paper.get(field, "")) for field in ("source_exam_id", "category_code", "subject_code", "file_type"))
    return (paper.source_exam_id, paper.category_code, paper.subject_code, paper.file_type)


def _bundle_asset_name(canonical_id: str) -> str:
    stable = _safe_segment(canonical_id, max_length=80)
    return f"{stable}.zip"


def _bundle_download_url(bundle_base_url: str, asset_name: str) -> str:
    return ""


def _lookup_canonical_ids(canonical_id: str, canonical_name: str, canonical_alias_ids: list[str] | None = None) -> list[str]:
    lookup_ids: list[str] = []
    for alias_id in canonical_alias_ids or []:
        if alias_id != canonical_id and alias_id not in lookup_ids:
            lookup_ids.append(alias_id)
    hashed_fallback = hashed_fallback_canonical_id(canonical_name)
    legacy_id = legacy_fallback_canonical_id(canonical_name)
    for fallback_id in (legacy_id, hashed_fallback):
        if fallback_id != canonical_id and fallback_id not in lookup_ids:
            lookup_ids.append(fallback_id)
    if canonical_id not in lookup_ids:
        lookup_ids.append(canonical_id)
    return lookup_ids


def _legacy_asset_names(
    canonical_id: str,
    canonical_name: str,
    asset_name: str,
    canonical_alias_ids: list[str] | None = None,
) -> list[str]:
    names: list[str] = []
    friendly = _safe_segment(canonical_name, max_length=80)
    stable = _safe_segment(canonical_id, max_length=80)
    if friendly != "unknown":
        names.append(f"{friendly}__{stable}.zip")
    public_ids: list[str] = []
    public_ids.extend(canonical_alias_ids or [])
    hashed_fallback = hashed_fallback_canonical_id(canonical_name)
    if canonical_id == hashed_fallback:
        public_ids.append(legacy_fallback_canonical_id(canonical_name))
    public_ids.append(canonical_id)
    names.extend(f"{_safe_segment(public_id, max_length=80)}.zip" for public_id in public_ids)
    return [name for name in dict.fromkeys(names) if name != asset_name]


_EntryRef = tuple[Path, str]


def _resolve_entry_ref(ref: _EntryRef) -> bytes | None:
    archive_path, entry_name = ref
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            return zf.read(entry_name)
    except (OSError, ValueError, zipfile.BadZipFile, KeyError):
        return None


def _load_existing_entries_by_canonical(
    bundle_dir: Path,
    on_progress: Callable | None = None,
) -> tuple[dict[str, dict[str, _EntryRef]], dict[str, dict[tuple[str, str, str, str], _EntryRef]]]:
    existing_entries_by_name: dict[str, dict[str, _EntryRef]] = {}
    existing_entries_by_key: dict[str, dict[tuple[str, str, str, str], _EntryRef]] = {}
    archives = sorted(bundle_dir.glob("*.zip"))
    total = len(archives)
    for idx, archive_path in enumerate(archives, 1):
        if on_progress and (idx == 1 or idx % 500 == 0 or idx == total):
            on_progress(idx, total)
        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                names = archive.namelist()
                if "bundle.json" not in names:
                    continue
                manifest = json.loads(archive.read("bundle.json").decode("utf-8"))
                canonical_id = manifest.get("canonical_id")
                if not canonical_id:
                    continue
                entries_by_name = existing_entries_by_name.setdefault(canonical_id, {})
                for name in names:
                    if name != "bundle.json":
                        entries_by_name[name] = (archive_path, name)
                manifest_papers = manifest.get("papers", [])
                if isinstance(manifest_papers, list):
                    entries_by_key = existing_entries_by_key.setdefault(canonical_id, {})
                    for paper_data in manifest_papers:
                        if isinstance(paper_data, dict):
                            entry_name = paper_data.get("bundle_entry")
                            if not isinstance(entry_name, str) or entry_name not in entries_by_name:
                                continue
                            entries_by_key[_paper_bundle_key(paper_data)] = entries_by_name[entry_name]
        except (OSError, ValueError, zipfile.BadZipFile):
            continue
    return existing_entries_by_name, existing_entries_by_key


def _preserve_rewrite_sources(
    bundle_path: Path,
    existing_entries: dict[str, _EntryRef],
    existing_entries_by_key: dict[tuple[str, str, str, str], _EntryRef],
) -> tuple[dict[str, _EntryRef], dict[tuple[str, str, str, str], _EntryRef], Path | None]:
    refs = [*existing_entries.values(), *existing_entries_by_key.values()]
    if not any(archive_path == bundle_path for archive_path, _entry_name in refs):
        return existing_entries, existing_entries_by_key, None

    preserved_path = bundle_path.with_name(f".{bundle_path.name}.preserve")
    shutil.copyfile(bundle_path, preserved_path)

    def rewrite(ref: _EntryRef) -> _EntryRef:
        archive_path, entry_name = ref
        if archive_path == bundle_path:
            return preserved_path, entry_name
        return ref

    return (
        {name: rewrite(ref) for name, ref in existing_entries.items()},
        {key: rewrite(ref) for key, ref in existing_entries_by_key.items()},
        preserved_path,
    )


def build_bundles(
    bundle_dir: Path,
    mirror_dir: Path,
    normalized: NormalizedCatalog,
    bundle_base_url: str,
    canonical_aliases: dict[str, list[str]] | None = None,
    on_progress: Callable | None = None,
    on_load_progress: Callable | None = None,
    min_years: int = 1,
) -> BundleBuildResult:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    existing_entries_by_canonical, existing_entries_by_paper_key = _load_existing_entries_by_canonical(bundle_dir, on_progress=on_load_progress)
    grouped: dict[str, list[NormalizedPaper]] = {}
    for paper in normalized.papers:
        grouped.setdefault(paper.canonical_id, []).append(paper)

    total_groups = len(grouped)
    bundle_assets: list[BundleAsset] = []
    failures: list[SyncFailure] = []
    for group_index, (canonical_id, papers) in enumerate(sorted(grouped.items()), 1):
        canonical_name = papers[0].canonical_name
        if min_years > 1:
            distinct_years = {p.year_roc for p in papers}
            if len(distinct_years) < min_years:
                if on_progress:
                    on_progress(group_index, total_groups, f"[skipped] {canonical_name}", 0)
                continue
        asset_name = _bundle_asset_name(canonical_id)
        compatibility_ids = list(canonical_aliases.get(canonical_id, [])) if canonical_aliases else []
        for fallback_id in (legacy_fallback_canonical_id(canonical_name), hashed_fallback_canonical_id(canonical_name)):
            if fallback_id != canonical_id and fallback_id in existing_entries_by_canonical and fallback_id not in compatibility_ids:
                compatibility_ids.append(fallback_id)
        legacy_asset_names = _legacy_asset_names(canonical_id, canonical_name, asset_name, compatibility_ids)
        storage_key = f"bundles/{asset_name}"
        bundle_path = bundle_dir / asset_name

        existing_entries: dict[str, _EntryRef] = {}
        existing_entries_by_key: dict[tuple[str, str, str, str], _EntryRef] = {}
        for lookup_id in _lookup_canonical_ids(canonical_id, canonical_name, compatibility_ids):
            existing_entries.update(existing_entries_by_canonical.get(lookup_id, {}))
            existing_entries_by_key.update(existing_entries_by_paper_key.get(lookup_id, {}))

        included_papers: list[NormalizedPaper] = []
        bundle_entries_by_paper_key: dict[tuple[str, str, str, str], str] = {}
        included_years: set[int] = set()
        file_count = 0
        download_url = _bundle_download_url(bundle_base_url, asset_name)
        for paper in papers:
            paper.download_url_bundle = ""

        ordered = sorted(
            papers,
            key=lambda item: (-item.year_roc, item.source_exam_id, item.category_code, item.subject_code, item.file_type),
        )
        resolved_names = _resolve_arcnames(ordered)
        existing_entries, existing_entries_by_key, preserved_archive = _preserve_rewrite_sources(
            bundle_path,
            existing_entries,
            existing_entries_by_key,
        )
        try:
            with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for paper, arcname in zip(ordered, resolved_names):
                    source_path = mirror_dir / Path(paper.storage_key) if paper.storage_key else None
                    if source_path and source_path.exists():
                        archive.write(source_path, arcname=arcname)
                        included_papers.append(paper)
                        bundle_entries_by_paper_key[_paper_bundle_key(paper)] = arcname
                        included_years.add(paper.year_roc)
                        file_count += 1
                        continue
                    legacy_arcname = _legacy_bundle_arcname(paper)
                    existing_ref = existing_entries.get(arcname)
                    if existing_ref is None:
                        base_arcname = _bundle_arcname(paper)
                        if base_arcname != arcname:
                            existing_ref = existing_entries.get(base_arcname)
                    if existing_ref is None:
                        existing_ref = existing_entries.get(_code_bundle_arcname(paper))
                    if existing_ref is None:
                        existing_ref = existing_entries.get(legacy_arcname)
                    if existing_ref is None:
                        existing_ref = existing_entries_by_key.get(_paper_bundle_key(paper))
                    existing_bytes = _resolve_entry_ref(existing_ref) if existing_ref is not None else None
                    if existing_bytes is not None:
                        archive.writestr(arcname, existing_bytes)
                        included_papers.append(paper)
                        bundle_entries_by_paper_key[_paper_bundle_key(paper)] = arcname
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
                    manifest_papers = []
                    for paper in included_papers:
                        paper_data = to_plain_data(paper)
                        paper_data["bundle_entry"] = bundle_entries_by_paper_key[_paper_bundle_key(paper)]
                        manifest_papers.append(paper_data)
                    manifest = {
                        "canonical_id": canonical_id,
                        "canonical_name": canonical_name,
                        "years": sorted(included_years, reverse=True),
                        "file_count": file_count,
                        "papers": manifest_papers,
                    }
                    archive.writestr("bundle.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        finally:
            if preserved_archive is not None:
                preserved_archive.unlink(missing_ok=True)

        if not included_papers:
            bundle_path.unlink(missing_ok=True)
            if on_progress:
                on_progress(group_index, total_groups, asset_name, 0)
            continue

        for paper in included_papers:
            paper.download_url_bundle = download_url

        digest = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
        bundle_assets.append(
            BundleAsset(
                canonical_id=canonical_id,
                canonical_name=canonical_name,
                years=sorted(included_years, reverse=True),
                file_count=file_count,
                storage_key=storage_key,
                asset_name=asset_name,
                release_tag="",
                download_url=download_url,
                checksum=digest,
                legacy_asset_names=legacy_asset_names,
            )
        )
        if on_progress:
            on_progress(group_index, total_groups, asset_name, file_count)
    return BundleBuildResult(bundles=bundle_assets, failures=failures)
