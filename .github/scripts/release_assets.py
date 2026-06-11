"""Manage assets on the MOEX bundle GitHub release.

Shared by the sync-full, sync-incremental, and audit-recent workflows so the
release logic lives in one place. Requires the gh CLI with GH_TOKEN set.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

RELEASE_TAG = os.environ.get("MOEX_RELEASE_TAG", "moex-bundles")
RELEASE_ASSETS_PATH = Path("data/release-assets.json")


def _local_assets() -> list[dict]:
    return json.loads(RELEASE_ASSETS_PATH.read_text(encoding="utf-8"))


def _asset_zip_names(asset: dict) -> list[str]:
    # Legacy alias names stay published on the release so old download URLs keep working.
    names = [asset["asset_name"], *asset.get("legacy_asset_names", [])]
    return [name for name in dict.fromkeys(names) if name and name.endswith(".zip")]


def _desired_zip_names() -> set[str]:
    return {name for asset in _local_assets() for name in _asset_zip_names(asset)}


def _release_zip_names() -> list[str]:
    payload = json.loads(
        subprocess.check_output(["gh", "release", "view", RELEASE_TAG, "--json", "assets"], text=True)
    )
    return sorted(asset["name"] for asset in payload.get("assets", []) if asset["name"].endswith(".zip"))


def ensure() -> int:
    view = subprocess.run(
        ["gh", "release", "view", RELEASE_TAG],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if view.returncode != 0:
        subprocess.run(
            [
                "gh", "release", "create", RELEASE_TAG,
                "--title", "MOEX downloadable bundles",
                "--notes", "Human-friendly exam bundles with compatibility aliases",
            ],
            check=True,
        )
    return 0


def coverage() -> int:
    expected_zip_names = sorted(_desired_zip_names())
    current_release_zip_names = _release_zip_names()
    bootstrap_required = current_release_zip_names != expected_zip_names
    print(
        f"expected zips: {len(expected_zip_names)}, release zips: {len(current_release_zip_names)}, "
        f"bootstrap_required: {bootstrap_required}"
    )
    if bootstrap_required:
        expected = set(expected_zip_names)
        current = set(current_release_zip_names)
        for name in sorted(expected - current):
            print(f"missing from release: {name}")
        for name in sorted(current - expected):
            print(f"unexpected in release: {name}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"bootstrap_required={str(bootstrap_required).lower()}\n")
    return 0


def upload() -> int:
    missing = []
    for asset in _local_assets():
        local_path = Path(asset["storage_key"])
        if not local_path.exists():
            missing.append(str(local_path))
            continue
        for name in _asset_zip_names(asset):
            spec = f"{local_path}#{name}"
            subprocess.run(["gh", "release", "upload", RELEASE_TAG, spec, "--clobber"], check=True)
    if missing:
        print("Missing expected bundle files before upload:\n" + "\n".join(missing), file=sys.stderr)
        return 1
    return 0


def prune() -> int:
    desired = _desired_zip_names()
    for name in _release_zip_names():
        if name not in desired:
            subprocess.run(["gh", "release", "delete-asset", RELEASE_TAG, name, "--yes"], check=True)
    return 0


COMMANDS = {"ensure": ensure, "coverage": coverage, "upload": upload, "prune": prune}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print(f"usage: release_assets.py {{{'|'.join(COMMANDS)}}}", file=sys.stderr)
        return 2
    return COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    raise SystemExit(main())
