import unittest
from pathlib import Path


class WorkflowTests(unittest.TestCase):
    def test_incremental_workflow_bootstraps_with_full_sync_when_release_is_incomplete(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("expected_zip_names", workflow)
        self.assertIn("current_release_zip_names", workflow)
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
        self.assertIn("expected_zip_names", workflow)
        self.assertIn("bootstrap_required", workflow)
        self.assertIn("python -m app sync-full", workflow)
        self.assertIn("python -m app sync-incremental --years 2", workflow)
        self.assertIn("--write-manifest", workflow)
        self.assertIn('asset["name"].endswith(".zip")', workflow)
        self.assertIn('"delete-asset"', workflow)

    def test_incremental_workflow_only_deletes_stale_zip_assets(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn('asset["name"].endswith(".zip")', workflow)

    def test_full_workflow_only_deletes_stale_zip_assets(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-full.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn('asset["name"].endswith(".zip")', workflow)

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
            self.assertIn('gh release create "$MOEX_RELEASE_TAG" --title "MOEX downloadable bundles"', workflow)
            self.assertIn('Human-friendly exam bundles with compatibility aliases', workflow)

    def test_readme_documents_human_friendly_bundle_assets(self) -> None:
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")

        self.assertIn("Bundle filenames use Chinese display names plus canonical IDs.", readme)
        self.assertIn("Release assets can include legacy compatibility alias names during migration.", readme)
        self.assertIn("Bundle asset: `護理師__nurse.zip`", readme)
        self.assertIn("Archive entry: `115/115030_護理師/101_0101_基礎醫學_試題.pdf`", readme)
        self.assertNotIn("optimize-mirror-pdfs", readme)


if __name__ == "__main__":
    unittest.main()
