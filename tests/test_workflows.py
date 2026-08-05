import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_SCRIPT_PATH = REPO_ROOT / ".github" / "scripts" / "release_assets.py"
_EMPTY_ZIP = b"PK\x05\x06"
_EMPTY_ZIP_DIGEST = hashlib.sha256(_EMPTY_ZIP).hexdigest()


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
        self.assertIn("commit-and-push.sh \"chore: refresh source manifest\" data/providers/moex/source-manifest.json", workflow)

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

    def test_sync_workflows_do_not_stage_legacy_site_output(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertNotIn("git add -f site", workflow)

    def test_pages_deploy_rebuilds_when_site_scoped_bundle_inputs_change(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
        push_paths = _workflow_push_paths(workflow)

        for expected_path in (
            "data/providers/**",
            "data/sites/default/**",
            "app/**",
            "scripts/validate_publication.py",
        ):
            self.assertIn(expected_path, push_paths)

    def test_pages_deploy_runs_catalog_and_frontend_gates_before_upload(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")

        for required in (
            "actions/setup-python@v5",
            "python -m pytest -q",
            "python -m app audit-catalog",
            "python -m app history-audit",
            "python scripts/validate_publication.py",
            "python scripts/validate_source_inventory.py",
            "python -m app plan-release",
            "npm test",
            "npm run lint",
            "npm run build",
        ):
            self.assertIn(required, workflow)
        self.assertLess(workflow.index("python scripts/validate_publication.py"), workflow.index("npm ci"))
        self.assertLess(workflow.index("npm run lint"), workflow.index("npm run build"))
        self.assertLess(workflow.index("npm run build"), workflow.index("actions/upload-pages-artifact@v5"))

    def test_mirrorless_workflows_skip_the_mirror_dimension_of_history_audit(self) -> None:
        # Both workflows check out without the gitignored mirror tree. Without
        # the opt-out every retained paper reports a download gap, so the gate
        # can never pass and the Pages deploy never runs.
        for name in ("ci.yml", "deploy-pages.yml"):
            workflow = (REPO_ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
            invocations = [line for line in workflow.splitlines() if "app history-audit" in line]
            with self.subTest(workflow=name):
                self.assertTrue(invocations, f"{name} no longer runs history-audit")
                for line in invocations:
                    self.assertIn("--skip-mirror-check", line)

    def test_release_script_only_deletes_stale_zip_assets(self) -> None:
        module = _load_release_script()
        release_digests = {"keep.zip": "keep-digest", "stale.zip": "stale-digest"}
        with mock.patch.object(module, "_local_assets", return_value=[{"asset_name": "keep.zip", "release_tag": "default-bundles-001"}]), \
                mock.patch.object(module, "_release_zip_digests", return_value=release_digests), \
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
        release_digests = {
            "nurse-id.zip": "a", "nurse-display.zip": "b", "nurse.zip": "c", "stale.zip": "d",
        }
        with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                mock.patch.object(module, "_release_zip_digests", return_value=release_digests), \
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
        local_assets = [
            {
                "asset_name": "a.zip",
                "legacy_asset_names": ["a-alias.zip"],
                "release_tag": "default-bundles-001",
                "checksum": "current-digest",
            }
        ]
        cases = [
            ({}, "bootstrap_required=true"),
            ({"a-alias.zip": "current-digest"}, "bootstrap_required=true"),
            ({"a.zip": "current-digest"}, "bootstrap_required=false"),
            ({"a-alias.zip": "current-digest", "a.zip": "current-digest"}, "bootstrap_required=false"),
        ]
        for release_digests, expected_line in cases:
            with self.subTest(release_digests=release_digests):
                with tempfile.TemporaryDirectory() as tmp:
                    output_path = Path(tmp) / "github-output"
                    with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                            mock.patch.object(module, "_release_zip_digests", return_value=release_digests), \
                            mock.patch.dict(module.os.environ, {"GITHUB_OUTPUT": str(output_path)}):
                        self.assertEqual(module.coverage(), 0)
                    self.assertIn(expected_line, output_path.read_text(encoding="utf-8"))

    def test_release_script_coverage_reports_published_bytes_that_lost_their_checksum(self) -> None:
        # The asset name is derived from bundle identity and stays put across a
        # rebuild, so a name-only check reads a pre-recovery download as covered.
        module = _load_release_script()
        local_assets = [
            {"asset_name": "a.zip", "release_tag": "default-bundles-001", "checksum": "rebuilt-digest"}
        ]
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "github-output"
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_digests", return_value={"a.zip": "pre-recovery-digest"}), \
                    mock.patch.dict(module.os.environ, {"GITHUB_OUTPUT": str(output_path)}):
                self.assertEqual(module.coverage(), 0)
            recorded = output_path.read_text(encoding="utf-8")

        self.assertIn("stale_required=true", recorded)
        # Stale bytes are repaired by the upload step, so they must not be
        # reported as a bootstrap the hosted runner has to refuse.
        self.assertIn("bootstrap_required=false", recorded)

    def test_release_script_reads_release_metadata_as_utf8(self) -> None:
        module = _load_release_script()
        payloads = ["4242\n", "學科能力測驗__ceec-gsat.zip\tsha256:abc123\nnotes.txt\t\n"]

        with mock.patch.object(module.subprocess, "check_output", side_effect=payloads) as check_output_mock, \
                mock.patch.dict(module.os.environ, {"GITHUB_REPOSITORY": "owner/repo"}):
            self.assertEqual(
                module._release_zip_digests("default-bundles-002"),
                {"學科能力測驗__ceec-gsat.zip": "abc123"},
            )

        self.assertEqual(
            [call.args[0] for call in check_output_mock.call_args_list],
            [
                ["gh", "api", "repos/owner/repo/releases/tags/default-bundles-002", "--jq", ".id"],
                [
                    "gh", "api", "--paginate",
                    "repos/owner/repo/releases/4242/assets?per_page=100",
                    "--jq", '.[] | [.name, (.digest // "")] | @tsv',
                ],
            ],
        )
        for call in check_output_mock.call_args_list:
            self.assertEqual(call.kwargs["encoding"], "utf-8")

    def test_release_script_reports_undigested_release_asset_as_unverifiable(self) -> None:
        # GitHub returns no digest for some older assets. Treating that as a
        # match would make the byte-level check silently vacuous.
        module = _load_release_script()
        payloads = ["7\n", "nurse.zip\t\n"]

        with mock.patch.object(module.subprocess, "check_output", side_effect=payloads):
            self.assertEqual(module._release_zip_digests("default-bundles-001"), {"nurse.zip": ""})

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
                    mock.patch.object(module, "_release_zip_digests", return_value={}), \
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

    def test_release_script_rejects_assets_at_github_byte_limit(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "bundle.zip"
            bundle_path.write_bytes(b"PK\x05\x06")
            local_assets = [{
                "storage_key": str(bundle_path),
                "asset_name": "bundle.zip",
                "release_tag": "default-bundles-001",
            }]
            with mock.patch.object(module, "GITHUB_RELEASE_ASSET_BYTE_LIMIT", 1), \
                    mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_digests", return_value={}), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 1)
        run_mock.assert_not_called()

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
                    mock.patch.object(module, "_release_zip_digests", return_value={"nurse-id.zip": _EMPTY_ZIP_DIGEST}), \
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
                    mock.patch.object(module, "_release_zip_digests", return_value={}), \
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
                    mock.patch.object(module, "_release_zip_digests", return_value={}), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 1)
        run_mock.assert_not_called()

    def test_release_script_upload_skips_missing_local_bundle_when_remote_asset_already_exists(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            absent = str(Path(tmp) / "nurse.zip")
            local_assets = [{"storage_key": absent, "asset_name": "nurse.zip", "release_tag": "default-bundles-001"}]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_digests", return_value={"nurse.zip": _EMPTY_ZIP_DIGEST}), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 0)

        run_mock.assert_not_called()

    def test_release_script_reuploads_when_published_bytes_are_stale(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "bundle.zip"
            bundle_path.write_bytes(_EMPTY_ZIP)
            local_assets = [
                {
                    "storage_key": str(bundle_path),
                    "asset_name": "nurse-id.zip",
                    "release_tag": "default-bundles-001",
                    "checksum": _EMPTY_ZIP_DIGEST,
                }
            ]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(
                        module, "_release_zip_digests", return_value={"nurse-id.zip": "pre-recovery-digest"}
                    ), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 0)

        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [
                [
                    "gh", "release", "upload", "default-bundles-001",
                    f"{bundle_path}#nurse-id.zip", "--clobber",
                ],
            ],
        )

    def test_release_script_upload_refuses_bundles_that_contradict_the_published_checksum(self) -> None:
        # Uploading here would serve bytes that fail the checksum the site
        # publishes for verification; the catalog has to be regenerated first.
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "bundle.zip"
            bundle_path.write_bytes(_EMPTY_ZIP)
            local_assets = [
                {
                    "storage_key": str(bundle_path),
                    "asset_name": "nurse-id.zip",
                    "release_tag": "default-bundles-001",
                    "checksum": "checksum-from-an-older-build",
                }
            ]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(module, "_release_zip_digests", return_value={}), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 1)

        run_mock.assert_not_called()

    def test_release_script_upload_leaves_assets_whose_published_bytes_already_match(self) -> None:
        module = _load_release_script()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "bundle.zip"
            bundle_path.write_bytes(_EMPTY_ZIP)
            local_assets = [
                {
                    "storage_key": str(bundle_path),
                    "asset_name": "nurse-id.zip",
                    "release_tag": "default-bundles-001",
                    "checksum": _EMPTY_ZIP_DIGEST,
                }
            ]
            with mock.patch.object(module, "_local_assets", return_value=local_assets), \
                    mock.patch.object(
                        module, "_release_zip_digests", return_value={"nurse-id.zip": _EMPTY_ZIP_DIGEST}
                    ), \
                    mock.patch.object(module.subprocess, "run") as run_mock:
                self.assertEqual(module.upload(), 0)

        run_mock.assert_not_called()

    def test_incremental_sync_repairs_stale_release_bytes_without_a_source_change(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-incremental.yml").read_text(encoding="utf-8")
        upload_condition = next(
            line for line in workflow.splitlines()
            if "if:" in line and "stale_required" in line
        )
        self.assertIn("steps.release_state.outputs.stale_required == 'true'", upload_condition)
        self.assertIn("steps.probe.outputs.should_sync == 'true'", upload_condition)

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

    def test_cold_cache_workflows_have_full_hosted_timeout_budget(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_name in ("sync-full.yml", "sync-incremental.yml", "audit-recent.yml", "sync-hakka-cert.yml"):
            workflow = (workflows_dir / workflow_name).read_text(encoding="utf-8")
            self.assertIn("timeout-minutes: 360", workflow, workflow_name)

    def test_shared_commit_commands_are_valid_yaml_block_scalars(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for workflow_path in sorted(workflows_dir.glob("*.yml")):
            lines = workflow_path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                if "commit-and-push.sh" not in line:
                    continue
                self.assertGreater(index, 0, workflow_path.name)
                self.assertEqual(lines[index - 1].strip(), "run: >-", workflow_path.name)
                self.assertFalse(line.lstrip().startswith("run:"), workflow_path.name)

    def test_data_writing_workflows_use_conflict_safe_publisher(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        workflow_paths = sorted(workflows_dir.glob("sync-*.yml")) + [workflows_dir / "audit-recent.yml"]

        for workflow_path in workflow_paths:
            workflow = workflow_path.read_text(encoding="utf-8")
            if "contents: write" not in workflow:
                continue
            self.assertIn(".github/scripts/commit-and-push.sh", workflow, workflow_path.name)
            self.assertNotIn("git add data\n", workflow, workflow_path.name)
            self.assertNotIn("\n          git push\n", workflow, workflow_path.name)

    def test_shared_publisher_gates_generated_data_on_the_source_inventory_floor(self) -> None:
        # Scheduled jobs push to main with GITHUB_TOKEN, and GitHub starts no
        # workflow for such a push, so neither CI nor the Pages deploy ever
        # sees what they wrote. The gate has to run inside the job, and it
        # lives in the shared publisher so a new sync workflow cannot omit it.
        script = (REPO_ROOT / ".github" / "scripts" / "commit-and-push.sh").read_text(encoding="utf-8")

        self.assertIn("scripts/check_sync_floor.py", script)
        self.assertLess(
            script.index("scripts/check_sync_floor.py"),
            script.index('git commit -m "$commit_message"'),
        )

    def test_every_data_writing_workflow_routes_through_the_gated_publisher(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        writers = [
            path
            for path in sorted(workflows_dir.glob("*.yml"))
            if "contents: write" in path.read_text(encoding="utf-8")
        ]

        self.assertTrue(writers)
        for workflow_path in writers:
            workflow = workflow_path.read_text(encoding="utf-8")
            with self.subTest(workflow=workflow_path.name):
                self.assertIn(".github/scripts/commit-and-push.sh", workflow)
                for forbidden in ("git commit -m", "git push origin"):
                    self.assertNotIn(forbidden, workflow)

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
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_tabf_cert_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-tabf-cert.yml").read_text(encoding="utf-8")

        self.assertIn("python -m app sync-full --provider tabf_cert --site-id default", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_tii_cert_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-tii-cert.yml").read_text(encoding="utf-8")

        self.assertIn("python -m app sync-full --provider tii_cert --site-id default", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_financial_cert_workflows_have_schedule(self) -> None:
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        for name in ("sync-sfi-cert.yml", "sync-tabf-cert.yml", "sync-tii-cert.yml"):
            with self.subTest(name=name):
                workflow = (workflows_dir / name).read_text(encoding="utf-8")
                self.assertIn("schedule:", workflow)
                self.assertIn("cron:", workflow)
                self.assertIn("workflow_dispatch:", workflow)


class RequestedTopicWorkflowTests(unittest.TestCase):
    def test_sync_teacher_recruit_tainan_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-teacher-recruit-tainan.yml").read_text(encoding="utf-8")

        self.assertIn('- cron: "25 5 * * 2"', workflow)
        self.assertNotIn('- cron: "35 5 * * 2"', workflow)
        self.assertIn("python -m app sync-full --provider teacher_recruit_tainan --site-id default", workflow)
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_teacher_recruit_taipei_junior_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-teacher-recruit-taipei-junior.yml").read_text(encoding="utf-8")

        self.assertIn("python -m app sync-full --provider teacher_recruit_taipei_junior --site-id default", workflow)
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_teacher_recruit_taipei_elementary_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-teacher-recruit-taipei-elementary.yml").read_text(encoding="utf-8")

        self.assertIn('- cron: "55 5 * * 2"', workflow)
        self.assertIn("python -m app sync-full --provider teacher_recruit_taipei_elementary --site-id default", workflow)
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_newtaipei_teacher_recruit_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-teacher-recruit-newtaipei.yml").read_text(encoding="utf-8")

        self.assertIn('- cron: "5 5 * * 2"', workflow)
        self.assertIn("python -m app sync-full --provider teacher_recruit_newtaipei --site-id default", workflow)
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_taoyuan_teacher_recruit_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-teacher-recruit-taoyuan-elementary.yml").read_text(encoding="utf-8")

        self.assertIn('- cron: "5 6 * * 2"', workflow)
        self.assertIn("python -m app sync-full --provider teacher_recruit_taoyuan_elementary --site-id default", workflow)
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_kaohsiung_teacher_recruit_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-teacher-recruit-kaohsiung.yml").read_text(encoding="utf-8")

        self.assertIn('- cron: "25 6 * * 2"', workflow)
        self.assertIn("python -m app sync-full --provider teacher_recruit_kaohsiung --site-id default", workflow)
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)

    def test_sync_central_alliance_teacher_recruit_workflow_is_provider_only(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sync-teacher-recruit-central-alliance.yml").read_text(encoding="utf-8")

        self.assertIn('- cron: "45 6 * * 2"', workflow)
        self.assertIn("python -m app sync-full --provider teacher_recruit_central_alliance --site-id default", workflow)
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn('python -m app publish-site --site-id default --repository "${{ github.repository }}"', workflow)
        self.assertNotIn("release_assets.py", workflow)


class LaunchCITest(unittest.TestCase):
    def test_ci_workflow_covers_release_and_frontend_gates(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        for required in (
            "pull_request:",
            "python -m pytest -q",
            "tests/test_workflows.py",
            "python -m app audit-catalog",
            "python -m app history-audit",
            "python scripts/validate_publication.py",
            "python -m app plan-release",
            "npm ci",
            "npm test",
            "npm run lint",
            "npm run build",
        ):
            self.assertIn(required, workflow)
        self.assertIn('node-version: "22"', workflow)


if __name__ == "__main__":
    unittest.main()
