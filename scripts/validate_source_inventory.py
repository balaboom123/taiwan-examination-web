from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.source_inventory import validate_source_inventory


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the reviewed source scope against local provider state.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--require-discovery-manifests", action="store_true")
    args = parser.parse_args()
    try:
        report = validate_source_inventory(
            args.repo_root,
            require_discovery_manifests=args.require_discovery_manifests,
        )
    except ValueError as exc:
        print(f"source inventory validation failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"validated {report['provider_count']} providers and {report['candidate_count']} candidates; "
        f"discovery manifests present={report['discovery_manifests_present']} "
        f"missing={len(report['discovery_manifests_missing'])} "
        f"not_applicable={len(report['discovery_manifests_not_applicable'])} "
        f"incomplete={len(report['discovery_manifests_incomplete'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
