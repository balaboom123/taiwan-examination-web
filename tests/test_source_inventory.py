from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from app.source_inventory import load_source_inventory, validate_source_inventory


ROOT = Path(__file__).resolve().parents[1]


class SourceInventoryTests(unittest.TestCase):
    def test_current_inventory_covers_default_registry_and_matches_local_state(self) -> None:
        report = validate_source_inventory(ROOT)

        self.assertEqual(report["provider_count"], 35)
        self.assertEqual(report["candidate_count"], 10)
        self.assertEqual(report["discovery_manifests_present"], 4)
        self.assertEqual(len(report["discovery_manifests_missing"]), 31)
        self.assertEqual(report["discovery_manifests_incomplete"], [])
        self.assertEqual(report["manifest_unrepresented_events"], [])
        self.assertEqual(report["local_state_drift"], [])

    def test_strict_manifest_requirement_remains_red_until_snapshots_are_complete(self) -> None:
        with self.assertRaisesRegex(ValueError, "complete source discovery remains unresolved"):
            validate_source_inventory(ROOT, require_discovery_manifests=True)

    def test_inventory_loader_rejects_unsupported_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            catalog = root / "catalog"
            catalog.mkdir()
            (catalog / "source-inventory.json").write_text(
                """{
                  "schema_version": 1,
                  "inventory_version": "test",
                  "captured_at": "2026-07-29",
                  "site_id": "default",
                  "providers": [{
                    "provider_id": "moex",
                    "official_source_urls": ["https://example.test"],
                    "exam_category": "test",
                    "status": "unknown",
                    "status_reason": "test",
                    "available_years": {"mode": "unknown", "note": "test", "start_ad": null, "end_ad": null},
                    "local_years": [],
                    "local_state": {"raw_event_pages": 0, "normalized_paper_records": 0, "sync_failures": 0},
                    "discovery_snapshot": {"manifest_path": "data/providers/moex/source-manifest.json", "status": "missing", "coverage": "unknown"},
                    "restrictions": [],
                    "evidence": ["test"]
                  }],
                  "candidates": []
                }""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unsupported status"):
                load_source_inventory(root)


if __name__ == "__main__":
    unittest.main()
