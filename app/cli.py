from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

from app.audit import audit_exit_code, build_catalog_audit, build_release_plan, write_catalog_audit, write_release_plan
from app.bundler import build_bundles
from app.crawler import year_ad_from_code
from app.manifest import load_source_manifest, source_manifest_from_data, write_source_manifest
from app.migration import migrate_legacy_state
from app.models import BundleAsset, NormalizedCatalog, SyncFailure
from app.normalizer import load_alias_rules, renormalize_catalog
from app.paths import ProviderPaths, provider_paths, site_paths
from app.publisher import publish_site, write_data_files, write_provider_state
from app.probe import probe_latest
from app.providers.base import SourceProvider
from app.providers.registry import get_provider
from app.state import load_existing_state, load_provider_state, load_site_bundles, merge_incremental_state, merge_targeted_state
from app.site_registry import get_site_config
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


def _provider_state_paths(data_dir: Path, mirror_dir: Path, provider_id: str) -> ProviderPaths:
    provider_data_dir = data_dir / "providers" / provider_id
    return ProviderPaths(
        provider_id=provider_id,
        data_dir=provider_data_dir,
        exams_dir=provider_data_dir / "exams",
        papers_dir=provider_data_dir / "papers",
        review_queue_path=provider_data_dir / "review-queue.json",
        sync_failures_path=provider_data_dir / "sync-failures.json",
        aliases_path=provider_data_dir / "aliases.json",
        source_manifest_path=provider_data_dir / "source-manifest.json",
        mirror_dir=mirror_dir / "providers" / provider_id,
    )


def _provider_manifest_from_probe(probe: dict[str, object]):
    updated_manifest = probe.get("updated_manifest")
    if isinstance(updated_manifest, dict):
        return source_manifest_from_data(updated_manifest)
    return None


def _resolve_probe_manifest_path(args: argparse.Namespace, provider_id: str) -> Path:
    if args.manifest is not None:
        return args.manifest
    return args.output.parent.parent / "data" / "providers" / provider_id / "source-manifest.json"


def _resolve_sync_manifest_path(args: argparse.Namespace, provider_id: str) -> Path:
    if args.manifest is not None:
        return args.manifest
    return _provider_state_paths(args.data_dir, args.mirror_dir, provider_id).source_manifest_path


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
    print(f"Built {len(bundles)} bundles, {len(rebuild_result.failures)} bundle failures", flush=True)
    if failures:
        print(f"{len(failures)} total failures (see data/sync-failures.json)", flush=True)
        return 1
    return 0


def run_probe_latest(args: argparse.Namespace, client: SourceProvider | None = None, now: str | None = None) -> int:
    probe_client = _provider_for_args(args, client)
    generated_at = now or datetime.now().astimezone().isoformat()
    provider_id = _provider_id_for_args(args, probe_client)
    if not _supports_probe_manifest(provider_id, probe_client):
        print(f"probe-latest is not supported for provider {provider_id}: missing probe URL model", flush=True)
        return 1
    manifest_path = _resolve_probe_manifest_path(args, provider_id)
    manifest = load_source_manifest(manifest_path, provider_id=provider_id)
    result = probe_latest(client=probe_client, manifest=manifest, year_window=args.years, now=generated_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result.to_output_data(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.write_manifest:
        write_source_manifest(manifest_path, result.updated_manifest)
    return 0


def _download_affected_bundles(
    bundle_dir: Path,
    existing_bundles: list[BundleAsset],
    affected_canonical_ids: set[str],
    release_tag: str,
) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for bundle in existing_bundles:
        if bundle.canonical_id not in affected_canonical_ids:
            continue
        resolved_release_tag = bundle.release_tag or release_tag
        if not resolved_release_tag:
            continue
        candidate_names = [
            asset_name
            for asset_name in dict.fromkeys([bundle.asset_name, *bundle.legacy_asset_names])
            if asset_name
        ]
        if not candidate_names:
            continue
        if any((bundle_dir / asset_name).exists() for asset_name in candidate_names):
            continue
        last_error: subprocess.CalledProcessError | None = None
        for asset_name in candidate_names:
            try:
                subprocess.run(
                    ["gh", "release", "download", resolved_release_tag, "--pattern", asset_name, "--dir", str(bundle_dir)],
                    check=True,
                )
            except subprocess.CalledProcessError as exc:
                last_error = exc
                continue
            break
        else:
            if last_error is not None:
                raise last_error


def _write_probe_manifest_if_present(probe: dict[str, object], manifest_path: Path) -> None:
    updated_manifest = probe.get("updated_manifest")
    if isinstance(updated_manifest, dict):
        write_source_manifest(manifest_path, source_manifest_from_data(updated_manifest))


def _repo_root_from_data_dir(data_dir: Path) -> Path:
    return data_dir.parent


def _resolve_sync_bundle_dir(args: argparse.Namespace) -> Path:
    bundle_dir = getattr(args, "bundle_dir", None)
    if bundle_dir is not None:
        return bundle_dir
    return site_paths(_repo_root_from_data_dir(args.data_dir), args.site_id).bundle_dir


def _write_publish_plan(
    path: Path,
    *,
    site_id: str,
    affected_canonical_ids: set[str],
    canonical_aliases: dict[str, list[str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "site_id": site_id,
        "affected_canonical_ids": sorted(affected_canonical_ids),
        "canonical_aliases": {canonical_id: sorted(alias_ids) for canonical_id, alias_ids in sorted(canonical_aliases.items())},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_publish_plan(path: Path | None, site_id: str) -> tuple[set[str] | None, dict[str, list[str]]]:
    if path is None:
        return None, {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload_site_id = str(payload.get("site_id") or site_id)
    if payload_site_id != site_id:
        raise ValueError(f"Publish plan site_id mismatch: expected {site_id}, got {payload_site_id}")
    affected = {str(canonical_id) for canonical_id in payload.get("affected_canonical_ids", []) if canonical_id}
    raw_aliases = payload.get("canonical_aliases", {})
    canonical_aliases = {
        str(canonical_id): [str(alias_id) for alias_id in alias_ids if alias_id]
        for canonical_id, alias_ids in raw_aliases.items()
        if alias_ids
    } if isinstance(raw_aliases, dict) else {}
    return affected, canonical_aliases


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
    provider_state = _provider_state_paths(args.data_dir, args.mirror_dir, provider_id)
    existing_provider_raw_pages, existing_provider_catalog, existing_provider_failures = load_provider_state(provider_state)
    refreshed_exam_ids = {page.source_exam_id for page in refreshed_raw_pages}
    provider_raw_pages, provider_normalized, _, affected_canonical_ids, canonical_aliases = merge_targeted_state(
        existing_raw_pages=existing_provider_raw_pages,
        existing_catalog=existing_provider_catalog,
        existing_bundles=[],
        refreshed_raw_pages=refreshed_raw_pages,
        refreshed_catalog=refreshed_catalog,
        removed_exam_ids=removed_exam_ids,
    )
    if getattr(args, "download_affected_bundles", False) and affected_canonical_ids:
        site = site_paths(_repo_root_from_data_dir(args.data_dir), args.site_id)
        _download_affected_bundles(
            _resolve_sync_bundle_dir(args),
            load_site_bundles(site),
            affected_canonical_ids,
            args.release_tag,
        )
    if args.publish_plan_output is not None:
        _write_publish_plan(
            args.publish_plan_output,
            site_id=args.site_id,
            affected_canonical_ids=affected_canonical_ids,
            canonical_aliases=canonical_aliases,
        )
    replaced_exam_ids = refreshed_exam_ids | removed_exam_ids
    provider_failures = [failure for failure in existing_provider_failures if failure.source_exam_id not in replaced_exam_ids]
    provider_failures.extend(sync_failures)
    write_provider_state(
        provider_state,
        raw_pages=provider_raw_pages,
        normalized=provider_normalized,
        aliases=aliases,
        failures=provider_failures,
        manifest=_provider_manifest_from_probe(probe),
    )
    _write_probe_manifest_if_present(probe, _resolve_sync_manifest_path(args, provider_id))
    return 0


def command_sync(args: argparse.Namespace, client: SourceProvider | None = None) -> int:
    provider = _provider_for_args(args, client)
    provider_id = _provider_id_for_args(args, provider)
    provider_state = _provider_state_paths(args.data_dir, args.mirror_dir, provider_id)
    if getattr(args, "write_manifest", False) and not _supports_probe_manifest(provider_id, provider):
        print(f"--write-manifest is not supported for provider {provider_id}: missing probe URL model", flush=True)
        return 1
    try:
        if getattr(args, "year_window", None):
            years = _latest_years(provider, args.year_window)
        else:
            years = _discover_years(provider, args.years)
    except Exception as exc:
        existing_provider_raw_pages, existing_provider_catalog, _existing_provider_failures = load_provider_state(provider_state)
        if existing_provider_raw_pages or existing_provider_catalog.papers:
            print(f"Provider {provider_id} discovery unavailable ({exc}); preserving existing provider state.", flush=True)
            return 0
        print(f"Provider {provider_id} discovery failed and no existing provider state is available: {exc}", flush=True)
        return 1
    aliases = load_alias_rules(args.aliases)
    mirror_store = MirrorStore(args.mirror_dir)

    all_raw_pages: list = []
    all_papers: list = []
    all_review_queue: list = []
    all_sync_failures: list = []

    for year in years:
        try:
            exam_codes = [(exam.code, exam.year_ad) for exam in provider.discover_exams(year)]
        except Exception as exc:
            print(f"Year {year}: failed to discover exams: {exc}")
            all_sync_failures.append(
                SyncFailure(
                    stage="discover",
                    source_exam_id=f"{provider_id}-{year}",
                    year_roc=year - 1911,
                    paper_code="",
                    file_type="",
                    url="",
                    message=f"Failed to discover exams: {exc}",
                )
            )
            continue
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
        existing_provider_raw_pages, existing_provider_catalog, existing_provider_failures = load_provider_state(provider_state)
        failed_exam_ids = {failure.source_exam_id for failure in sync_failures}
        safe_raw_pages = [page for page in refreshed_raw_pages if page.source_exam_id not in failed_exam_ids]
        safe_catalog = NormalizedCatalog(
            papers=[p for p in refreshed_catalog.papers if p.source_exam_id not in failed_exam_ids],
            review_queue=[r for r in refreshed_catalog.review_queue if r.source_exam_id not in failed_exam_ids],
        )
        provider_raw_pages, provider_normalized, _, affected_canonical_ids, canonical_aliases = merge_incremental_state(
            existing_raw_pages=existing_provider_raw_pages,
            existing_catalog=existing_provider_catalog,
            existing_bundles=[],
            refreshed_raw_pages=safe_raw_pages,
            refreshed_catalog=safe_catalog,
        )
        if getattr(args, "download_affected_bundles", False) and affected_canonical_ids:
            site = site_paths(_repo_root_from_data_dir(args.data_dir), args.site_id)
            _download_affected_bundles(
                _resolve_sync_bundle_dir(args),
                load_site_bundles(site),
                affected_canonical_ids,
                args.release_tag,
            )
        refreshed_exam_ids = {page.source_exam_id for page in refreshed_raw_pages}
        provider_failures = [failure for failure in existing_provider_failures if failure.source_exam_id not in refreshed_exam_ids]
        provider_failures.extend(sync_failures)
        failures = provider_failures
    else:
        provider_raw_pages = refreshed_raw_pages
        provider_normalized = refreshed_catalog
        provider_failures = sync_failures
        affected_canonical_ids = {paper.canonical_id for paper in provider_normalized.papers}
        canonical_aliases = {}
        failures = sync_failures
    if args.publish_plan_output is not None:
        _write_publish_plan(
            args.publish_plan_output,
            site_id=args.site_id,
            affected_canonical_ids=affected_canonical_ids,
            canonical_aliases=canonical_aliases,
        )
    provider_manifest = None
    if getattr(args, "write_manifest", False) and not failures:
        manifest_path = _resolve_sync_manifest_path(args, provider_id)
        manifest = load_source_manifest(manifest_path, provider_id=provider_id)
        result = probe_latest(client=provider, manifest=manifest, year_window=len(years), now=datetime.now().astimezone().isoformat())
        provider_manifest = result.updated_manifest
        write_source_manifest(manifest_path, provider_manifest)
    write_provider_state(
        provider_state,
        raw_pages=provider_raw_pages,
        normalized=provider_normalized,
        aliases=aliases,
        failures=provider_failures,
        manifest=provider_manifest,
    )
    if failures:
        print(f"Completed with {len(failures)} failure(s). See data/sync-failures.json for details.")
        return 1
    return 0



def command_plan_release(args: argparse.Namespace) -> int:
    try:
        plan = build_release_plan(args.repo_root, site_id=args.site_id, release_tag_prefix=args.release_tag_prefix)
        write_release_plan(plan, args.output)
    except ValueError as exc:
        print(str(exc), flush=True)
        return 1
    print(
        f"Planned {len(plan['bundles'])} bundles across {len(plan['shards'])} release shards; "
        f"report: {args.output}",
        flush=True,
    )
    return 0

def command_audit_catalog(args: argparse.Namespace) -> int:
    report = build_catalog_audit(args.repo_root, site_id=args.site_id)
    write_catalog_audit(report, args.output)
    print(
        f"Scanned {report['paper_records_scanned']} records across {report['provider_count']} providers; "
        f"{len(report['mixed_legacy_groups'])} legacy groups require split and "
        f"{report['records_needing_review']} records require review. Report: {args.output}",
        flush=True,
    )
    return audit_exit_code(report, strict=args.strict)


def command_migrate_catalog(args: argparse.Namespace) -> int:
    site_config = get_site_config(args.site_id)
    provider_ids = (args.provider,) if args.provider else site_config.provider_ids
    migrated = 0
    records = 0
    for provider_id in provider_ids:
        provider = provider_paths(args.repo_root, provider_id)
        if not provider.data_dir.exists():
            continue
        raw_pages, catalog, failures = load_provider_state(provider)
        aliases = load_alias_rules(provider.aliases_path)
        migrated_catalog = renormalize_catalog(catalog, aliases)
        manifest = None
        if provider.source_manifest_path.exists():
            manifest = load_source_manifest(provider.source_manifest_path, provider_id=provider_id)
        write_provider_state(
            provider,
            raw_pages=raw_pages,
            normalized=migrated_catalog,
            aliases=aliases,
            failures=failures,
            manifest=manifest,
        )
        migrated += 1
        records += len(migrated_catalog.papers)
    print(f"Migrated {records} paper records across {migrated} providers to exam-identity-v2", flush=True)
    return 0


def command_publish_site(args: argparse.Namespace) -> int:
    try:
        affected_canonical_ids, canonical_aliases = _load_publish_plan(args.publish_plan, args.site_id)
        publish_site(
            args.repo_root,
            site_id=args.site_id,
            repository=args.repository,
            affected_canonical_ids=affected_canonical_ids,
            canonical_aliases=canonical_aliases,
        )
    except ValueError as exc:
        print(str(exc), flush=True)
        return 1
    return 0


def command_migrate_legacy_state(args: argparse.Namespace) -> int:
    report = migrate_legacy_state(
        args.repo_root,
        provider_id=args.provider,
        site_id=args.site_id,
        mode=args.mode,
    )
    print(report.output, flush=True)
    return report.exit_code


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
    probe_parser.add_argument("--manifest", type=Path, default=None)
    probe_parser.add_argument("--output", type=Path, default=repo_root / ".tmp" / "source-probe.json")
    probe_parser.add_argument("--write-manifest", action="store_true")
    probe_parser.set_defaults(handler=run_probe_latest)

    targeted = subparsers.add_parser("sync-targeted", help="Sync only changed exams from a probe output file.")
    targeted.add_argument("--probe", type=Path, default=repo_root / ".tmp" / "source-probe.json")
    targeted.add_argument("--data-dir", type=Path, default=repo_root / "data")
    targeted.add_argument("--mirror-dir", type=Path, default=repo_root / "mirror")
    targeted.add_argument("--bundle-dir", type=Path, default=None)
    targeted.add_argument("--aliases", type=Path, default=repo_root / "data" / "aliases.json")
    targeted.add_argument("--manifest", type=Path, default=None)
    targeted.add_argument("--bundle-base-url", default="")
    targeted.add_argument("--mirror-base-url", default="")
    targeted.add_argument("--download-attachments", action="store_true", default=False)
    targeted.add_argument("--download-affected-bundles", action="store_true", default=False)
    targeted.add_argument("--publish-plan-output", type=Path, default=None)
    targeted.add_argument("--provider", default=None)
    targeted.add_argument("--site-id", default="default")
    targeted.add_argument("--release-tag", default="moex-bundles")
    targeted.set_defaults(handler=run_sync_targeted)

    for name in ("sync-full", "sync-incremental"):
        sync = subparsers.add_parser(name, help=f"{name} against the selected provider.")
        sync.add_argument("--data-dir", type=Path, default=repo_root / "data")
        sync.add_argument("--mirror-dir", type=Path, default=repo_root / "mirror")
        sync.add_argument("--bundle-dir", type=Path, default=None)
        sync.add_argument("--aliases", type=Path, default=repo_root / "data" / "aliases.json")
        sync.add_argument("--manifest", type=Path, default=None)
        sync.add_argument("--bundle-base-url", default="")
        sync.add_argument("--mirror-base-url", default="")
        sync.add_argument("--download-attachments", action="store_true", default=False)
        sync.add_argument("--download-affected-bundles", action="store_true", default=False)
        sync.add_argument("--publish-plan-output", type=Path, default=None)
        sync.add_argument("--provider", default="moex")
        sync.add_argument("--site-id", default="default")
        sync.add_argument("--release-tag", default="moex-bundles")
        sync.add_argument("--write-manifest", action="store_true", default=False)
        if name == "sync-full":
            sync.add_argument("--years", nargs="*", type=int, default=None)
        else:
            sync.add_argument("--years", dest="year_window", type=int, default=3)
        sync.set_defaults(handler=command_sync)

    build_bundles_parser = subparsers.add_parser("build-bundles", help="Rebuild ZIP bundles from existing local data (no network).")
    build_bundles_parser.add_argument("--data-dir", type=Path, default=repo_root / "data")
    build_bundles_parser.add_argument("--mirror-dir", type=Path, default=repo_root / "mirror")
    build_bundles_parser.add_argument("--bundle-dir", type=Path, default=repo_root / "bundles")
    build_bundles_parser.add_argument("--aliases", type=Path, default=repo_root / "data" / "aliases.json")
    build_bundles_parser.add_argument("--bundle-base-url", default="")
    build_bundles_parser.add_argument("--min-years", type=int, default=2)
    build_bundles_parser.set_defaults(handler=command_build_bundles)

    plan_release_parser = subparsers.add_parser(
        "plan-release",
        help="Plan physical release shards from current site inventory without uploading or deleting assets.",
    )
    plan_release_parser.add_argument("--repo-root", type=Path, default=repo_root)
    plan_release_parser.add_argument("--site-id", default="default")
    plan_release_parser.add_argument("--output", type=Path, default=repo_root / ".tmp" / "release-plan.json")
    plan_release_parser.add_argument("--release-tag-prefix", default=None)
    plan_release_parser.set_defaults(handler=command_plan_release)

    audit_parser = subparsers.add_parser(
        "audit-catalog",
        help="Audit every provider record and current bundle for identity coverage and mixed groups.",
    )
    audit_parser.add_argument("--repo-root", type=Path, default=repo_root)
    audit_parser.add_argument("--site-id", default="default")
    audit_parser.add_argument("--output", type=Path, default=repo_root / ".tmp" / "catalog-audit.json")
    audit_parser.add_argument("--strict", action="store_true")
    audit_parser.set_defaults(handler=command_audit_catalog)

    migrate_catalog_parser = subparsers.add_parser(
        "migrate-catalog",
        help="Reclassify all retained provider state into exam-identity-v2 without network access.",
    )
    migrate_catalog_parser.add_argument("--repo-root", type=Path, default=repo_root)
    migrate_catalog_parser.add_argument("--site-id", default="default")
    migrate_catalog_parser.add_argument("--provider", default=None)
    migrate_catalog_parser.set_defaults(handler=command_migrate_catalog)

    publish_site_parser = subparsers.add_parser("publish-site", help="Aggregate provider outputs and publish one site.")
    publish_site_parser.add_argument("--repo-root", type=Path, default=repo_root)
    publish_site_parser.add_argument("--site-id", default="default")
    publish_site_parser.add_argument("--repository", default="example/repo")
    publish_site_parser.add_argument("--publish-plan", type=Path, default=None)
    publish_site_parser.set_defaults(handler=command_publish_site)

    migrate_parser = subparsers.add_parser(
        "migrate-legacy-state",
        help="Promote legacy root-level provider/site state into scoped paths without network access.",
    )
    migrate_parser.add_argument("--repo-root", type=Path, default=repo_root)
    migrate_parser.add_argument("--provider", default="moex")
    migrate_parser.add_argument("--site-id", default="default")
    migrate_parser.add_argument("--mode", choices=("dry-run", "move", "verify"), default="dry-run")
    migrate_parser.set_defaults(handler=command_migrate_legacy_state)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)
