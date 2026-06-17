import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app.lootlabs import (
    LootLabsError,
    LootLabsManifest,
    LootLabsManifestEntry,
    LootLabsSettings,
    load_lootlabs_settings_from_env,
    should_refresh_lootlabs_entry,
    sync_lootlabs_manifest,
    write_lootlabs_manifest,
)
from app.models import BundleAsset


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class _FakeBytesResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def _bundle(
    *,
    canonical_id: str = "nurse",
    asset_name: str = "nurse.zip",
    release_tag: str = "",
    download_url: str = "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
    checksum: str = "sha-1",
) -> BundleAsset:
    return BundleAsset(
        canonical_id=canonical_id,
        canonical_name=canonical_id.title(),
        years=[115],
        file_count=1,
        storage_key=f"bundles/{asset_name}",
        asset_name=asset_name,
        release_tag=release_tag,
        download_url=download_url,
        checksum=checksum,
    )


class LootLabsTests(unittest.TestCase):
    def test_load_lootlabs_settings_from_env_raises_for_non_numeric_values(self) -> None:
        for field_name in ("LOOTLABS_TIER_ID", "LOOTLABS_NUMBER_OF_TASKS", "LOOTLABS_THEME"):
            env = {
                "LOOTLABS_API_KEY": "token",
                "LOOTLABS_TIER_ID": "1",
                "LOOTLABS_NUMBER_OF_TASKS": "1",
                "LOOTLABS_THEME": "1",
                field_name: "abc",
            }

            with self.subTest(field_name=field_name):
                with self.assertRaises(LootLabsError):
                    load_lootlabs_settings_from_env(env)

    def test_should_refresh_lootlabs_entry_for_target_checksum_and_settings_changes(self) -> None:
        bundle = _bundle()
        entry = LootLabsManifestEntry(
            canonical_id="nurse",
            asset_name="nurse.zip",
            loot_url="https://loot-link.com/s?ok",
            target_download_url=bundle.download_url,
            target_checksum=bundle.checksum,
            updated_at="2026-06-15T00:00:00+08:00",
        )
        settings = LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1)

        self.assertFalse(should_refresh_lootlabs_entry(bundle, entry, settings, settings))
        self.assertTrue(should_refresh_lootlabs_entry(_bundle(checksum="sha-2"), entry, settings, settings))
        self.assertTrue(
            should_refresh_lootlabs_entry(
                _bundle(download_url="https://example.com/other.zip"),
                entry,
                settings,
                settings,
            )
        )
        self.assertTrue(
            should_refresh_lootlabs_entry(
                bundle,
                entry,
                settings,
                LootLabsSettings(tier_id=2, number_of_tasks=1, theme=1),
            )
        )

    def test_should_refresh_lootlabs_entry_uses_bundle_release_tag_resolved_url(self) -> None:
        bundle = _bundle(
            canonical_id="nurse",
            asset_name="nurse.zip",
            release_tag="default-bundles-001",
            download_url="https://github.com/example/repo/releases/download/default-bundles-001/nurse.zip",
        )
        entry = LootLabsManifestEntry(
            canonical_id="nurse",
            asset_name="nurse.zip",
            loot_url="https://loot-link.test/nurse",
            target_download_url="https://github.com/example/repo/releases/download/default-bundles-001/nurse.zip",
            target_checksum=bundle.checksum,
            updated_at="2026-06-17T09:00:00+08:00",
        )
        settings = LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1)

        self.assertFalse(should_refresh_lootlabs_entry(bundle, entry, settings, settings))

    def test_sync_lootlabs_manifest_reuses_existing_link_without_http(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "lootlabs-links.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "provider": "lootlabs",
                        "settings": {"tier_id": 1, "number_of_tasks": 1, "theme": 1},
                        "bundles": {
                            "nurse": {
                                "canonical_id": "nurse",
                                "asset_name": "nurse.zip",
                                "loot_url": "https://loot-link.com/s?cached",
                                "target_download_url": "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
                                "target_checksum": "sha-1",
                                "updated_at": "2026-06-15T00:00:00+08:00",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            opener = mock.Mock()

            manifest = sync_lootlabs_manifest(
                bundles=[_bundle()],
                manifest_path=manifest_path,
                api_key="token",
                settings=LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1),
                opener=opener,
                now=lambda: "2026-06-15T08:00:00+08:00",
            )

        self.assertEqual(manifest.bundles["nurse"].loot_url, "https://loot-link.com/s?cached")
        opener.assert_not_called()

    def test_sync_lootlabs_manifest_accepts_list_message_from_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "lootlabs-links.json"
            manifest = sync_lootlabs_manifest(
                bundles=[_bundle()],
                manifest_path=manifest_path,
                api_key="token",
                settings=LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1),
                opener=mock.Mock(
                    return_value=_FakeResponse(
                        {
                            "type": "created",
                            "message": [
                                {
                                    "short": "kYKMxBrz",
                                    "loot_url": "https://lootdest.org/s?kYKMxBrz",
                                    "destination_url": "https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
                                }
                            ],
                        }
                    )
                ),
                now=lambda: "2026-06-15T08:00:00+08:00",
            )

        self.assertEqual(manifest.bundles["nurse"].loot_url, "https://lootdest.org/s?kYKMxBrz")

    def test_sync_lootlabs_manifest_raises_when_provider_response_has_no_loot_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "lootlabs-links.json"
            with self.assertRaises(LootLabsError):
                sync_lootlabs_manifest(
                    bundles=[_bundle()],
                    manifest_path=manifest_path,
                    api_key="token",
                    settings=LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1),
                    opener=mock.Mock(
                        return_value=_FakeResponse({"type": "error", "message": "Internal Server Error"})
                    ),
                    now=lambda: "2026-06-15T08:00:00+08:00",
                )

    def test_sync_lootlabs_manifest_raises_when_provider_request_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "lootlabs-links.json"
            with self.assertRaises(LootLabsError):
                sync_lootlabs_manifest(
                    bundles=[_bundle()],
                    manifest_path=manifest_path,
                    api_key="token",
                    settings=LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1),
                    opener=mock.Mock(side_effect=OSError("network down")),
                    now=lambda: "2026-06-15T08:00:00+08:00",
                )

    def test_sync_lootlabs_manifest_raises_when_provider_response_is_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "lootlabs-links.json"
            with self.assertRaises(LootLabsError):
                sync_lootlabs_manifest(
                    bundles=[_bundle()],
                    manifest_path=manifest_path,
                    api_key="token",
                    settings=LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1),
                    opener=mock.Mock(return_value=_FakeBytesResponse(b"{not-json")),
                    now=lambda: "2026-06-15T08:00:00+08:00",
                )

    def test_sync_lootlabs_manifest_raises_for_manifest_provider_or_version_mismatch(self) -> None:
        test_cases = [
            {"provider": "other-provider", "version": 1},
            {"provider": "lootlabs", "version": 999},
        ]

        for payload_override in test_cases:
            with self.subTest(payload_override=payload_override):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    manifest_path = Path(tmp_dir) / "lootlabs-links.json"
                    manifest_path.write_text(
                        json.dumps(
                            {
                                "version": payload_override["version"],
                                "provider": payload_override["provider"],
                                "settings": {"tier_id": 1, "number_of_tasks": 1, "theme": 1},
                                "bundles": {},
                            }
                        ),
                        encoding="utf-8",
                    )
                    opener = mock.Mock()

                    with self.assertRaises(LootLabsError):
                        sync_lootlabs_manifest(
                            bundles=[_bundle()],
                            manifest_path=manifest_path,
                            api_key="token",
                            settings=LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1),
                            opener=opener,
                            now=lambda: "2026-06-15T08:00:00+08:00",
                        )

                opener.assert_not_called()

    def test_write_lootlabs_manifest_removes_temp_file_when_dump_fails(self) -> None:
        manifest = LootLabsManifest(
            version=1,
            provider="lootlabs",
            settings=LootLabsSettings(tier_id=1, number_of_tasks=1, theme=1),
            bundles={
                "nurse": LootLabsManifestEntry(
                    canonical_id="nurse",
                    asset_name="nurse.zip",
                    loot_url="https://loot-link.com/s?cached",
                    target_download_url="https://github.com/example/repo/releases/download/moex-bundles/nurse.zip",
                    target_checksum="sha-1",
                    updated_at="2026-06-15T08:00:00+08:00",
                )
            },
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "lootlabs-links.json"
            with mock.patch("app.lootlabs.json.dump", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    write_lootlabs_manifest(manifest_path, manifest)

            self.assertEqual(list(Path(tmp_dir).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
