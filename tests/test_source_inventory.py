from __future__ import annotations

import json
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
        self.assertEqual(report["discovery_manifests_present"], 23)
        self.assertEqual(len(report["discovery_manifests_missing"]), 11)
        self.assertEqual(report["discovery_manifests_blocked"], ["teacher_recruit_kaohsiung"])
        self.assertEqual(
            report["discovery_manifests_incomplete"],
            ["cpc_recruit", "moea_recruit", "taipower_recruit", "taisugar_recruit"],
        )
        self.assertEqual(
            report["manifest_event_gaps"],
            [
                {
                    "provider_id": "cpc_recruit",
                    "enforced": False,
                    "missing_events": [
                        ["cpc-recruit-104", 2015],
                        ["cpc-recruit-105", 2016],
                        ["cpc-recruit-106", 2017],
                        ["cpc-recruit-107", 2018],
                        ["cpc-recruit-109", 2020],
                        ["cpc-recruit-110", 2021],
                        ["cpc-recruit-111", 2022],
                        ["cpc-recruit-113", 2024],
                        ["cpc-recruit-114", 2025],
                    ],
                },
                {
                    "provider_id": "moea_recruit",
                    "enforced": False,
                    "missing_events": [
                        ["moea-recruit-115", 2026],
                        ["moea-recruit-90", 2001],
                        ["moea-recruit-92", 2003],
                        ["moea-recruit-94", 2005],
                        ["moea-recruit-99", 2010],
                    ],
                },
            ],
        )
        self.assertEqual(
            report["manifest_unrepresented_events"],
            [
                {
                    "provider_id": "moea_recruit",
                    "events": [
                        ["moea-recruit-100", 2011],
                        ["moea-recruit-107", 2018],
                        ["moea-recruit-91", 2002],
                        ["moea-recruit-93", 2004],
                        ["moea-recruit-98", 2009],
                    ],
                },
                {
                    "provider_id": "taipower_recruit",
                    "events": [
                        ["taipower-recruit-107-12", 2018],
                        ["taipower-recruit-107-5", 2018],
                    ],
                },
                {
                    "provider_id": "taisugar_recruit",
                    "events": [
                        ["taisugar-recruit-106", 2017],
                        ["taisugar-recruit-107", 2018],
                        ["taisugar-recruit-108", 2019],
                        ["taisugar-recruit-109", 2020],
                        ["taisugar-recruit-110", 2021],
                        ["taisugar-recruit-111", 2022],
                        ["taisugar-recruit-112", 2023],
                    ],
                },
            ],
        )
        self.assertEqual(report["local_state_drift"], [])

    def test_cpc_manifest_records_verified_scope_and_contamination(self) -> None:
        manifest = json.loads(
            (ROOT / "data/providers/cpc_recruit/source-manifest.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(sorted(map(int, manifest["years"])), [2009, 2011, 2012, 2013, 2019])
        self.assertEqual(len(manifest["exams"]), 5)
        self.assertEqual(len(manifest["files"]), 5)
        self.assertEqual(
            sum(item["bytes"] for item in manifest["files"].values()),
            14_071_292,
        )
        policy = manifest["probe_policy"]
        self.assertEqual(policy["accepted_asset_count"], 5)
        self.assertEqual(policy["excluded_brochure_archive"]["asset_count"], 15)
        self.assertEqual(
            policy["retained_local_contamination"]["normalized_brochure_records"],
            12,
        )
        self.assertEqual(
            policy["contracted_source_blockers"][0]["status"],
            "login_required",
        )

    def test_moea_manifest_records_exact_listing_and_contamination(self) -> None:
        manifest = json.loads(
            (ROOT / "data/providers/moea_recruit/source-manifest.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            sorted(map(int, manifest["years"])),
            [
                2002, 2004, 2006, 2007, 2008, 2009, 2011,
                2012, 2013, 2014, 2015, 2016, 2017, 2018,
                2019, 2020, 2021, 2022, 2023, 2024, 2025,
            ],
        )
        self.assertEqual(len(manifest["exams"]), 21)
        self.assertEqual(manifest["files"], {})
        policy = manifest["probe_policy"]
        self.assertEqual(policy["subject_group_count"], 515)
        self.assertEqual(policy["listed_asset_count"], 1_486)
        self.assertEqual(
            sum(item["subject_group_count"] for item in manifest["years"].values()),
            515,
        )
        self.assertEqual(
            sum(item["asset_count"] for item in manifest["years"].values()),
            1_486,
        )
        contamination = policy["retained_local_contamination"]
        self.assertEqual(contamination["normalized_records"], 370)
        self.assertTrue(contamination["all_records_are_taipower_hiring_material"])
        self.assertTrue(contamination["exact_taipower_source_url_set_duplicate"])
        self.assertTrue(contamination["exact_taipower_checksum_set_duplicate"])
        self.assertEqual(
            contamination["source_only_events"],
            [
                ["moea-recruit-100", 2011],
                ["moea-recruit-107", 2018],
                ["moea-recruit-91", 2002],
                ["moea-recruit-93", 2004],
                ["moea-recruit-98", 2009],
            ],
        )
        self.assertEqual(
            contamination["local_only_events"],
            [
                ["moea-recruit-115", 2026],
                ["moea-recruit-90", 2001],
                ["moea-recruit-92", 2003],
                ["moea-recruit-94", 2005],
                ["moea-recruit-99", 2010],
            ],
        )

    def test_taipower_manifest_records_event_scope_and_truncation(self) -> None:
        manifest = json.loads(
            (ROOT / "data/providers/taipower_recruit/source-manifest.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(len(manifest["years"]), 22)
        self.assertEqual(len(manifest["exams"]), 23)
        self.assertEqual(manifest["files"], {})
        self.assertEqual(
            manifest["years"]["2018"]["exam_codes"],
            ["taipower-recruit-107-12", "taipower-recruit-107-5"],
        )
        policy = manifest["probe_policy"]
        self.assertEqual(policy["coverage_status"], "partial")
        self.assertEqual(
            policy["known_listing_evidence"]["older_unfiltered_archive"]
            ["indexed_subject_group_count"],
            301,
        )
        retained = policy["retained_local_state"]
        self.assertEqual(retained["normalized_records"], 370)
        self.assertEqual(
            retained["source_only_events"],
            [
                ["taipower-recruit-107-12", 2018],
                ["taipower-recruit-107-5", 2018],
            ],
        )
        self.assertEqual(policy["stale_mirror_files"]["count"], 8)
        self.assertEqual(policy["stale_mirror_files"]["bytes"], 3_570_035)

    def test_taisugar_manifest_records_public_assets_and_login_blocker(self) -> None:
        manifest = json.loads(
            (ROOT / "data/providers/taisugar_recruit/source-manifest.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(len(manifest["years"]), 8)
        self.assertEqual(len(manifest["exams"]), 8)
        self.assertEqual(len(manifest["files"]), 49)
        self.assertEqual(
            sum(item["bytes"] for item in manifest["files"].values()),
            69_909_204,
        )
        policy = manifest["probe_policy"]
        self.assertEqual(policy["coverage_status"], "partial")
        self.assertEqual(policy["listing_evidence"]["declared_row_count"], 35)
        self.assertEqual(policy["current_cycle_blocker"]["status"], "login_required")
        self.assertEqual(len(policy["excluded_paper_rows"]), 2)
        self.assertTrue(
            policy["retained_local_state"]["retained_asset_matches_live_sha256"]
        )

    def test_strict_manifest_requirement_remains_red_until_snapshots_are_complete(self) -> None:
        with self.assertRaisesRegex(ValueError, "complete source discovery remains unresolved") as context:
            validate_source_inventory(ROOT, require_discovery_manifests=True)

        self.assertNotIn("teacher_recruit_kaohsiung", str(context.exception))

    def test_blocked_discovery_requires_exact_provider_coverage_ledger(self) -> None:
        payload = json.loads((ROOT / "catalog/source-inventory.json").read_text(encoding="utf-8"))
        entry = next(
            item for item in payload["providers"]
            if item["provider_id"] == "teacher_recruit_kaohsiung"
        )
        entry["evidence"].remove("catalog/source-coverage/teacher_recruit_kaohsiung.json")

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            catalog = root / "catalog"
            catalog.mkdir()
            (catalog / "source-inventory.json").write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "blocked discovery requires exact provider coverage ledger"):
                load_source_inventory(root)

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
