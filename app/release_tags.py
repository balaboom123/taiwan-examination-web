from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

from app.models import BundleAsset


def _is_active_release_tag(release_tag_prefix: str, release_tag: str) -> bool:
    return release_tag.startswith(f"{release_tag_prefix}-")


def assign_release_tags(
    *,
    release_tag_prefix: str,
    existing_bundles: list[BundleAsset],
    bundles: list[BundleAsset],
    max_assets_per_release: int = 900,
) -> list[BundleAsset]:
    if max_assets_per_release < 1:
        raise ValueError("max_assets_per_release must be at least 1")

    preserved = {
        bundle.asset_name: bundle.release_tag
        for bundle in existing_bundles
        if bundle.release_tag and _is_active_release_tag(release_tag_prefix, bundle.release_tag)
    }
    ordered = sorted(bundles, key=lambda item: item.asset_name)
    counts: dict[str, int] = defaultdict(int)

    for bundle in ordered:
        release_tag = preserved.get(bundle.asset_name)
        if release_tag:
            counts[release_tag] += 1

    def shard_name(index: int) -> str:
        return f"{release_tag_prefix}-{index:03d}"

    next_shard = 1
    assigned: list[BundleAsset] = []
    for bundle in ordered:
        release_tag = preserved.get(bundle.asset_name)
        if not release_tag:
            while counts[shard_name(next_shard)] >= max_assets_per_release:
                next_shard += 1
            release_tag = shard_name(next_shard)
            counts[release_tag] += 1
        assigned.append(replace(bundle, release_tag=release_tag))
    return assigned
