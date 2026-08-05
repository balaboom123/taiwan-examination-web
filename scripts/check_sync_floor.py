from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.source_inventory import check_sync_floor, provider_ids_from_paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refuse sync output that retains fewer records than the reviewed source inventory.",
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "paths",
        nargs="+",
        help="Paths staged for commit; provider IDs are read from data/providers/<id>.",
    )
    args = parser.parse_args()

    provider_ids = provider_ids_from_paths(args.paths)
    if not provider_ids:
        print("no provider data staged; sync floor check does not apply")
        return 0

    try:
        report = check_sync_floor(args.repo_root, provider_ids)
    except ValueError as exc:
        print(f"sync floor check failed: {exc}", file=sys.stderr)
        print(
            "Nothing was committed. Re-run the sync if the source was briefly incomplete. "
            "If the removal is genuine, ratify it by lowering the provider's local_state in "
            "catalog/source-inventory.json through a reviewed change.",
            file=sys.stderr,
        )
        return 1

    for provider in report["providers"]:
        print(
            f"{provider['provider_id']}: {provider['raw_event_pages']} event page(s), "
            f"{provider['normalized_paper_records']} paper record(s) at or above the reviewed floor"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
