"""Manage downloadable bundle assets on GitHub releases.

Shared by the publication workflows so the release logic lives in one place.
Requires the gh CLI with GH_TOKEN set.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

RELEASE_TAG = os.environ.get("RELEASE_TAG") or os.environ.get("MOEX_RELEASE_TAG") or ""
SITE_ID = os.environ.get("SITE_ID", "default")
RELEASE_ASSETS_PATH = Path("data") / "sites" / SITE_ID / "release-assets.json"
UPLOAD_BATCH_SIZE = 50


def _local_assets() -> list[dict]:
    payload = json.loads(RELEASE_ASSETS_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload.get("assets", payload)
    return payload


def _asset_release_tag(asset: dict) -> str:
    release_tag = str(asset.get("release_tag") or RELEASE_TAG).strip()
    if not release_tag:
        raise ValueError("release asset entry is missing release_tag and no fallback release tag is configured")
    return release_tag


def _group_assets_by_release_tag(assets: list[dict] | None = None) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for asset in assets or _local_assets():
        grouped[_asset_release_tag(asset)].append(asset)
    return dict(grouped)


def _asset_zip_names(asset: dict, *, include_legacy: bool = True) -> list[str]:
    names = [asset["asset_name"]]
    if include_legacy:
        # Legacy alias names stay published on the release when already present so old download URLs keep working.
        names.extend(asset.get("legacy_asset_names", []))
    return [name for name in dict.fromkeys(names) if name and name.endswith(".zip")]


def _desired_zip_names(release_tag: str | None = None) -> set[str]:
    if release_tag is None:
        return {name for asset in _local_assets() for name in _asset_zip_names(asset, include_legacy=False)}
    return {
        name
        for asset in _group_assets_by_release_tag().get(release_tag, [])
        for name in _asset_zip_names(asset, include_legacy=False)
    }


def _release_zip_names(release_tag: str, *, allow_missing: bool = False) -> list[str]:
    try:
        raw_payload = subprocess.check_output(
            ["gh", "release", "view", release_tag, "--json", "assets"],
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError:
        if allow_missing:
            return []
        raise
    payload = json.loads(raw_payload)
    return sorted(asset["name"] for asset in payload.get("assets", []) if asset["name"].endswith(".zip"))


def ensure() -> int:
    for release_tag in sorted(_group_assets_by_release_tag()):
        view = subprocess.run(
            ["gh", "release", "view", release_tag],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if view.returncode != 0:
            subprocess.run(
                [
                    "gh", "release", "create", release_tag,
                    "--title", f"Downloadable exam bundles ({release_tag})",
                    "--notes", "Human-friendly exam bundles with compatibility aliases",
                ],
                check=True,
            )
    return 0


def coverage() -> int:
    bootstrap_required = False
    total_expected = 0
    total_release = 0
    for release_tag in sorted(_group_assets_by_release_tag()):
        expected = _desired_zip_names(release_tag)
        current = set(_release_zip_names(release_tag, allow_missing=True))
        published = {
            name
            for asset in _group_assets_by_release_tag().get(release_tag, [])
            for name in _asset_zip_names(asset, include_legacy=True)
        }
        total_expected += len(expected)
        total_release += len(current)
        missing = expected - current
        unexpected = current - published
        release_bootstrap_required = bool(missing or unexpected)
        bootstrap_required = bootstrap_required or release_bootstrap_required
        print(
            f"release_tag: {release_tag}, expected zips: {len(expected)}, release zips: {len(current)}, "
            f"bootstrap_required: {release_bootstrap_required}"
        )
        if release_bootstrap_required:
            for name in sorted(missing):
                print(f"missing from release {release_tag}: {name}")
            for name in sorted(unexpected):
                print(f"unexpected in release {release_tag}: {name}")
    print(f"total expected zips: {total_expected}, total release zips: {total_release}, bootstrap_required: {bootstrap_required}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"bootstrap_required={str(bootstrap_required).lower()}\n")
    return 0


def upload() -> int:
    missing = []
    for release_tag, assets in sorted(_group_assets_by_release_tag().items()):
        remote_names = set(_release_zip_names(release_tag, allow_missing=True))
        upload_specs: list[str] = []
        for asset in assets:
            local_path = Path(asset["storage_key"])
            zip_names = _asset_zip_names(asset, include_legacy=False)
            if not local_path.exists():
                if any(name not in remote_names for name in zip_names):
                    missing.append(str(local_path))
                continue
            for name in zip_names:
                if name in remote_names:
                    continue
                spec = f"{local_path}#{name}"
                upload_specs.append(spec)
                remote_names.add(name)
        for start in range(0, len(upload_specs), UPLOAD_BATCH_SIZE):
            batch = upload_specs[start:start + UPLOAD_BATCH_SIZE]
            subprocess.run(["gh", "release", "upload", release_tag, *batch, "--clobber"], check=True)
    if missing:
        print("Missing expected bundle files before upload:\n" + "\n".join(missing), file=sys.stderr)
        return 1
    return 0


def prune() -> int:
    for release_tag in sorted(_group_assets_by_release_tag()):
        desired = {
            name
            for asset in _group_assets_by_release_tag().get(release_tag, [])
            for name in _asset_zip_names(asset, include_legacy=True)
        }
        for name in _release_zip_names(release_tag, allow_missing=True):
            if name not in desired:
                subprocess.run(["gh", "release", "delete-asset", release_tag, name, "--yes"], check=True)
    return 0


COMMANDS = {"ensure": ensure, "coverage": coverage, "upload": upload, "prune": prune}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print(f"usage: release_assets.py {{{'|'.join(COMMANDS)}}}", file=sys.stderr)
        return 2
    return COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    raise SystemExit(main())
