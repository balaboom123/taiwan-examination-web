from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SiteConfig:
    site_id: str
    provider_ids: tuple[str, ...]
    release_tag_prefix: str
    release_shard_size: int = 900
    public_min_years: int = 1
    public_min_years_by_canonical_prefix: dict[str, int] | None = None
    required_provider_ids: tuple[str, ...] = ()


_SITES = {
    "default": SiteConfig(
        site_id="default",
        provider_ids=(
            "moex",
            "ceec_gsat",
            "cpc_recruit",
            "moea_recruit",
            "taipower_recruit",
            "taisugar_recruit",
            "twc_recruit",
            "rcpet_cap",
            "wdasec_skill",
            "sfi_cert",
            "tabf_cert",
            "tii_cert",
        ),
        release_tag_prefix="default-bundles",
        release_shard_size=900,
        public_min_years=2,
        public_min_years_by_canonical_prefix={"sfi-": 1, "tabf-": 1, "tii-": 1},
        required_provider_ids=("moex", "ceec_gsat"),
    )
}


def get_site_config(site_id: str) -> SiteConfig:
    try:
        return _SITES[site_id]
    except KeyError as exc:
        raise ValueError(f"Unknown site_id: {site_id}") from exc
