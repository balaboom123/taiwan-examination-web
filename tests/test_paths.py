import unittest
from pathlib import Path

from app.paths import legacy_paths, provider_paths, site_paths


class PathLayoutTests(unittest.TestCase):
    def test_provider_paths_resolve_scoped_outputs(self) -> None:
        root = Path("/repo")
        paths = provider_paths(root, "ceec_gsat")

        self.assertEqual(paths.provider_id, "ceec_gsat")
        self.assertEqual(paths.data_dir, root / "data" / "providers" / "ceec_gsat")
        self.assertEqual(paths.exams_dir, root / "data" / "providers" / "ceec_gsat" / "exams")
        self.assertEqual(paths.papers_dir, root / "data" / "providers" / "ceec_gsat" / "papers")
        self.assertEqual(paths.review_queue_path, root / "data" / "providers" / "ceec_gsat" / "review-queue.json")
        self.assertEqual(paths.source_manifest_path, root / "data" / "providers" / "ceec_gsat" / "source-manifest.json")
        self.assertEqual(paths.mirror_dir, root / "mirror" / "providers" / "ceec_gsat")

    def test_site_paths_resolve_scoped_publication_outputs(self) -> None:
        root = Path("/repo")
        paths = site_paths(root, "default")

        self.assertEqual(paths.site_id, "default")
        self.assertEqual(paths.data_dir, root / "data" / "sites" / "default")
        self.assertEqual(paths.bundles_path, root / "data" / "sites" / "default" / "bundles.json")
        self.assertEqual(paths.release_assets_path, root / "data" / "sites" / "default" / "release-assets.json")
        self.assertEqual(paths.lootlabs_manifest_path, root / "data" / "sites" / "default" / "lootlabs-links.json")
        self.assertEqual(paths.bundle_dir, root / "bundles" / "sites" / "default")

    def test_legacy_paths_keep_current_root_layout(self) -> None:
        root = Path("/repo")
        paths = legacy_paths(root)

        self.assertEqual(paths.data_dir, root / "data")
        self.assertEqual(paths.bundles_path, root / "data" / "bundles.json")
        self.assertEqual(paths.bundle_dir, root / "bundles")
