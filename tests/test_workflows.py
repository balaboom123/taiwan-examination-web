import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_SCRIPT_PATH = REPO_ROOT / ".github" / "scripts" / "release_assets.py"


def _load_release_script():
    spec = importlib.util.spec_from_file_location("release_assets", RELEASE_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _workflow_push_paths(workflow: str) -> list[str]:
    paths: list[str] = []
    inside_push = False
    inside_paths = False

    for line in workflow.splitlines():
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped == "push:" and indent == 2:
            inside_push = True
            inside_paths = False
            continue

        if inside_push and stripped and indent <= 2:
            inside_push = False
            inside_paths = False

        if not inside_push:
            continue

        if stripped == "paths:" and indent == 4:
            inside_paths = True
            continue

        if inside_paths and stripped.startswith("- ") and indent == 6:
            paths.append(stripped[2:])
            continue

        if inside_paths and stripped and indent <= 4:
            inside_paths = False

    return paths


class WorkflowTests(unittest.TestCase):
    def test_incremental_workflow_bootstraps_with_full_sync_when_release_is_incomplete(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("release_assets.py coverage", workflow)
        self.assertIn("bootstrap_required", workflow)
        self.assertIn("python -m app sync-full", workflow)
        self.assertIn("steps.release_state.outputs.bootstrap_required == 'true'", workflow)

    def test_incremental_workflow_probes_before_syncing(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("python -m app probe-latest --years 2", workflow)
        self.assertIn("python -m app sync-targeted", workflow)
        self.assertLess(workflow.index("python -m app probe-latest"), workflow.index("python -m app sync-targeted"))

    def test_incremental_workflow_can_exit_before_heavy_steps_when_unchanged(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("steps.probe.outputs.should_sync == 'true'", workflow)
        self.assertIn(".tmp/source-probe.json", workflow)
        self.assertIn("steps.probe.outputs.should_sync != 'true'", workflow)
        self.assertIn("git add data/source-manifest.json", workflow)

    def test_incremental_workflow_does_not_download_release_bundles_before_probe(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertNotIn('gh release download "$MOEX_RELEASE_TAG" --pattern "*.zip" --dir bundles', workflow)
        self.assertIn("--download-affected-bundles", workflow)

    def test_monthly_audit_workflow_exists(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "audit-recent.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn('- cron: "45 3 1 * *"', workflow)
        self.assertIn("release_assets.py coverage", workflow)
        self.assertIn("bootstrap_required", workflow)
        self.assertIn("python -m app sync-full", workflow)
        self.assertIn("python -m app sync-incremental --years 2", workflow)
        self.assertIn("--write-manifest", workflow)
        self.assertIn("release_assets.py prune", workflow)

    def test_workflows_prune_stale_assets_via_shared_script(self) -> None:
        workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertIn("release_assets.py upload", workflow)
            self.assertIn("release_assets.py prune", workflow)

    def test_workflows_sync_lootlabs_after_release_asset_updates(self) -> None:
        workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
        commit_steps = {
            "sync-full.yml": "Commit regenerated data and site",
            "sync-incremental.yml": "Commit regenerated data and site",
            "audit-recent.yml": "Commit audited data and site",
        }
        for workflow_name, commit_step in commit_steps.items():
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            sync_lootlabs_index = workflow.index("python -m app sync-lootlabs")
            self.assertIn("python -m app sync-lootlabs", workflow)
            self.assertLess(workflow.index("release_assets.py upload"), sync_lootlabs_index)
            self.assertLess(workflow.index("release_assets.py prune"), sync_lootlabs_index)
            self.assertLess(sync_lootlabs_index, workflow.index(commit_step))

    def test_pages_deploy_rebuilds_when_lootlabs_manifest_changes(self) -> None:
        workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "deploy-pages.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("data/lootlabs-links.json", _workflow_push_paths(workflow))

    def test_pages_deploy_path_check_ignores_occurrences_outside_push_paths(self) -> None:
        workflow = """name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - frontend/**
  workflow_dispatch:

jobs:
  deploy:
    steps:
      - run: echo data/lootlabs-links.json
"""

        self.assertNotIn("data/lootlabs-links.json", _workflow_push_paths(workflow))

    def test_release_script_only_deletes_stale_zip_assets(self) -> None:
        module = _load_release_script()
        release_payload = json.dumps(
            {"assets": [{"name": "keep.zip"}, {"name": "stale.zip"}, {"name": "notes.txt"}]}
        )
        with mock.patch.object(module, "_local_assets", return_value=[{"asset_name": "keep.zip"}]), \
                mock.patch.object(module.subprocess, "check_output", return_value=release_payload), \
                mock.patch.object(module.subprocess, "run") as run_mock:
            exit_code = module.prune()

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [["gh", "release", "delete-asset", module.RELEASE_TAG, "stale.zip", "--yes"]],
        )

    def test_release_script_never_prunes_legacy_alias_assets(self) -> None:
        module = _load_release_script()
        local_assets = [{"asset_name": "nurse-id.zip", "legacy_asset_names": ["護理師__nurse.zip", "nurse.zip"]}]
        release_payload = json.dumps(
            {"assets": [{"name": "nurse-id.zip"}, {"name": "護理師__nurse.zip"}, {"name": "nurse.zip"}, {"name": "stale.zip"}]}
        )
        with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                mock.patch.object(module.subprocess, "check_output", return_value=release_payload), \
                mock.patch.object(module.subprocess, "run") as run_mock:
            self.assertEqual(module.prune(), 0)

        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [["gh", "release", "delete-asset", module.RELEASE_TAG, "stale.zip", "--yes"]],
        )

    def test_release_script_coverage_compares_expected_and_current_zip_names(self) -> None:
        module = _load_release_script()
        local_assets = [{"asset_name": "a.zip", "legacy_asset_names": ["a-alias.zip"]}]
        cases = [
            ([], "bootstrap_required=true"),
            (["a.zip"], "bootstrap_required=true"),
            (["a-alias.zip", "a.zip"], "bootstrap_required=false"),
        ]
        for release_names, expected_line in cases:
            with self.subTest(release_names=release_names):
                with tempfile.TemporaryDirectory() as tmp:
                    output_path = Path(tmp) / "github-output"
                    with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                            mock.patch.object(module, "_release_zip_names", return_value=release_names), \
                            mock.patch.dict(module.os.environ, {"GITHUB_OUTPUT": str(output_path)}):
                        self.assertEqual(module.coverage(), 0)
                    self.assertIn(expected_line, output_path.read_text(encoding="utf-8"))

    def test_release_script_uploads_primary_and_legacy_asset_names(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "bundle.zip"
            bundle_path.write_bytes(b"PK\x05\x06")
            local_assets = [
                {"storage_key": str(bundle_path), "asset_name": "nurse-id.zip", "legacy_asset_names": ["nurse.zip"]}
            ]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 0)

        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [
                ["gh", "release", "upload", module.RELEASE_TAG, f"{bundle_path}#nurse-id.zip", "--clobber"],
                ["gh", "release", "upload", module.RELEASE_TAG, f"{bundle_path}#nurse.zip", "--clobber"],
            ],
        )

    def test_release_script_upload_fails_when_local_bundle_files_missing(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            absent = str(Path(tmp) / "absent.zip")
            local_assets = [{"storage_key": absent, "asset_name": "absent.zip"}]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 1)
        run_mock.assert_not_called()

    def test_workflows_no_longer_install_or_use_ghostscript(self) -> None:
        workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertNotIn("ghostscript", workflow.lower())
            self.assertNotIn("--optimize-pdfs", workflow)
            self.assertNotIn("--pdf-quality", workflow)
            self.assertNotIn("--rewrite-existing-pdfs", workflow)

    def test_workflows_use_plain_manifest_based_mirror_cache(self) -> None:
        workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertIn("moex-mirror-${{ hashFiles('data/source-manifest.json') }}", workflow)
            self.assertNotIn("PDF_CACHE_VERSION", workflow)
            self.assertNotIn("PDF_QUALITY_PROFILE", workflow)

    def test_workflows_describe_downloadable_bundle_release(self) -> None:
        workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertIn("release_assets.py ensure", workflow)

        module = _load_release_script()
        with mock.patch.object(module.subprocess, "run") as run_mock:
            run_mock.side_effect = [mock.Mock(returncode=1), mock.Mock(returncode=0)]
            self.assertEqual(module.ensure(), 0)
        create_command = run_mock.call_args_list[1].args[0]
        self.assertIn("MOEX downloadable bundles", create_command)
        self.assertIn("Human-friendly exam bundles with compatibility aliases", create_command)

    def test_readme_documents_human_friendly_bundle_assets(self) -> None:
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")

        self.assertIn("Bundle filenames use Chinese display names plus canonical IDs.", readme)
        self.assertIn("Release assets can include legacy compatibility alias names during migration.", readme)
        self.assertIn("Bundle asset: `護理師__nurse.zip`", readme)
        self.assertIn("Archive entry: `115/115030_護理師/101_0101_基礎醫學_試題.pdf`", readme)
        self.assertNotIn("optimize-mirror-pdfs", readme)


if __name__ == "__main__":
    unittest.main()
