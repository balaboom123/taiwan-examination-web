import unittest

from app.site_registry import get_site_config


class SiteRegistryTests(unittest.TestCase):
    def test_default_site_config_uses_moex_only_before_ceec_task(self) -> None:
        site = get_site_config("default")
        self.assertEqual(site.site_id, "default")
        self.assertEqual(site.provider_ids, ("moex",))
        self.assertEqual(site.release_tag_prefix, "moex-bundles")
        self.assertEqual(site.release_shard_size, 900)
