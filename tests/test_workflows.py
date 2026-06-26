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
    def test_incremental_workflow_fails_fast_when_release_is_incomplete_on_hosted_ci(self) -> None:
        workflow_path = REPO_ROOT / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("release_assets.py coverage", workflow)
        self.assertIn("bootstrap_required", workflow)
        self.assertNotIn("python -m app sync-full", workflow)
        self.assertIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertIn("steps.release_state.outputs.bootstrap_required == 'true'", workflow)
        self.assertIn("Hosted bootstrap is unsupported on GitHub-hosted runners.", workflow)

    def test_incremental_workflow_probes_before_syncing(self) -> None:
        workflow_path = REPO_ROOT / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("python -m app probe-latest --provider moex --years 2 --manifest data/providers/moex/source-manifest.json", workflow)
        self.assertIn(
            "python -m app sync-targeted --provider moex --probe .tmp/source-probe.json --manifest data/providers/moex/source-manifest.json --download-affected-bundles --publish-plan-output .tmp/site-publish-plan.json",
            workflow,
        )
        self.assertIn(
            'python -m app publish-site --site-id default --repository "${{ github.repository }}" --publish-plan .tmp/site-publish-plan.json',
            workflow,
        )
        self.assertLess(workflow.index("python -m app probe-latest"), workflow.index("python -m app sync-targeted"))
        self.assertLess(workflow.index("python -m app sync-targeted"), workflow.index("python -m app publish-site"))

    def test_incremental_workflow_can_exit_before_heavy_steps_when_unchanged(self) -> None:
        workflow_path = REPO_ROOT / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("steps.probe.outputs.should_sync == 'true'", workflow)
        self.assertIn(".tmp/source-probe.json", workflow)
        self.assertIn("steps.probe.outputs.should_sync != 'true'", workflow)
        self.assertIn("git add data/providers/moex/source-manifest.json", workflow)

    def test_incremental_workflow_downloads_only_affected_release_bundles_via_targeted_sync(self) -> None:
        workflow_path = REPO_ROOT / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertNotIn('gh release download "$MOEX_RELEASE_TAG" --pattern "*.zip" --dir bundles', workflow)
        self.assertIn("--download-affected-bundles", workflow)
        self.assertIn("--publish-plan-output .tmp/site-publish-plan.json", workflow)

    def test_monthly_audit_workflow_exists(self) -> None:
        workflow_path = REPO_ROOT / ".github" / "workflows" / "audit-recent.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn('- cron: "45 3 1 * *"', workflow)
        self.assertIn("release_assets.py coverage", workflow)
        self.assertIn("bootstrap_required", workflow)
        self.assertNotIn("python -m app sync-full --provider moex --write-manifest --manifest data/providers/moex/source-manifest.json", workflow)
        self.assertIn("Hosted bootstrap is unsupported on GitHub-hosted runners.", workflow)
        self.assertIn(
            "python -m app sync-incremental --provider moex --years 2 --write-manifest --manifest data/providers/moex/source-manifest.json --download-affected-bundles --publish-plan-output .tmp/site-publish-plan.json",
            workflow,
        )
        self.assertIn(
            'python -m app publish-site --site-id default --repository "${{ github.repository }}" --publish-plan .tmp/site-publish-plan.json',
            workflow,
        )
        self.assertIn("--write-manifest", workflow)
        self.assertIn("release_assets.py prune", workflow)

    def test_workflows_prune_stale_assets_via_shared_script(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertIn("release_assets.py upload", workflow)
            self.assertIn("release_assets.py prune", workflow)

    def test_workflows_sync_lootlabs_after_release_asset_updates(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        commit_steps = {
            "sync-full.yml": "Commit regenerated data",
            "sync-incremental.yml": "Commit regenerated data",
            "audit-recent.yml": "Commit audited data",
        }
        for workflow_name, commit_step in commit_steps.items():
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            sync_lootlabs_index = workflow.index("python -m app sync-lootlabs --site-id default")
            self.assertIn("python -m app sync-lootlabs --site-id default", workflow)
            self.assertLess(workflow.index("release_assets.py upload"), sync_lootlabs_index)
            self.assertLess(workflow.index("release_assets.py prune"), sync_lootlabs_index)
            self.assertLess(sync_lootlabs_index, workflow.index(commit_step))

    def test_sync_workflows_do_not_stage_legacy_site_output(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertNotIn("git add -f site", workflow)

    def test_pages_deploy_rebuilds_when_site_scoped_bundle_inputs_change(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
        push_paths = _workflow_push_paths(workflow)

        self.assertIn("data/sites/default/bundles.json", push_paths)
        self.assertIn("data/sites/default/lootlabs-links.json", push_paths)

    def test_pages_deploy_syncs_lootlabs_manifest_before_frontend_build(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")

        self.assertIn("actions/setup-python@v5", workflow)
        self.assertIn('python-version: "3.12"', workflow)
        self.assertIn("python -m app sync-lootlabs --site-id default", workflow)
        self.assertIn("LOOTLABS_API_KEY: ${{ secrets.LOOTLABS_API_KEY }}", workflow)
        self.assertIn('VITE_ENABLE_LOOTLABS_GATING: "true"', workflow)
        self.assertLess(workflow.index("actions/setup-python@v5"), workflow.index("python -m app sync-lootlabs --site-id default"))
        self.assertLess(workflow.index("python -m app sync-lootlabs --site-id default"), workflow.index("npm run build"))

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
      - run: echo data/sites/default/lootlabs-links.json
"""

        self.assertNotIn("data/sites/default/lootlabs-links.json", _workflow_push_paths(workflow))

    def test_release_script_only_deletes_stale_zip_assets(self) -> None:
        module = _load_release_script()
        release_payload = json.dumps(
            {"assets": [{"name": "keep.zip"}, {"name": "stale.zip"}, {"name": "notes.txt"}]}
        )
        with mock.patch.object(module, "_local_assets", return_value=[{"asset_name": "keep.zip", "release_tag": "default-bundles-001"}]), \
                mock.patch.object(module.subprocess, "check_output", return_value=release_payload), \
                mock.patch.object(module.subprocess, "run") as run_mock:
            exit_code = module.prune()

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [["gh", "release", "delete-asset", "default-bundles-001", "stale.zip", "--yes"]],
        )

    def test_release_script_never_prunes_legacy_alias_assets(self) -> None:
        module = _load_release_script()
        local_assets = [
            {
                "asset_name": "nurse-id.zip",
                "legacy_asset_names": ["nurse-display.zip", "nurse.zip"],
                "release_tag": "default-bundles-001",
            }
        ]
        release_payload = json.dumps(
            {"assets": [{"name": "nurse-id.zip"}, {"name": "nurse-display.zip"}, {"name": "nurse.zip"}, {"name": "stale.zip"}]}
        )
        with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                mock.patch.object(module.subprocess, "check_output", return_value=release_payload), \
                mock.patch.object(module.subprocess, "run") as run_mock:
            self.assertEqual(module.prune(), 0)

        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [["gh", "release", "delete-asset", "default-bundles-001", "stale.zip", "--yes"]],
        )

    def test_release_script_reads_wrapped_site_release_assets_schema(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            release_assets_path = Path(tmp) / "release-assets.json"
            release_assets_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "site_id": "default",
                        "assets": [{"asset_name": "nurse.zip", "release_tag": "default-bundles-001"}],
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(module, "RELEASE_ASSETS_PATH", release_assets_path):
                self.assertEqual(module._local_assets(), [{"asset_name": "nurse.zip", "release_tag": "default-bundles-001"}])

    def test_release_script_defaults_to_scoped_site_release_assets_path(self) -> None:
        module = _load_release_script()

        self.assertEqual(module.RELEASE_ASSETS_PATH, Path("data") / "sites" / "default" / "release-assets.json")

    def test_release_script_fails_closed_when_release_tag_metadata_is_missing(self) -> None:
        module = _load_release_script()

        with mock.patch.object(module, "RELEASE_TAG", ""):
            with self.assertRaisesRegex(ValueError, "missing release_tag"):
                module._group_assets_by_release_tag([{"asset_name": "nurse.zip"}])

    def test_release_script_coverage_compares_expected_and_current_zip_names(self) -> None:
        module = _load_release_script()
        local_assets = [{"asset_name": "a.zip", "legacy_asset_names": ["a-alias.zip"], "release_tag": "default-bundles-001"}]
        cases = [
            ([], "bootstrap_required=true"),
            (["a-alias.zip"], "bootstrap_required=true"),
            (["a.zip"], "bootstrap_required=false"),
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

    def test_release_script_reads_release_metadata_as_utf8(self) -> None:
        module = _load_release_script()
        payload = json.dumps({"assets": [{"name": "學科能力測驗__ceec-gsat.zip"}]}, ensure_ascii=False)

        with mock.patch.object(module.subprocess, "check_output", return_value=payload) as check_output_mock:
            self.assertEqual(module._release_zip_names("default-bundles-002"), ["學科能力測驗__ceec-gsat.zip"])

        self.assertEqual(
            check_output_mock.call_args,
            mock.call(
                ["gh", "release", "view", "default-bundles-002", "--json", "assets"],
                text=True,
                encoding="utf-8",
            ),
        )

    def test_release_script_uploads_primary_asset_name_only(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "bundle.zip"
            bundle_path.write_bytes(b"PK\x05\x06")
            local_assets = [
                {
                    "storage_key": str(bundle_path),
                    "asset_name": "nurse-id.zip",
                    "legacy_asset_names": ["nurse.zip"],
                    "release_tag": "default-bundles-001",
                }
            ]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_names", return_value=[]), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 0)

        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [
                [
                    "gh",
                    "release",
                    "upload",
                    "default-bundles-001",
                    f"{bundle_path}#nurse-id.zip",
                    "--clobber",
                ],
            ],
        )

    def test_release_script_upload_skips_remote_zip_names_that_already_exist(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "bundle.zip"
            bundle_path.write_bytes(b"PK\x05\x06")
            local_assets = [
                {
                    "storage_key": str(bundle_path),
                    "asset_name": "nurse-id.zip",
                    "legacy_asset_names": ["nurse.zip"],
                    "release_tag": "default-bundles-001",
                }
            ]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_names", return_value=["nurse-id.zip"]), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 0)

        run_mock.assert_not_called()

    def test_release_script_upload_groups_assets_by_release_tag(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            first_path = Path(tmp) / "first.zip"
            second_path = Path(tmp) / "second.zip"
            first_path.write_bytes(b"PK\x05\x06")
            second_path.write_bytes(b"PK\x05\x06")
            local_assets = [
                {"storage_key": str(first_path), "asset_name": "first.zip", "release_tag": "default-bundles-001"},
                {"storage_key": str(second_path), "asset_name": "second.zip", "release_tag": "default-bundles-002"},
            ]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_names", return_value=[]), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 0)

        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [
                ["gh", "release", "upload", "default-bundles-001", f"{first_path}#first.zip", "--clobber"],
                ["gh", "release", "upload", "default-bundles-002", f"{second_path}#second.zip", "--clobber"],
            ],
        )

    def test_release_script_upload_fails_when_local_bundle_files_missing(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            absent = str(Path(tmp) / "absent.zip")
            local_assets = [{"storage_key": absent, "asset_name": "absent.zip", "release_tag": "default-bundles-001"}]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_names", return_value=[]), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 1)
        run_mock.assert_not_called()

    def test_release_script_upload_skips_missing_local_bundle_when_remote_asset_already_exists(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            absent = str(Path(tmp) / "nurse.zip")
            local_assets = [{"storage_key": absent, "asset_name": "nurse.zip", "release_tag": "default-bundles-001"}]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_names", return_value=["nurse.zip"]), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 0)

        run_mock.assert_not_called()

    def test_workflows_no_longer_install_or_use_ghostscript(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml", "sync-ceec-gsat.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertNotIn("ghostscript", workflow.lower())
            self.assertNotIn("--optimize-pdfs", workflow)
            self.assertNotIn("--pdf-quality", workflow)
            self.assertNotIn("--rewrite-existing-pdfs", workflow)

    def test_workflows_use_plain_manifest_based_mirror_cache(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertIn("moex-mirror-${{ hashFiles('data/providers/moex/source-manifest.json') }}", workflow)
            self.assertNotIn("PDF_CACHE_VERSION", workflow)
            self.assertNotIn("PDF_QUALITY_PROFILE", workflow)

    def test_workflows_define_timeout_and_concurrency_controls(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertIn("concurrency:", workflow)
            self.assertIn("timeout-minutes:", workflow)

    def test_workflows_describe_downloadable_bundle_release(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertIn("python -m app publish-site --site-id default", workflow)
            self.assertIn("release_assets.py ensure", workflow)

        module = _load_release_script()
        local_assets = [{"asset_name": "nurse.zip", "release_tag": "default-bundles-001"}]
        with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                mock.patch.object(module.subprocess, "run") as run_mock:
            run_mock.side_effect = [mock.Mock(returncode=1), mock.Mock(returncode=0)]
            self.assertEqual(module.ensure(), 0)
        create_command = run_mock.call_args_list[1].args[0]
        self.assertIn("default-bundles-001", create_command)
        self.assertTrue(any("Downloadable exam bundles" in part for part in create_command))
        self.assertTrue(any("Human-friendly exam bundles with compatibility aliases" in part for part in create_command))

    def test_sync_full_workflow_requires_explicit_override_before_running_unsupported_hosted_bootstrap(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-full.yml").read_text(encoding="utf-8")

        self.assertIn("allow_unsupported_hosted_bootstrap", workflow)
        self.assertIn("Hosted bootstrap is unsupported on GitHub-hosted runners.", workflow)
        self.assertIn("python -m app sync-full --provider moex --write-manifest --manifest data/providers/moex/source-manifest.json", workflow)

    def test_sync_ceec_gsat_workflow_is_provider_only_until_default_site_publication_is_safe(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-ceec-gsat.yml").read_text(encoding="utf-8")

        self.assertIn('- cron: "20 3 * * 6"', workflow)
        self.assertIn("python -m app sync-full --provider ceec_gsat --site-id default", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("python -m app sync-lootlabs --site-id default", workflow)
        self.assertNotIn("release_assets.py ensure", workflow)
        self.assertNotIn("release_assets.py upload", workflow)
        self.assertNotIn("release_assets.py prune", workflow)

    def test_readme_documents_human_friendly_bundle_assets(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Bundle filenames use Chinese display names plus canonical IDs.", readme)
        self.assertIn("Release assets can include legacy compatibility alias names during migration.", readme)
        self.assertIn("Bundle asset: `\u8b77\u7406\u5e2b__nurse.zip`", readme)
        self.assertIn(
            "Archive entry: `115/115030_\u8b77\u7406\u5e2b/101_0101_\u57fa\u790e\u91ab\u5b78_\u8a66\u984c.pdf`",
            readme,
        )
        self.assertNotIn("optimize-mirror-pdfs", readme)


class FinancialCertWorkflowTests(unittest.TestCase):
    def test_sync_sfi_cert_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-sfi-cert.yml").read_text(encoding="utf-8")

        self.assertIn("python -m app sync-full --provider sfi_cert --site-id default", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("python -m app sync-lootlabs --site-id default", workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_tabf_cert_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-tabf-cert.yml").read_text(encoding="utf-8")

        self.assertIn("python -m app sync-full --provider tabf_cert --site-id default", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("python -m app sync-lootlabs --site-id default", workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_tii_cert_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-tii-cert.yml").read_text(encoding="utf-8")

        self.assertIn("python -m app sync-full --provider tii_cert --site-id default", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("python -m app sync-lootlabs --site-id default", workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_financial_cert_workflows_have_schedule(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for name in ("sync-sfi-cert.yml", "sync-tabf-cert.yml", "sync-tii-cert.yml"):
            with self.subTest(name=name):
                workflow = (workflows_dir / name).read_text(encoding="utf-8")
                self.assertIn("schedule:", workflow)
                self.assertIn("cron:", workflow)
                self.assertIn("workflow_dispatch:", workflow)


if __name__ == "__main__":
    unittest.main()
