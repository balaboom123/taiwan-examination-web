import json
import tempfile
import unittest
from pathlib import Path

from app.cli import build_parser, main
from app.lootlabs import LootLabsManifest, LootLabsManifestEntry, LootLabsSettings, write_lootlabs_manifest
from app.migration import migrate_legacy_state


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_legacy_state(root: Path) -> None:
    _write_json(
        root / "data" / "exams" / "2026.json",
        [
            {
                "provider_id": "moex",
                "source_exam_id": "115030",
                "year_ad": 2026,
                "year_roc": 115,
                "exam_name_raw": "115 Nurse Exam",
                "attachments": [],
                "papers": [],
            }
        ],
    )
    _write_json(
        root / "data" / "papers" / "2026.json",
        [
            {
                "provider_id": "moex",
                "canonical_id": "nurse",
                "canonical_name": "Nurse",
                "year_roc": 115,
                "exam_name_raw": "115 Nurse Exam",
                "category_raw": "Nurse",
                "category_code": "101",
                "source_exam_id": "115030",
                "subject_code": "0101",
                "subject_name_raw": "Medical Basics",
                "paper_code": "101-0101-question",
                "file_type": "question",
                "download_url_source": "https://example.test/question.pdf",
                "storage_key": "115/115030/101/0101/question.pdf",
                "checksum": "paper-sha",
            }
        ],
    )
    _write_json(
        root / "data" / "review-queue.json",
        [
            {
                "raw_category": "Nurse",
                "normalized_candidate": "Nurse",
                "source_exam_id": "115030",
                "year_roc": 115,
            }
        ],
    )
    _write_json(root / "data" / "sync-failures.json", [])
    _write_json(
        root / "data" / "source-manifest.json",
        {
            "schema_version": 1,
            "provider_id": "moex",
            "probe_policy": {},
            "years": {},
            "exams": {},
            "files": {},
        },
    )
    _write_json(
        root / "data" / "aliases.json",
        {
            "rules": [
                {
                    "match_type": "exact",
                    "raw_pattern": "Nurse",
                    "canonical_id": "nurse",
                    "canonical_name": "Nurse",
                }
            ]
        },
    )
    _write_json(
        root / "data" / "bundles.json",
        [
            {
                "canonical_id": "nurse",
                "canonical_name": "Nurse",
                "years": [115],
                "file_count": 1,
                "storage_key": "bundles/nurse.zip",
                "asset_name": "nurse.zip",
                "release_tag": "default-bundles-001",
                "download_url": "https://example.test/nurse.zip",
                "checksum": "bundle-sha",
                "legacy_asset_names": ["nurse-legacy.zip"],
            }
        ],
    )
    _write_json(
        root / "data" / "release-assets.json",
        [
            {
                "storage_key": "bundles/nurse.zip",
                "asset_name": "nurse.zip",
                "release_tag": "default-bundles-001",
                "checksum": "bundle-sha",
                "legacy_asset_names": ["nurse-legacy.zip"],
            }
        ],
    )
    write_lootlabs_manifest(
        root / "data" / "lootlabs-links.json",
        LootLabsManifest(
            version=1,
            provider="lootlabs",
            settings=LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1),
            bundles={
                "nurse": LootLabsManifestEntry(
                    canonical_id="nurse",
                    asset_name="nurse.zip",
                    loot_url="https://loot.example/nurse",
                    target_download_url="https://example.test/nurse.zip",
                    target_checksum="bundle-sha",
                    updated_at="2026-06-19T00:00:00+08:00",
                )
            },
        ),
    )

    mirror_path = root / "mirror" / "115" / "115030" / "101" / "0101" / "question.pdf"
    mirror_path.parent.mkdir(parents=True, exist_ok=True)
    mirror_path.write_bytes(b"%PDF-1.7 legacy mirror")

    bundle_path = root / "bundles" / "nurse.zip"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_bytes(b"PK\x03\x04legacy bundle")


class LegacyMigrationTests(unittest.TestCase):
    def test_migrate_legacy_state_parser_accepts_repo_root_provider_site_and_mode(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "migrate-legacy-state",
                "--repo-root",
                "repo",
                "--provider",
                "moex",
                "--site-id",
                "default",
                "--mode",
                "dry-run",
            ]
        )

        self.assertEqual(args.repo_root, Path("repo"))
        self.assertEqual(args.provider, "moex")
        self.assertEqual(args.site_id, "default")
        self.assertEqual(args.mode, "dry-run")

    def test_migrate_legacy_state_dry_run_reports_provider_and_site_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            _seed_legacy_state(root)

            report = migrate_legacy_state(root, provider_id="moex", site_id="default", mode="dry-run")

        self.assertEqual(report.exit_code, 0)
        self.assertIn("data/exams/2026.json -> data/providers/moex/exams/2026.json", report.output)
        self.assertIn("data/bundles.json -> data/sites/default/bundles.json", report.output)
        self.assertIn("bundles/nurse.zip -> bundles/sites/default/nurse.zip", report.output)
        self.assertFalse((root / "data" / "providers" / "moex").exists())
        self.assertFalse((root / "data" / "sites" / "default").exists())

    def test_migrate_legacy_state_move_promotes_provider_site_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            _seed_legacy_state(root)

            report = migrate_legacy_state(root, provider_id="moex", site_id="default", mode="move")

            site_bundles = json.loads((root / "data" / "sites" / "default" / "bundles.json").read_text(encoding="utf-8"))
            release_assets = json.loads((root / "data" / "sites" / "default" / "release-assets.json").read_text(encoding="utf-8"))
            self.assertEqual(report.exit_code, 0)
            self.assertEqual(report.conflicts, [])
            self.assertTrue((root / "data" / "providers" / "moex" / "exams" / "2026.json").exists())
            self.assertTrue((root / "data" / "providers" / "moex" / "papers" / "2026.json").exists())
            self.assertTrue((root / "data" / "providers" / "moex" / "source-manifest.json").exists())
            self.assertTrue((root / "data" / "providers" / "moex" / "aliases.json").exists())
            self.assertTrue((root / "mirror" / "providers" / "moex" / "115" / "115030" / "101" / "0101" / "question.pdf").exists())
            self.assertTrue((root / "bundles" / "sites" / "default" / "nurse.zip").exists())
            self.assertFalse((root / "data" / "exams" / "2026.json").exists())
            self.assertFalse((root / "data" / "bundles.json").exists())
            self.assertFalse((root / "bundles" / "nurse.zip").exists())
            self.assertEqual(site_bundles["site_id"], "default")
            self.assertEqual(site_bundles["bundles"][0]["storage_key"], "bundles/sites/default/nurse.zip")
            self.assertEqual(release_assets["site_id"], "default")
            self.assertEqual(release_assets["assets"][0]["storage_key"], "bundles/sites/default/nurse.zip")

    def test_migrate_legacy_state_verify_succeeds_after_move(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            _seed_legacy_state(root)

            move_report = migrate_legacy_state(root, provider_id="moex", site_id="default", mode="move")
            verify_report = migrate_legacy_state(root, provider_id="moex", site_id="default", mode="verify")

        self.assertEqual(move_report.exit_code, 0)
        self.assertEqual(verify_report.exit_code, 0)
        self.assertIn("Verification passed", verify_report.output)

    def test_migrate_legacy_state_verify_reports_conflicting_duplicate_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            _seed_legacy_state(root)
            scoped_path = root / "mirror" / "providers" / "moex" / "115" / "115030" / "101" / "0101" / "question.pdf"
            scoped_path.parent.mkdir(parents=True, exist_ok=True)
            scoped_path.write_bytes(b"%PDF-1.7 conflicting mirror")

            report = migrate_legacy_state(root, provider_id="moex", site_id="default", mode="verify")

        self.assertNotEqual(report.exit_code, 0)
        self.assertTrue(report.conflicts)
        self.assertIn("Conflict", report.output)

    def test_command_migrate_legacy_state_returns_non_zero_on_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            _seed_legacy_state(root)
            scoped_path = root / "mirror" / "providers" / "moex" / "115" / "115030" / "101" / "0101" / "question.pdf"
            scoped_path.parent.mkdir(parents=True, exist_ok=True)
            scoped_path.write_bytes(b"%PDF-1.7 conflicting mirror")

            exit_code = main(
                [
                    "migrate-legacy-state",
                    "--repo-root",
                    str(root),
                    "--provider",
                    "moex",
                    "--site-id",
                    "default",
                    "--mode",
                    "verify",
                ]
            )

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
