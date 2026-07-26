from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import sys
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.bundler import public_bundle_ids
from app.publisher import load_site_catalog
from app.site_registry import get_site_config

SITE_DIR = ROOT / "data" / "sites" / "default"
GENERIC_SUBJECT_PREFIXES = ("wdasec-skill-", "ceec-gsat-", "ceec-ast-", "tcte-tve-")


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def validate_provider_site_coverage(site_bundle_ids: set[str]) -> None:
    site_config = get_site_config("default")
    normalized, failures = load_site_catalog(ROOT, site_id=site_config.site_id)
    if failures:
        details = ", ".join(
            f"{failure.provider_id}:{failure.stage}:{failure.source_exam_id}"
            for failure in failures[:5]
        )
        suffix = " ..." if len(failures) > 5 else ""
        fail(f"provider state contains {len(failures)} unresolved sync failures ({details}{suffix})")

    expected_ids = public_bundle_ids(
        normalized,
        min_years=site_config.public_min_years,
        min_years_by_canonical_prefix=site_config.public_min_years_by_canonical_prefix,
    )
    missing = sorted(expected_ids - site_bundle_ids)
    extra = sorted(site_bundle_ids - expected_ids)
    if missing or extra:
        samples = []
        if missing:
            samples.append(f"missing={len(missing)} ({', '.join(missing[:5])})")
        if extra:
            samples.append(f"extra={len(extra)} ({', '.join(extra[:5])})")
        fail("normalized catalog and public site eligibility differ: " + "; ".join(samples))


def validate_publication() -> tuple[int, int, int]:
    site = load_json(SITE_DIR / "bundles.json")
    feed = load_json(SITE_DIR / "frontend-bundles.json")
    release = load_json(SITE_DIR / "release-assets.json")

    for label, payload in (("site", site), ("frontend", feed), ("release", release)):
        if payload.get("schema_version") != 2:
            fail(f"{label} payload is not schema_version 2")
        if payload.get("catalog_version") != "exam-identity-v2":
            fail(f"{label} payload is missing catalog_version exam-identity-v2")
        if payload.get("site_id") != "default":
            fail(f"{label} payload is not for the default site")

    site_rows = site.get("bundles")
    feed_rows = feed.get("bundles")
    release_rows = release.get("assets")
    if not all(isinstance(rows, list) for rows in (site_rows, feed_rows, release_rows)):
        fail("publication payload arrays are missing")

    site_asset_names = []
    site_bundle_ids = set()
    for index, row in enumerate(site_rows):
        prefix = f"site bundle {index}"
        required = ("bundle_id", "canonical_name", "years", "file_count", "asset_name", "release_tag", "download_url", "checksum", "classification_confidence")
        for key in required:
            if key not in row:
                fail(f"{prefix} missing {key}")
        bundle_id = row["bundle_id"]
        if not isinstance(bundle_id, str) or not bundle_id:
            fail(f"{prefix} has an invalid bundle_id")
        site_bundle_ids.add(bundle_id)
        if not isinstance(row["years"], list) or not row["years"]:
            fail(f"{prefix} has no years")
        if not isinstance(row["file_count"], int) or row["file_count"] < 1:
            fail(f"{prefix} has an invalid file_count")
        if row["classification_confidence"] not in {"high", "medium"}:
            fail(f"{prefix} is not launch-safe: confidence={row['classification_confidence']}")
        for field in ("search_aliases", "subject_labels"):
            values = row.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) or "\n" in value or len(value) > 120 for value in values):
                fail(f"{prefix} has invalid {field}")
            if len(values) != len(set(values)):
                fail(f"{prefix} has duplicate {field}")
        if bundle_id.startswith(GENERIC_SUBJECT_PREFIXES) and not row.get("subject_labels"):
            fail(f"{prefix} has no subject label for a generic bundle")
        asset_name = row["asset_name"]
        if not isinstance(asset_name, str) or not asset_name.endswith(".zip"):
            fail(f"{prefix} has an invalid asset_name")
        site_asset_names.append(asset_name)
        if not isinstance(row["download_url"], str) or not row["download_url"].startswith("https://github.com/"):
            fail(f"{prefix} has an invalid download_url")
        if unquote(urlparse(row["download_url"]).path).rsplit("/", 1)[-1] != asset_name:
            fail(f"{prefix} download URL does not target its asset")

    if len(site_asset_names) != len(set(site_asset_names)):
        fail("site publication contains duplicate asset names")

    release_asset_names = []
    release_counts = Counter()
    for index, row in enumerate(release_rows):
        if not isinstance(row.get("asset_name"), str) or not row["asset_name"].endswith(".zip"):
            fail(f"release asset {index} has an invalid asset_name")
        release_asset_names.append(row["asset_name"])
        release_counts[row.get("release_tag", "")] += 1
    if set(release_asset_names) != set(site_asset_names):
        fail("release inventory and site publication asset sets differ")
    if len(release_asset_names) != len(set(release_asset_names)):
        fail("release inventory contains duplicate asset names")
    if any(not tag or count > 900 for tag, count in release_counts.items()):
        fail(f"release shard safety target exceeded: {dict(release_counts)}")

    validate_provider_site_coverage(site_bundle_ids)

    feed_ids = []
    for index, row in enumerate(feed_rows):
        prefix = f"frontend bundle {index}"
        for key in ("id", "name", "years", "fileCount", "url"):
            if key not in row:
                fail(f"{prefix} missing {key}")
        bundle_id = row["id"]
        feed_ids.append(bundle_id)
        if bundle_id not in site_bundle_ids:
            fail(f"{prefix} is not present in site publication")
        if not isinstance(row["searchAliases"], list) or not row["searchAliases"]:
            fail(f"{prefix} has no search aliases")
        if bundle_id.startswith(GENERIC_SUBJECT_PREFIXES) and not row.get("subjectLabels"):
            fail(f"{prefix} has no subject labels for a generic bundle")
    if len(feed_ids) != len(set(feed_ids)):
        fail("frontend feed contains duplicate logical bundle IDs")
    if set(feed_ids) != site_bundle_ids:
        fail("frontend feed and site publication logical bundle sets differ")

    return len(site_rows), len(feed_rows), len(release_rows)


def validate_schema_json() -> int:
    paths = sorted((ROOT / "schemas").rglob("*.json"))
    paths += sorted((ROOT / "catalog").rglob("*.json"))
    for path in paths:
        load_json(path)
    return len(paths)


if __name__ == "__main__":
    try:
        site_count, feed_count, release_count = validate_publication()
        schema_count = validate_schema_json()
    except ValueError as exc:
        print(f"publication validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"validated {site_count} site bundles, {feed_count} frontend bundles, {release_count} release assets, and {schema_count} schema files")
