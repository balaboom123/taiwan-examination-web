import unittest

from app.providers.base import SourceProvider
from app.providers.registry import get_provider


class FinancialCertRegistryTests(unittest.TestCase):
    def test_sfi_cert_registered(self) -> None:
        provider = get_provider("sfi_cert")
        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "sfi_cert")

    def test_tabf_cert_registered(self) -> None:
        provider = get_provider("tabf_cert")
        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "tabf_cert")

    def test_tii_cert_registered(self) -> None:
        provider = get_provider("tii_cert")
        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "tii_cert")


if __name__ == "__main__":
    unittest.main()
