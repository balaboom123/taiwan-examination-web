import tempfile
import unittest
from pathlib import Path

from app.storage import MirrorStore


class MirrorStoreTests(unittest.TestCase):
    def test_write_bytes_is_idempotent_for_existing_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = MirrorStore(Path(tmp_dir))
            first = store.write_bytes("115/115030/101/0101/question.pdf", b"%PDF-1.7 demo")
            second = store.write_bytes("115/115030/101/0101/question.pdf", b"%PDF-1.7 demo")

            self.assertEqual(first.checksum, second.checksum)
            self.assertFalse(second.created)
            self.assertTrue((Path(tmp_dir) / "115" / "115030" / "101" / "0101" / "question.pdf").exists())

    def test_write_bytes_can_overwrite_existing_content_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "115" / "115030" / "101" / "0101" / "question.pdf"
            store = MirrorStore(Path(tmp_dir))
            store.write_bytes("115/115030/101/0101/question.pdf", b"%PDF-1.7 original")

            updated = store.write_bytes("115/115030/101/0101/question.pdf", b"%PDF-1.7 optimized", overwrite=True)

            self.assertFalse(updated.created)
            self.assertEqual(file_path.read_bytes(), b"%PDF-1.7 optimized")

    def test_find_existing_prefers_pdf_over_legacy_ashx_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            question_dir = root / "115" / "115030" / "101" / "0101"
            question_dir.mkdir(parents=True, exist_ok=True)
            (question_dir / "question.ashx").write_bytes(b"\xef\xbb\xbf<!DOCTYPE html>")
            (question_dir / "question.pdf").write_bytes(b"%PDF-1.7 valid")
            store = MirrorStore(root)

            stored = store.find_existing("115/115030/101/0101/question")

            self.assertIsNotNone(stored)
            self.assertEqual(stored.storage_key, "115/115030/101/0101/question.pdf")

    def test_delete_matching_except_prunes_legacy_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            question_dir = root / "115" / "115030" / "101" / "0101"
            question_dir.mkdir(parents=True, exist_ok=True)
            (question_dir / "question.ashx").write_bytes(b"\xef\xbb\xbf<!DOCTYPE html>")
            (question_dir / "question.pdf").write_bytes(b"%PDF-1.7 valid")
            store = MirrorStore(root)

            store.delete_matching_except("115/115030/101/0101/question", "115/115030/101/0101/question.pdf")

            self.assertFalse((question_dir / "question.ashx").exists())
            self.assertTrue((question_dir / "question.pdf").exists())


if __name__ == "__main__":
    unittest.main()
