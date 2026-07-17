import unittest

from app.models import BundleAsset, NormalizedCatalog, NormalizedPaper
from app.publisher import apply_bundle_download_urls
from app.release_tags import assign_release_tags


def _bundle(name: str, *, canonical_id: str | None = None) -> BundleAsset:
    bundle_id = canonical_id or name[:-4]
    return BundleAsset(
        canonical_id=bundle_id,
        canonical_name=bundle_id.title(),
        years=[115],
        file_count=1,
        storage_key=f"bundles/sites/default/{name}",
        asset_name=name,
        checksum=f"sha-{name}",
    )


def _paper(canonical_id: str) -> NormalizedPaper:
    return NormalizedPaper(
        canonical_id=canonical_id,
        canonical_name=canonical_id.title(),
        year_roc=115,
        exam_name_raw=f"{canonical_id} exam",
        category_raw="category",
        subject_name_raw="subject",
        paper_code=f"{canonical_id}-question",
        file_type="question",
        download_url_source=f"https://source.example/{canonical_id}.pdf",
        category_code="101",
        source_exam_id=f"{canonical_id}-115",
        subject_code="0101",
        download_url_mirror="",
        download_url_bundle="",
        storage_key=f"providers/default/115/{canonical_id}.pdf",
        checksum=f"paper-{canonical_id}",
    )


class ReleaseTagAssignmentTests(unittest.TestCase):
    def test_assign_release_tags_preserves_existing_tags(self) -> None:
        existing = [_bundle("a.zip")]
        existing[0].release_tag = "default-bundles-001"

        updated = assign_release_tags(
            release_tag_prefix="default-bundles",
            existing_bundles=existing,
            bundles=[_bundle("a.zip"), _bundle("b.zip")],
            max_assets_per_release=2,
        )

        self.assertEqual(updated[0].release_tag, "default-bundles-001")
        self.assertEqual(updated[1].release_tag, "default-bundles-001")

    def test_assign_release_tags_ignores_existing_tags_with_different_prefix(self) -> None:
        existing = [_bundle("a.zip")]
        existing[0].release_tag = "moex-bundles"

        updated = assign_release_tags(
            release_tag_prefix="default-bundles",
            existing_bundles=existing,
            bundles=[_bundle("a.zip")],
            max_assets_per_release=2,
        )

        self.assertEqual(updated[0].release_tag, "default-bundles-001")

    def test_assign_release_tags_opens_new_shard_after_capacity(self) -> None:
        bundles = [_bundle("a.zip"), _bundle("b.zip"), _bundle("c.zip")]
        updated = assign_release_tags(
            release_tag_prefix="default-bundles",
            existing_bundles=[],
            bundles=bundles,
            max_assets_per_release=2,
        )

        self.assertEqual(
            [bundle.release_tag for bundle in updated],
            ["default-bundles-001", "default-bundles-001", "default-bundles-002"],
        )

    def test_apply_bundle_download_urls_returns_updated_catalog_bundles_and_frontend_feed(self) -> None:
        bundles = assign_release_tags(
            release_tag_prefix="default-bundles",
            existing_bundles=[],
            bundles=[_bundle("nurse.zip"), _bundle("social worker.zip", canonical_id="social-worker")],
            max_assets_per_release=10,
        )
        normalized = NormalizedCatalog(
            papers=[_paper("nurse"), _paper("social-worker"), _paper("orphan")],
            review_queue=[],
        )

        updated_catalog, updated_bundles, frontend_bundles = apply_bundle_download_urls(
            normalized,
            bundles,
            repository="example/repo",
        )

        self.assertEqual([bundle.download_url for bundle in bundles], ["", ""])
        self.assertEqual(
            [bundle.download_url for bundle in updated_bundles],
            [
                "https://github.com/example/repo/releases/download/default-bundles-001/nurse.zip",
                "https://github.com/example/repo/releases/download/default-bundles-001/social%20worker.zip",
            ],
        )
        self.assertEqual(
            [paper.download_url_bundle for paper in updated_catalog.papers],
            [
                "https://github.com/example/repo/releases/download/default-bundles-001/nurse.zip",
                "https://github.com/example/repo/releases/download/default-bundles-001/social%20worker.zip",
                "",
            ],
        )
        self.assertEqual([paper.download_url_bundle for paper in normalized.papers], ["", "", ""])
        self.assertEqual(
            frontend_bundles,
            [
                {
                    "id": "nurse",
                    "name": "Nurse",
                    "years": [115],
                    "fileCount": 1,
                    "url": "https://github.com/example/repo/releases/download/default-bundles-001/nurse.zip",
                },
                {
                    "id": "social-worker",
                    "name": "Social-Worker",
                    "years": [115],
                    "fileCount": 1,
                    "url": "https://github.com/example/repo/releases/download/default-bundles-001/social%20worker.zip",
                },
            ],
        )

    def test_assign_release_tags_counts_compatibility_aliases_as_physical_assets(self) -> None:
        first = _bundle("a.zip")
        first.legacy_asset_names = ["a-legacy.zip"]
        second = _bundle("b.zip")
        updated = assign_release_tags(
            release_tag_prefix="default-bundles",
            existing_bundles=[],
            bundles=[first, second],
            max_assets_per_release=2,
        )

        self.assertEqual([bundle.release_tag for bundle in updated], ["default-bundles-001", "default-bundles-002"])

    def test_release_capacity_rejects_more_than_hard_limit(self) -> None:
        from app.release_tags import validate_release_capacity

        bundle = _bundle("primary.zip")
        bundle.release_tag = "default-bundles-001"
        bundle.legacy_asset_names = [f"alias-{index}.zip" for index in range(1000)]

        with self.assertRaisesRegex(ValueError, "release asset cap exceeded"):
            validate_release_capacity([bundle])

    def test_assign_release_tags_rejects_one_bundle_over_shard_target(self) -> None:
        oversized = _bundle("oversized.zip")
        oversized.legacy_asset_names = ["alias-1.zip", "alias-2.zip"]

        with self.assertRaisesRegex(ValueError, "exceeding shard target"):
            assign_release_tags(
                release_tag_prefix="default-bundles",
                existing_bundles=[],
                bundles=[oversized],
                max_assets_per_release=2,
            )

    def test_strip_ambiguous_legacy_assets_removes_aliases_from_new_projection(self) -> None:
        from app.release_tags import strip_ambiguous_legacy_assets

        first = _bundle("first.zip", canonical_id="first")
        first.legacy_asset_names = ["shared.zip"]
        second = _bundle("second.zip", canonical_id="second")
        second.legacy_asset_names = ["shared.zip"]

        cleaned, conflicts = strip_ambiguous_legacy_assets([first, second])

        self.assertEqual(conflicts[0]["asset_name"], "shared.zip")
        self.assertEqual(conflicts[0]["bundle_ids"], ["first", "second"])
        self.assertEqual(cleaned[0].legacy_asset_names, [])
        self.assertEqual(cleaned[1].legacy_asset_names, [])


if __name__ == "__main__":
    unittest.main()
