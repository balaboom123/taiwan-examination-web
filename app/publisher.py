from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import TypeVar
from urllib.parse import quote

from app.bundler import build_bundles
from app.manifest import SourceManifest, write_source_manifest
from app.models import AliasRule, BundleAsset, NormalizedCatalog, NormalizedPaper, SourceExamPage, SyncFailure, to_plain_data
from app.paths import provider_paths, site_paths
from app.release_tags import assign_release_tags
from app.site_registry import get_site_config
from app.state import filter_catalog_by_canonical_ids, load_provider_state, load_site_bundles

T = TypeVar("T")


def _write_split_by_year(directory: Path, items: list[T], year_of: Callable[[T], int]) -> dict[int, list[T]]:
    directory.mkdir(parents=True, exist_ok=True)
    by_year: dict[int, list[T]] = {}
    for item in items:
        by_year.setdefault(year_of(item), []).append(item)
    existing = {int(f.stem) for f in directory.glob("*.json") if f.stem.isdigit()}
    for year_ad, year_items in sorted(by_year.items()):
        (directory / f"{year_ad}.json").write_text(
            json.dumps(to_plain_data(year_items), ensure_ascii=False), encoding="utf-8"
        )
    for stale_year in existing - by_year.keys():
        (directory / f"{stale_year}.json").unlink(missing_ok=True)
    return by_year


def write_data_files(
    data_dir: Path,
    raw_pages: list[SourceExamPage],
    normalized: NormalizedCatalog,
    aliases: list[AliasRule],
    bundles: list[BundleAsset],
    failures: list[SyncFailure],
) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    _write_split_by_year(data_dir / "exams", raw_pages, lambda page: page.year_ad)
    _write_split_by_year(data_dir / "papers", normalized.papers, lambda paper: paper.year_roc + 1911)
    for legacy in ("exams.raw.json", "papers.json"):
        (data_dir / legacy).unlink(missing_ok=True)
    (data_dir / "bundles.json").write_text(json.dumps(to_plain_data(bundles), ensure_ascii=False, indent=2), encoding="utf-8")
    (data_dir / "review-queue.json").write_text(
        json.dumps(to_plain_data(normalized.review_queue), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (data_dir / "sync-failures.json").write_text(
        json.dumps(to_plain_data(failures), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (data_dir / "aliases.json").write_text(json.dumps({"rules": to_plain_data(aliases)}, ensure_ascii=False, indent=2), encoding="utf-8")
    release_assets = [
        {
            "storage_key": bundle.storage_key,
            "asset_name": bundle.asset_name,
            "checksum": bundle.checksum,
            "legacy_asset_names": bundle.legacy_asset_names,
        }
        for bundle in bundles
    ]
    (data_dir / "release-assets.json").write_text(
        json.dumps(release_assets, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_provider_state(
    provider,
    raw_pages: list[SourceExamPage],
    normalized: NormalizedCatalog,
    aliases: list[AliasRule],
    failures: list[SyncFailure],
    manifest: SourceManifest | None,
) -> None:
    provider.data_dir.mkdir(parents=True, exist_ok=True)
    _write_split_by_year(provider.exams_dir, raw_pages, lambda page: page.year_ad)
    _write_split_by_year(provider.papers_dir, normalized.papers, lambda paper: paper.year_roc + 1911)
    provider.review_queue_path.write_text(
        json.dumps(to_plain_data(normalized.review_queue), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    provider.sync_failures_path.write_text(
        json.dumps(to_plain_data(failures), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    provider.aliases_path.write_text(
        json.dumps({"rules": to_plain_data(aliases)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if manifest is not None:
        write_source_manifest(provider.source_manifest_path, manifest)


def write_site_state(
    site,
    bundles: list[BundleAsset],
    frontend_bundles: list[dict],
    lootlabs_manifest: dict | None,
) -> None:
    site.data_dir.mkdir(parents=True, exist_ok=True)
    site.bundles_path.write_text(
        json.dumps(
            {"schema_version": 1, "site_id": site.site_id, "bundles": to_plain_data(bundles)},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    site.release_assets_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "site_id": site.site_id,
                "assets": [
                    {
                        "release_tag": bundle.release_tag,
                        "storage_key": bundle.storage_key,
                        "asset_name": bundle.asset_name,
                        "checksum": bundle.checksum,
                        "legacy_asset_names": bundle.legacy_asset_names,
                    }
                    for bundle in bundles
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    site.frontend_bundles_path.write_text(
        json.dumps(
            {"schema_version": 1, "site_id": site.site_id, "bundles": frontend_bundles},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    if lootlabs_manifest is not None:
        site.lootlabs_manifest_path.write_text(json.dumps(lootlabs_manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_bundle_download_urls(
    normalized: NormalizedCatalog,
    bundles: list[BundleAsset],
    *,
    repository: str,
) -> tuple[NormalizedCatalog, list[BundleAsset], list[dict]]:
    updated_bundles: list[BundleAsset] = []
    bundle_index: dict[str, BundleAsset] = {}
    for bundle in bundles:
        download_url = ""
        if repository and bundle.release_tag:
            download_url = f"https://github.com/{repository}/releases/download/{bundle.release_tag}/{quote(bundle.asset_name)}"
        updated_bundle = replace(bundle, download_url=download_url)
        updated_bundles.append(updated_bundle)
        bundle_index[updated_bundle.canonical_id] = updated_bundle

    updated_papers = [
        replace(
            paper,
            download_url_bundle=bundle_index.get(paper.canonical_id).download_url
            if paper.canonical_id in bundle_index
            else "",
        )
        for paper in normalized.papers
    ]

    frontend_bundles = [
        {
            "id": bundle.canonical_id,
            "name": bundle.canonical_name,
            "years": bundle.years,
            "fileCount": bundle.file_count,
            "url": bundle.download_url,
        }
        for bundle in updated_bundles
    ]
    return (
        NormalizedCatalog(papers=updated_papers, review_queue=normalized.review_queue),
        updated_bundles,
        frontend_bundles,
    )


def _site_bundle_storage_key(site_id: str, asset_name: str) -> str:
    return f"bundles/sites/{site_id}/{asset_name}"


def _site_scoped_bundles(site_id: str, bundles: list[BundleAsset]) -> list[BundleAsset]:
    return [replace(bundle, storage_key=_site_bundle_storage_key(site_id, bundle.asset_name)) for bundle in bundles]


def _format_bundle_failures(failures: list[SyncFailure]) -> str:
    details = []
    for failure in failures:
        parts = [failure.stage, failure.source_exam_id]
        if failure.paper_code:
            parts.append(failure.paper_code)
        if failure.file_type:
            parts.append(failure.file_type)
        details.append(f"{' '.join(parts)}: {failure.message}")
    return "\n".join(details)


def publish_site(
    repo_root: Path,
    *,
    site_id: str,
    repository: str,
    affected_canonical_ids: set[str] | None = None,
    canonical_aliases: dict[str, list[str]] | None = None,
) -> tuple[NormalizedCatalog, list[BundleAsset]]:
    site_config = get_site_config(site_id)
    aggregated_papers: list[NormalizedPaper] = []
    aggregated_review_queue = []
    for provider_id in site_config.provider_ids:
        provider = provider_paths(repo_root, provider_id)
        if not provider.data_dir.exists():
            if provider_id in site_config.required_provider_ids:
                raise ValueError(f"Missing provider state for {provider_id}: expected {provider.data_dir}")
            continue
        _raw_pages, provider_catalog, _failures = load_provider_state(provider)
        aggregated_papers.extend(provider_catalog.papers)
        aggregated_review_queue.extend(provider_catalog.review_queue)

    normalized = NormalizedCatalog(papers=aggregated_papers, review_queue=aggregated_review_queue)
    site = site_paths(repo_root, site_id)
    if affected_canonical_ids is not None and not site.bundles_path.exists():
        raise ValueError(f"Partial publish requires existing site bundle metadata: expected {site.bundles_path}")
    existing_bundles = load_site_bundles(site)
    if affected_canonical_ids is None:
        preserved_bundles: list[BundleAsset] = []
        rebuild_catalog = normalized
    else:
        active_canonical_ids = {paper.canonical_id for paper in normalized.papers}
        preserved_bundles = [
            bundle
            for bundle in existing_bundles
            if bundle.canonical_id in active_canonical_ids and bundle.canonical_id not in affected_canonical_ids
        ]
        rebuild_catalog = filter_catalog_by_canonical_ids(normalized, affected_canonical_ids)

    bundle_result = build_bundles(
        bundle_dir=site.bundle_dir,
        mirror_dir=repo_root / "mirror",
        normalized=rebuild_catalog,
        bundle_base_url="",
        canonical_aliases=canonical_aliases,
        min_years=site_config.public_min_years,
        min_years_by_canonical_prefix=site_config.public_min_years_by_canonical_prefix,
    )
    if bundle_result.failures:
        raise ValueError(_format_bundle_failures(bundle_result.failures))
    site_scoped_bundles = sorted(
        [*preserved_bundles, *_site_scoped_bundles(site_id, bundle_result.bundles)],
        key=lambda bundle: bundle.canonical_id,
    )
    tagged_bundles = assign_release_tags(
        release_tag_prefix=site_config.release_tag_prefix,
        existing_bundles=existing_bundles,
        bundles=site_scoped_bundles,
        max_assets_per_release=site_config.release_shard_size,
    )
    normalized_with_urls, bundles_with_urls, frontend_bundles = apply_bundle_download_urls(
        normalized,
        tagged_bundles,
        repository=repository,
    )
    write_site_state(
        site,
        bundles_with_urls,
        frontend_bundles,
        lootlabs_manifest=None,
    )
    return normalized_with_urls, bundles_with_urls
