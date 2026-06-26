import unittest

from app.site_registry import get_site_config


class SiteRegistryTests(unittest.TestCase):
    def test_default_site_config_aggregates_all_providers(self) -> None:
        site = get_site_config("default")
        self.assertEqual(site.site_id, "default")
        self.assertEqual(
            site.provider_ids,
            (
                "moex",
                "ceec_gsat",
                "cpc_recruit",
                "moea_recruit",
                "taipower_recruit",
                "taisugar_recruit",
                "twc_recruit",
                "rcpet_cap",
                "wdasec_skill",
            ),
        )
        self.assertEqual(site.release_tag_prefix, "default-bundles")
        self.assertEqual(site.release_shard_size, 900)
        self.assertEqual(site.public_min_years, 2)
