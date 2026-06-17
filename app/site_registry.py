from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SiteConfig:
    site_id: str
    provider_ids: tuple[str, ...]
    release_tag_prefix: str
    release_shard_size: int = 900


_SITES = {
    "default": SiteConfig(
        site_id="default",
        provider_ids=("moex",),
        release_tag_prefix="moex-bundles",
        release_shard_size=900,
    )
}


def get_site_config(site_id: str) -> SiteConfig:
    try:
        return _SITES[site_id]
    except KeyError as exc:
        raise ValueError(f"Unknown site_id: {site_id}") from exc
