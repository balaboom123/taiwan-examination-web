from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

from app.bundler import build_bundles
from app.crawler import year_ad_from_code
from app.lootlabs import LootLabsError, load_lootlabs_settings_from_env, sync_lootlabs_manifest
from app.manifest import load_source_manifest, source_manifest_from_data, write_source_manifest
from app.models import BundleAsset, NormalizedCatalog, NormalizedPaper
from app.normalizer import load_alias_rules, renormalize_catalog
from app.publisher import build_site, publish_site, write_data_files
from app.probe import probe_latest
from app.providers.base import SourceProvider
from app.providers.registry import get_provider
from app.state import filter_catalog_by_canonical_ids, load_existing_state, merge_incremental_state, merge_targeted_state
from app.sync import sync_exam_pages
from app.storage import MirrorStore


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _discover_years(client: SourceProvider, years: list[int] | None) -> list[int]:
    if years:
        return years
    return client.discover_available_years()


def _latest_years(client: SourceProvider, count: int) -> list[int]:
    return sorted(client.discover_available_years(), reverse=True)[:count]


def _provider_for_args(args: argparse.Namespace, client: SourceProvider | None = None) -> SourceProvider:
    return client or get_provider(getattr(args, "provider", None) or "moex")


def _provider_id_for_args(args: argparse.Namespace, client: SourceProvider) -> str:
    return getattr(client, "provider_id", getattr(args, "provider", None) or "moex")


def _provider_for_targeted_probe(
    args: argparse.Namespace,
    probe: dict[str, object],
    client: SourceProvider | None = None,
) -> tuple[SourceProvider, str]:
    probe_provider_id = str(probe.get("provider_id") or "")
    if client is not None:
        client_provider_id = _provider_id_for_args(args, client)
        if probe_provider_id and client_provider_id != probe_provider_id:
            raise ValueError(
                f"Probe provider mismatch: probe declares {probe_provider_id}, but targeted sync client is {client_provider_id}"
            )
        return client, probe_provider_id or client_provider_id

    if probe_provider_id:
        arg_provider_id = getattr(args, "provider", None)
        if arg_provider_id is not None and arg_provider_id != probe_provider_id:
            raise ValueError(
                f"Probe provider mismatch: probe declares {probe_provider_id}, but --provider is {arg_provider_id}"
            )
        return get_provider(probe_provider_id), probe_provider_id

    resolved_client = _provider_for_args(args, client)
    return resolved_client, _provider_id_for_args(args, resolved_client)


def _supports_probe_manifest(provider_id: str, client: SourceProvider) -> bool:
    return provider_id == "moex" or (
        callable(getattr(client, "build_probe_year_url", None))
        and callable(getattr(client, "build_probe_exam_url", None))
    )


def _targeted_exam_codes_from_probe(probe: dict[str, object], provider_id: str) -> list[tuple[str, int]]:
    changed_exam_codes = list(probe.get("changed_exam_codes", []))
    exam_years = {code: int(year) for code, year in probe.get("exam_years", {}).items()}
    resolved_exam_codes: list[tuple[str, int]] = []
    missing_years: list[str] = []
    for code in changed_exam_codes:
        year_ad = exam_years.get(code)
        if year_ad is None:
            if provider_id == "moex":
                year_ad = year_ad_from_code(code)
            else:
                missing_years.append(code)
                continue
        resolved_exam_codes.append((code, year_ad))
    if missing_years:
        joined_codes = ", ".join(sorted(missing_years))
        raise ValueError(f"Probe exam_years is required for provider {provider_id}: {joined_codes}")
    return resolved_exam_codes


def command_discover(args: argparse.Namespace) -> int:
    client = _provider_for_args(args)
    years = _discover_years(client, args.years)
    payload = []
    for year in years:
        payload.append(
            {
                "year_ad": year,
                "year_roc": year - 1911,
                "exams": [exam.__dict__ for exam in client.discover_exams(year)],
            }
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def command_build_bundles(args: argparse.Namespace) -> int:
    print("Loading existing data...", flush=True)
    existing_raw_pages, existing_catalog, _, existing_failures = load_existing_state(args.data_dir)
    aliases = load_alias_rules(args.aliases)
    existing_catalog = renormalize_catalog(existing_catalog, aliases)
    groups = len({p.canonical_id for p in existing_catalog.papers})
    print(f"Found {len(existing_catalog.papers)} papers in {groups} exam groups", flush=True)
    rebuild_result = build_bundles(
        bundle_dir=args.bundle_dir,
        mirror_dir=args.mirror_dir,
        normalized=existing_catalog,
        bundle_base_url=args.bundle_base_url,
        on_progress=lambda i, total, name, count: print(f"  Building [{i}/{total}] {name} ({count} files)", flush=True),
        on_load_progress=lambda i, total: print(f"  Scanning existing bundles... {i}/{total}", flush=True),
        min_years=args.min_years,
    )
    bundles = rebuild_result.bundles
    failures = existing_failures + rebuild_result.failures
    write_data_files(args.data_dir, existing_raw_pages, existing_catalog, aliases, bundles, failures)
    build_site(args.site_dir, existing_catalog, bundles)
    print(f"Built {len(bundles)} bundles, {len(rebuild_result.failures)} bundle failures", flush=True)
    if failures:
        print(f"{len(failures)} total failures (see data/sync-failures.json)", flush=True)
        return 1
    return 0


def command_build_site(args: argparse.Namespace) -> int:
    papers_dir = args.data_dir / "papers"
    papers: list[dict] = []
    if papers_dir.is_dir():
        for f in sorted(papers_dir.glob("*.json")):
            papers.extend(json.loads(f.read_text(encoding="utf-8")))
    bundles_path = args.data_dir / "bundles.json"
    bundles_data = json.loads(bundles_path.read_text(encoding="utf-8")) if bundles_path.exists() else []
    catalog = NormalizedCatalog(papers=[NormalizedPaper(**paper) for paper in papers], review_queue=[])
    bundles = [BundleAsset(**bundle) for bundle in bundles_data]
    build_site(args.site_dir, catalog, bundles)
    return 0


def _load_lootlabs_bundles(data_dir: Path) -> list[BundleAsset]:
    bundles_path = data_dir / "bundles.json"
    if not bundles_path.exists():
        raise LootLabsError(f"{bundles_path} is required")
    try:
        bundles_data = json.loads(bundles_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LootLabsError(f"Failed to read {bundles_path}: {exc}") from exc
    if not isinstance(bundles_data, list):
        raise LootLabsError(f"{bundles_path} must contain a JSON list of bundles")
    try:
        return [BundleAsset(**bundle) for bundle in bundles_data]
    except TypeError as exc:
        raise LootLabsError(f"Invalid bundle entry in {bundles_path}") from exc


def command_sync_lootlabs(args: argparse.Namespace) -> int:
    try:
        bundles = _load_lootlabs_bundles(args.data_dir)
        api_key, settings = load_lootlabs_settings_from_env()
        sync_lootlabs_manifest(
            bundles=bundles,
            manifest_path=args.manifest,
            api_key=api_key,
            settings=settings,
        )
    except LootLabsError as exc:
        print(str(exc), flush=True)
        return 1
    return 0


def run_probe_latest(args: argparse.Namespace, client: SourceProvider | None = None, now: str | None = None) -> int:
    probe_client = _provider_for_args(args, client)
    generated_at = now or datetime.now().astimezone().isoformat()
    provider_id = _provider_id_for_args(args, probe_client)
    if not _supports_probe_manifest(provider_id, probe_client):
        print(f"probe-latest is not supported for provider {provider_id}: missing probe URL model", flush=True)
        return 1
    manifest = load_source_manifest(args.manifest, provider_id=_provider_id_for_args(args, probe_client))
    result = probe_latest(client=probe_client, manifest=manifest, year_window=args.years, now=generated_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result.to_output_data(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.write_manifest:
        write_source_manifest(args.manifest, result.updated_manifest)
    return 0


def _download_affected_bundles(bundle_dir: Path, existing_bundles: list[BundleAsset], affected_canonical_ids: set[str], release_tag: str) -> None:
    asset_names = []
    for bundle in existing_bundles:
        if bundle.canonical_id not in affected_canonical_ids:
            continue
        asset_names.extend([name for name in [bundle.asset_name, *bundle.legacy_asset_names] if name])
    if not asset_names:
        return
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for asset_name in sorted(set(asset_names)):
        if (bundle_dir / asset_name).exists():
            continue
        subprocess.run(["gh", "release", "download", release_tag, "--pattern", asset_name, "--dir", str(bundle_dir)], check=True)


def _write_probe_manifest_if_present(probe: dict[str, object], manifest_path: Path) -> None:
    updated_manifest = probe.get("updated_manifest")
    if isinstance(updated_manifest, dict):
        write_source_manifest(manifest_path, source_manifest_from_data(updated_manifest))


def _merge_bundle_lists(preserved: list[BundleAsset], rebuilt: list[BundleAsset]) -> list[BundleAsset]:
    canonical_order = {bundle.canonical_id: bundle for bundle in preserved}
    for bundle in rebuilt:
        canonical_order[bundle.canonical_id] = bundle
    return sorted(canonical_order.values(), key=lambda bundle: bundle.canonical_id)


def _print_failures(failures: list) -> None:
    for failure in failures:
        parts = [failure.stage, failure.source_exam_id]
        if failure.paper_code:
            parts.append(failure.paper_code)
        if failure.file_type:
            parts.append(failure.file_type)
        detail = " ".join(parts)
        print(f"{detail}: {failure.message}")
        if failure.url:
            print(f"  url: {failure.url}")


def run_sync_targeted(args: argparse.Namespace, client: SourceProvider | None = None) -> int:
    probe = json.loads(args.probe.read_text(encoding="utf-8"))
    if not probe.get("should_sync", False):
        return 0

    try:
        sync_client, provider_id = _provider_for_targeted_probe(args, probe, client)
    except ValueError as exc:
        print(str(exc), flush=True)
        return 1
    changed_exam_codes = list(probe.get("changed_exam_codes", []))
    removed_exam_ids = set(probe.get("removed_exam_codes", []))
    try:
        exam_codes = _targeted_exam_codes_from_probe(probe, provider_id)
    except ValueError as exc:
        print(str(exc), flush=True)
        return 1
    aliases = load_alias_rules(args.aliases)
    refreshed_raw_pages, refreshed_catalog, sync_failures = sync_exam_pages(
        client=sync_client,
        exam_codes=exam_codes,
        mirror_store=MirrorStore(args.mirror_dir),
        alias_rules=aliases,
        mirror_base_url="",
        download_attachments=args.download_attachments,
    )
    # Abort on any failure: targeted sync only handles known-changed exams, partial writes are not safe
    if sync_failures:
        _print_failures(sync_failures)
        return 1
    existing_raw_pages, existing_catalog, existing_bundles, existing_failures = load_existing_state(args.data_dir)
    refreshed_exam_ids = {page.source_exam_id for page in refreshed_raw_pages}
    raw_pages, normalized, preserved_bundles, affected_canonical_ids, canonical_aliases = merge_targeted_state(
        existing_raw_pages=existing_raw_pages,
        existing_catalog=existing_catalog,
        existing_bundles=existing_bundles,
        refreshed_raw_pages=refreshed_raw_pages,
        refreshed_catalog=refreshed_catalog,
        removed_exam_ids=removed_exam_ids,
    )
    if args.download_affected_bundles:
        _download_affected_bundles(args.bundle_dir, existing_bundles, affected_canonical_ids, args.release_tag)
    rebuild_result = build_bundles(
        bundle_dir=args.bundle_dir,
        mirror_dir=args.mirror_dir,
        normalized=filter_catalog_by_canonical_ids(normalized, affected_canonical_ids),
        bundle_base_url=args.bundle_base_url or args.mirror_base_url,
        canonical_aliases=canonical_aliases,
    )
    if rebuild_result.failures:
        _print_failures(rebuild_result.failures)
        return 1
    bundles = _merge_bundle_lists(preserved_bundles, rebuild_result.bundles)
    replaced_exam_ids = refreshed_exam_ids | removed_exam_ids
    failures = [failure for failure in existing_failures if failure.source_exam_id not in replaced_exam_ids]
    failures.extend(sync_failures)
    failures.extend(rebuild_result.failures)

    write_data_files(args.data_dir, raw_pages, normalized, aliases, bundles, failures)
    build_site(args.site_dir, normalized, bundles)
    _write_probe_manifest_if_present(probe, args.manifest)
    return 0


def command_sync(args: argparse.Namespace, client: SourceProvider | None = None) -> int:
    provider = _provider_for_args(args, client)
    provider_id = _provider_id_for_args(args, provider)
    if getattr(args, "write_manifest", False) and not _supports_probe_manifest(provider_id, provider):
        print(f"--write-manifest is not supported for provider {provider_id}: missing probe URL model", flush=True)
        return 1
    if getattr(args, "year_window", None):
        years = _latest_years(provider, args.year_window)
    else:
        years = _discover_years(provider, args.years)
    aliases = load_alias_rules(args.aliases)
    mirror_store = MirrorStore(args.mirror_dir)

    all_raw_pages: list = []
    all_papers: list = []
    all_review_queue: list = []
    all_sync_failures: list = []

    for year in years:
        exam_codes = [(exam.code, exam.year_ad) for exam in provider.discover_exams(year)]
        print(f"Syncing year {year} ({len(exam_codes)} exams)...")
        try:
            raw_pages_year, catalog_year, failures_year = sync_exam_pages(
                client=provider,
                exam_codes=exam_codes,
                mirror_store=mirror_store,
                alias_rules=aliases,
                mirror_base_url="",
                download_attachments=args.download_attachments,
            )
        except Exception as exc:
            print(f"Year {year}: failed with unexpected error: {exc}")
            continue
        all_raw_pages.extend(raw_pages_year)
        all_papers.extend(catalog_year.papers)
        all_review_queue.extend(catalog_year.review_queue)
        all_sync_failures.extend(failures_year)
        print(f"Year {year}: {len(raw_pages_year)} exams, {len(catalog_year.papers)} papers, {len(failures_year)} failures")

    refreshed_raw_pages = all_raw_pages
    refreshed_catalog = NormalizedCatalog(papers=all_papers, review_queue=all_review_queue)
    sync_failures = all_sync_failures

    incremental_mode = getattr(args, "year_window", None) is not None
    if incremental_mode:
        existing_raw_pages, existing_catalog, existing_bundles, existing_failures = load_existing_state(args.data_dir)
        failed_exam_ids = {failure.source_exam_id for failure in sync_failures}
        safe_raw_pages = [page for page in refreshed_raw_pages if page.source_exam_id not in failed_exam_ids]
        safe_catalog = NormalizedCatalog(
            papers=[p for p in refreshed_catalog.papers if p.source_exam_id not in failed_exam_ids],
            review_queue=[r for r in refreshed_catalog.review_queue if r.source_exam_id not in failed_exam_ids],
        )
        raw_pages, normalized, preserved_bundles, affected_canonical_ids, canonical_aliases = merge_incremental_state(
            existing_raw_pages=existing_raw_pages,
            existing_catalog=existing_catalog,
            existing_bundles=existing_bundles,
            refreshed_raw_pages=safe_raw_pages,
            refreshed_catalog=safe_catalog,
        )
        rebuild_result = build_bundles(
            bundle_dir=args.bundle_dir,
            mirror_dir=args.mirror_dir,
            normalized=filter_catalog_by_canonical_ids(normalized, affected_canonical_ids),
            bundle_base_url=args.bundle_base_url or args.mirror_base_url,
            canonical_aliases=canonical_aliases,
        )
        if rebuild_result.failures:
            _print_failures(rebuild_result.failures)
            return 1
        bundles = _merge_bundle_lists(preserved_bundles, rebuild_result.bundles)
        refreshed_exam_ids = {page.source_exam_id for page in refreshed_raw_pages}
        failures = [failure for failure in existing_failures if failure.source_exam_id not in refreshed_exam_ids]
        failures.extend(sync_failures)
        failures.extend(rebuild_result.failures)
    else:
        raw_pages = refreshed_raw_pages
        normalized = refreshed_catalog
        rebuild_result = build_bundles(
            bundle_dir=args.bundle_dir,
            mirror_dir=args.mirror_dir,
            normalized=normalized,
            bundle_base_url=args.bundle_base_url or args.mirror_base_url,
        )
        bundles = rebuild_result.bundles
        failures = sync_failures + rebuild_result.failures

    write_data_files(args.data_dir, raw_pages, normalized, aliases, bundles, failures)
    build_site(args.site_dir, normalized, bundles)
    if getattr(args, "write_manifest", False) and not failures:
        manifest = load_source_manifest(args.manifest, provider_id=provider_id)
        result = probe_latest(client=provider, manifest=manifest, year_window=len(years), now=datetime.now().astimezone().isoformat())
        write_source_manifest(args.manifest, result.updated_manifest)
    if failures:
        print(f"Completed with {len(failures)} failure(s). See data/sync-failures.json for details.")
        return 1
    return 0


def command_publish_site(args: argparse.Namespace) -> int:
    publish_site(args.repo_root, site_id=args.site_id, repository=args.repository)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app")
    subparsers = parser.add_subparsers(dest="command", required=True)
    repo_root = _default_repo_root()

    discover = subparsers.add_parser("discover", help="Discover available exams grouped by year.")
    discover.add_argument("--provider", default="moex")
    discover.add_argument("--years", nargs="*", type=int, default=None)
    discover.set_defaults(handler=command_discover)

    probe_parser = subparsers.add_parser("probe-latest", help="Probe recent source changes without downloading files.")
    probe_parser.add_argument("--provider", default="moex")
    probe_parser.add_argument("--years", type=int, default=2)
    probe_parser.add_argument("--manifest", type=Path, default=repo_root / "data" / "source-manifest.json")
    probe_parser.add_argument("--output", type=Path, default=repo_root / ".tmp" / "source-probe.json")
    probe_parser.add_argument("--write-manifest", action="store_true")
    probe_parser.set_defaults(handler=run_probe_latest)

    targeted = subparsers.add_parser("sync-targeted", help="Sync only changed exams from a probe output file.")
    targeted.add_argument("--probe", type=Path, default=repo_root / ".tmp" / "source-probe.json")
    targeted.add_argument("--data-dir", type=Path, default=repo_root / "data")
    targeted.add_argument("--site-dir", type=Path, default=repo_root / "site")
    targeted.add_argument("--mirror-dir", type=Path, default=repo_root / "mirror")
    targeted.add_argument("--bundle-dir", type=Path, default=repo_root / "bundles")
    targeted.add_argument("--aliases", type=Path, default=repo_root / "data" / "aliases.json")
    targeted.add_argument("--manifest", type=Path, default=repo_root / "data" / "source-manifest.json")
    targeted.add_argument("--bundle-base-url", default="")
    targeted.add_argument("--mirror-base-url", default="")
    targeted.add_argument("--download-attachments", action="store_true", default=False)
    targeted.add_argument("--download-affected-bundles", action="store_true", default=False)
    targeted.add_argument("--provider", default=None)
    targeted.add_argument("--site-id", default="default")
    targeted.add_argument("--release-tag", default="moex-bundles")
    targeted.set_defaults(handler=run_sync_targeted)

    for name in ("sync-full", "sync-incremental"):
        sync = subparsers.add_parser(name, help=f"{name} against the selected provider.")
        sync.add_argument("--data-dir", type=Path, default=repo_root / "data")
        sync.add_argument("--site-dir", type=Path, default=repo_root / "site")
        sync.add_argument("--mirror-dir", type=Path, default=repo_root / "mirror")
        sync.add_argument("--bundle-dir", type=Path, default=repo_root / "bundles")
        sync.add_argument("--aliases", type=Path, default=repo_root / "data" / "aliases.json")
        sync.add_argument("--manifest", type=Path, default=repo_root / "data" / "source-manifest.json")
        sync.add_argument("--bundle-base-url", default="")
        sync.add_argument("--mirror-base-url", default="")
        sync.add_argument("--download-attachments", action="store_true", default=False)
        sync.add_argument("--provider", default="moex")
        sync.add_argument("--site-id", default="default")
        sync.add_argument("--write-manifest", action="store_true", default=False)
        if name == "sync-full":
            sync.add_argument("--years", nargs="*", type=int, default=None)
        else:
            sync.add_argument("--years", dest="year_window", type=int, default=3)
        sync.set_defaults(handler=command_sync)

    build_bundles_parser = subparsers.add_parser("build-bundles", help="Rebuild ZIP bundles and site from existing local data (no network).")
    build_bundles_parser.add_argument("--data-dir", type=Path, default=repo_root / "data")
    build_bundles_parser.add_argument("--site-dir", type=Path, default=repo_root / "site")
    build_bundles_parser.add_argument("--mirror-dir", type=Path, default=repo_root / "mirror")
    build_bundles_parser.add_argument("--bundle-dir", type=Path, default=repo_root / "bundles")
    build_bundles_parser.add_argument("--aliases", type=Path, default=repo_root / "data" / "aliases.json")
    build_bundles_parser.add_argument("--bundle-base-url", default="")
    build_bundles_parser.add_argument("--min-years", type=int, default=2)
    build_bundles_parser.set_defaults(handler=command_build_bundles)

    lootlabs_parser = subparsers.add_parser(
        "sync-lootlabs",
        help="Create or refresh LootLabs content-locker links for generated bundle downloads.",
    )
    lootlabs_parser.add_argument("--data-dir", type=Path, default=repo_root / "data")
    lootlabs_parser.add_argument("--manifest", type=Path, default=repo_root / "data" / "lootlabs-links.json")
    lootlabs_parser.set_defaults(handler=command_sync_lootlabs)

    build_site_parser = subparsers.add_parser("build-site", help="Build static HTML from data/papers/*.json.")
    build_site_parser.add_argument("--data-dir", type=Path, default=repo_root / "data")
    build_site_parser.add_argument("--site-dir", type=Path, default=repo_root / "site")
    build_site_parser.set_defaults(handler=command_build_site)

    publish_site_parser = subparsers.add_parser("publish-site", help="Aggregate provider outputs and publish one site.")
    publish_site_parser.add_argument("--repo-root", type=Path, default=repo_root)
    publish_site_parser.add_argument("--site-id", default="default")
    publish_site_parser.add_argument("--repository", default="example/repo")
    publish_site_parser.set_defaults(handler=command_publish_site)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)
