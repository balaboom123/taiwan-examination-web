from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable, Mapping
from urllib.request import Request, urlopen

from app.models import BundleAsset

API_ENDPOINT = "https://creators.lootlabs.gg/api/public/content_locker"
MANIFEST_VERSION = 1
PROVIDER_NAME = "lootlabs"


class LootLabsError(RuntimeError):
    pass


@dataclass(frozen=True)
class LootLabsSettings:
    tier_id: int
    number_of_tasks: int
    theme: int = 1


@dataclass(frozen=True)
class LootLabsManifestEntry:
    canonical_id: str
    asset_name: str
    loot_url: str
    target_download_url: str
    target_checksum: str
    updated_at: str


@dataclass(frozen=True)
class LootLabsManifest:
    version: int
    provider: str
    settings: LootLabsSettings
    bundles: dict[str, LootLabsManifestEntry]


def _load_int_setting(source: Mapping[str, str], key: str, default: str) -> int:
    value = source.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise LootLabsError(f"{key} must be an integer") from exc


def load_lootlabs_settings_from_env(env: Mapping[str, str] | None = None) -> tuple[str, LootLabsSettings]:
    source = dict(os.environ if env is None else env)
    api_key = source.get("LOOTLABS_API_KEY", "").strip()
    if not api_key:
        raise LootLabsError("LOOTLABS_API_KEY is required")
    settings = LootLabsSettings(
        tier_id=_load_int_setting(source, "LOOTLABS_TIER_ID", "1"),
        number_of_tasks=_load_int_setting(source, "LOOTLABS_NUMBER_OF_TASKS", "1"),
        theme=_load_int_setting(source, "LOOTLABS_THEME", "1"),
    )
    if settings.tier_id not in (1, 2, 3):
        raise LootLabsError("LOOTLABS_TIER_ID must be 1, 2, or 3")
    if not 1 <= settings.number_of_tasks <= 5:
        raise LootLabsError("LOOTLABS_NUMBER_OF_TASKS must be between 1 and 5")
    if not 1 <= settings.theme <= 5:
        raise LootLabsError("LOOTLABS_THEME must be between 1 and 5")
    return api_key, settings


def load_lootlabs_manifest(path: Path) -> LootLabsManifest | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return LootLabsManifest(
        version=payload["version"],
        provider=payload["provider"],
        settings=LootLabsSettings(**payload["settings"]),
        bundles={
            canonical_id: LootLabsManifestEntry(**entry)
            for canonical_id, entry in payload.get("bundles", {}).items()
        },
    )


def should_refresh_lootlabs_entry(
    bundle: BundleAsset,
    entry: LootLabsManifestEntry | None,
    current_settings: LootLabsSettings,
    stored_settings: LootLabsSettings | None,
) -> bool:
    if entry is None or not entry.loot_url:
        return True
    if stored_settings != current_settings:
        return True
    if entry.target_download_url != bundle.download_url:
        return True
    if entry.target_checksum != bundle.checksum:
        return True
    return False


def _create_lootlabs_entry(
    bundle: BundleAsset,
    api_key: str,
    settings: LootLabsSettings,
    opener: Callable = urlopen,
    now: Callable[[], str] | None = None,
) -> LootLabsManifestEntry:
    payload = json.dumps(
        {
            "title": bundle.canonical_name[:30],
            "url": bundle.download_url,
            "tier_id": settings.tier_id,
            "number_of_tasks": settings.number_of_tasks,
            "theme": settings.theme,
        }
    ).encode("utf-8")
    request = Request(
        API_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with opener(request) as response:
        result = json.loads(response.read().decode("utf-8"))
    message = result.get("message", {})
    loot_url = message.get("loot_url") if isinstance(message, dict) else None
    if result.get("type") not in {"created", "fetch"} or not loot_url:
        raise LootLabsError(f"LootLabs link creation failed: {result}")
    timestamp = now() if now is not None else datetime.now().astimezone().isoformat()
    return LootLabsManifestEntry(
        canonical_id=bundle.canonical_id,
        asset_name=bundle.asset_name,
        loot_url=loot_url,
        target_download_url=bundle.download_url,
        target_checksum=bundle.checksum,
        updated_at=timestamp,
    )


def write_lootlabs_manifest(path: Path, manifest: LootLabsManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": manifest.version,
        "provider": manifest.provider,
        "settings": asdict(manifest.settings),
        "bundles": {canonical_id: asdict(entry) for canonical_id, entry in manifest.bundles.items()},
    }
    with NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def sync_lootlabs_manifest(
    bundles: list[BundleAsset],
    manifest_path: Path,
    api_key: str,
    settings: LootLabsSettings,
    opener: Callable = urlopen,
    now: Callable[[], str] | None = None,
) -> LootLabsManifest:
    existing = load_lootlabs_manifest(manifest_path)
    stored_settings = existing.settings if existing is not None else None
    stored_bundles = {} if existing is None else existing.bundles
    synced: dict[str, LootLabsManifestEntry] = {}
    for bundle in bundles:
        entry = stored_bundles.get(bundle.canonical_id)
        if should_refresh_lootlabs_entry(bundle, entry, settings, stored_settings):
            entry = _create_lootlabs_entry(bundle, api_key, settings, opener=opener, now=now)
        synced[bundle.canonical_id] = entry
    manifest = LootLabsManifest(
        version=MANIFEST_VERSION,
        provider=PROVIDER_NAME,
        settings=settings,
        bundles=synced,
    )
    write_lootlabs_manifest(manifest_path, manifest)
    return manifest
