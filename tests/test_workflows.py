import unittest
from pathlib import Path


class WorkflowTests(unittest.TestCase):
    def test_incremental_workflow_does_not_ignore_bundle_download_failures(self) -> None:
        workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "sync-incremental.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn('gh release download "$MOEX_RELEASE_TAG" --pattern "*.zip" --dir bundles', workflow)
        self.assertNotIn('gh release download "$MOEX_RELEASE_TAG" --pattern "*.zip" --dir bundles || true', workflow)


if __name__ == "__main__":
    unittest.main()
