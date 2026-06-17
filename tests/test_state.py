import tempfile
import unittest
from pathlib import Path

from app.models import BundleAsset, NormalizedCatalog
from app.paths import provider_paths, site_paths
from app.publisher import write_provider_state, write_site_state
from app.state import load_provider_state, load_site_bundles


class ScopedStateTests(unittest.TestCase):
    def test_provider_state_round_trips_under_scoped_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            provider = provider_paths(root, "moex")
            write_provider_state(
                provider,
                raw_pages=[],
                normalized=NormalizedCatalog(papers=[], review_queue=[]),
                aliases=[],
                failures=[],
                manifest=None,
            )

            raw_pages, catalog, failures = load_provider_state(provider)
            self.assertEqual(raw_pages, [])
            self.assertEqual(catalog.papers, [])
            self.assertEqual(failures, [])

    def test_site_bundles_load_from_wrapped_scoped_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            site = site_paths(root, "default")
            write_site_state(
                site,
                bundles=[
                    BundleAsset(
                        canonical_id="nurse",
                        canonical_name="Nurse",
                        years=[115],
                        file_count=1,
                        storage_key="bundles/sites/default/nurse.zip",
                        asset_name="nurse.zip",
                        release_tag="moex-bundles",
                        download_url="https://example.test/nurse.zip",
                        checksum="sha-1",
                    )
                ],
                frontend_bundles=[{"id": "nurse", "name": "Nurse", "years": [115], "fileCount": 1, "url": "https://example.test/nurse.zip"}],
                lootlabs_manifest=None,
                write_legacy=False,
            )

            bundles = load_site_bundles(site)
            self.assertEqual(bundles[0].release_tag, "moex-bundles")
