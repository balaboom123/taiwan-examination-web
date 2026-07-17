import json
import unittest
from pathlib import Path


class CatalogContractTests(unittest.TestCase):
    def test_taxonomy_mappings_and_schemas_are_valid_json(self) -> None:
        root = Path(__file__).resolve().parents[1]
        paths = [
            *sorted((root / "catalog" / "taxonomy").glob("*.json")),
            *sorted((root / "catalog" / "mappings").glob("*.json")),
            *sorted((root / "catalog" / "mappings" / "moex").glob("*.json")),
            *sorted((root / "schemas").glob("*.json")),
        ]
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(payload, dict)

        taxonomy = json.loads((root / "catalog/taxonomy/exam-identity-v2.json").read_text(encoding="utf-8"))
        self.assertEqual(taxonomy["catalog_version"], "exam-identity-v2")
        self.assertEqual(taxonomy["identity_schema_version"], 2)

        bundle_schema = json.loads((root / "schemas/bundle-v2.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(bundle_schema["properties"]["schema_version"]["const"], 2)


if __name__ == "__main__":
    unittest.main()
