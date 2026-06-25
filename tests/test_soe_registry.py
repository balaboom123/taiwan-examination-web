import unittest

from app.providers.base import SourceProvider
from app.providers.registry import get_provider
from app.normalizer import _derive_canonical


class SoeRegistryTests(unittest.TestCase):
    def test_all_soe_providers_registered(self) -> None:
        provider_ids = [
            "moea_recruit",
            "taipower_recruit",
            "cpc_recruit",
            "twc_recruit",
            "taisugar_recruit",
        ]
        for provider_id in provider_ids:
            with self.subTest(provider_id=provider_id):
                provider = get_provider(provider_id)
                self.assertIsInstance(provider, SourceProvider)
                self.assertEqual(provider.provider_id, provider_id)


class SoeNormalizerCanonicalTests(unittest.TestCase):
    def _derive(self, source_exam_id: str) -> tuple[str, str, str, bool]:
        return _derive_canonical(source_exam_id, "", "", 2024, [])

    def test_moea_recruit_canonical(self) -> None:
        canonical_id, canonical_name, _, needs_review = self._derive("moea-recruit-2024")
        self.assertEqual(canonical_id, "moea-recruit")
        self.assertEqual(canonical_name, "國營事業聯招（新進職員）")
        self.assertFalse(needs_review)

    def test_taipower_recruit_canonical(self) -> None:
        canonical_id, canonical_name, _, needs_review = self._derive("taipower-recruit-2024")
        self.assertEqual(canonical_id, "taipower-recruit")
        self.assertEqual(canonical_name, "台電新進僱用人員甄試")
        self.assertFalse(needs_review)

    def test_cpc_recruit_canonical(self) -> None:
        canonical_id, canonical_name, _, needs_review = self._derive("cpc-recruit-2024")
        self.assertEqual(canonical_id, "cpc-recruit")
        self.assertEqual(canonical_name, "中油新進人員甄試")
        self.assertFalse(needs_review)

    def test_twc_recruit_canonical(self) -> None:
        canonical_id, canonical_name, _, needs_review = self._derive("twc-recruit-2024")
        self.assertEqual(canonical_id, "twc-recruit")
        self.assertEqual(canonical_name, "台水評價職位人員甄試")
        self.assertFalse(needs_review)

    def test_taisugar_recruit_canonical(self) -> None:
        canonical_id, canonical_name, _, needs_review = self._derive("taisugar-recruit-2024")
        self.assertEqual(canonical_id, "taisugar-recruit")
        self.assertEqual(canonical_name, "台糖新進工員甄試")
        self.assertFalse(needs_review)


if __name__ == "__main__":
    unittest.main()
