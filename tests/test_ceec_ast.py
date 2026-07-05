import unittest
from unittest.mock import patch

from app.models import NormalizedCatalog
from app.normalizer import normalize_papers
from app.providers.base import SourceProvider
from app.providers.registry import get_provider

from app.providers.ceec_ast.client import CeecAstClient, parse_listing_page


LISTING_HTML = """
<html><body>
<h2>一般試題</h2>
<div>共 25 頁 / 241 筆</div>
<table>
  <tr><th>發佈日期</th><th>標題</th><th>下載</th></tr>
  <tr>
    <td>114-08-12</td>
    <td>114學年度分科測驗－數學甲</td>
    <td>
      <a href="/files/math-a-question.pdf">試題內容</a>
      <a href="/files/math-a-question-2.pdf">試題內容</a>
      <a href="/files/math-a-sheet.pdf">答題卷</a>
      <a href="/files/math-a-answer.pdf">選擇(填)題答案</a>
      <a href="/files/math-a-guideline.pdf">非選擇題評分原則</a>
    </td>
  </tr>
</table>
</body></html>
"""


class CeecAstParserTests(unittest.TestCase):
    def test_parse_listing_page_extracts_total_pages_and_ast_row(self) -> None:
        page = parse_listing_page(LISTING_HTML)

        self.assertEqual(page.total_pages, 25)
        self.assertEqual(len(page.entries), 1)
        self.assertEqual(page.entries[0].year_ad, 2025)
        self.assertEqual(page.entries[0].source_exam_id, "ceec-ast-114-math-a")
        self.assertEqual(page.entries[0].title, "114學年度分科測驗－數學甲")
        self.assertEqual(
            [item.label for item in page.entries[0].downloads],
            ["試題內容", "試題內容", "答題卷", "選擇(填)題答案", "非選擇題評分原則"],
        )

    def test_fetch_exam_page_turns_one_listing_row_into_many_single_file_papers(self) -> None:
        with patch.object(CeecAstClient, "_fetch_text", return_value=LISTING_HTML):
            client = CeecAstClient()
            page = client.fetch_exam_page("ceec-ast-114-math-a", 2025)

        self.assertEqual(page.provider_id, "ceec_ast")
        self.assertEqual(page.exam_name_raw, "114學年度分科測驗－數學甲")
        self.assertEqual({paper.category_raw for paper in page.papers}, {"分科測驗"})
        self.assertEqual(
            {file_type for paper in page.papers for file_type in paper.files},
            {"question", "question_alt", "answer_sheet", "answer", "corrected_answer"},
        )

    def test_registry_returns_ceec_ast_provider(self) -> None:
        provider = get_provider("ceec_ast")

        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "ceec_ast")

    def test_ceec_ast_normalization_uses_stable_canonical_bundle_identity(self) -> None:
        with patch.object(CeecAstClient, "_fetch_text", return_value=LISTING_HTML):
            client = CeecAstClient()
            page = client.fetch_exam_page("ceec-ast-114-math-a", 2025)

        mirror_metadata = {}
        for paper in page.papers:
            for file_type in paper.files:
                mirror_metadata[(paper.category_code, paper.subject_code, file_type)] = {
                    "checksum": f"{paper.subject_code}-{file_type}",
                    "storage_key": f"providers/ceec_ast/114/{page.source_exam_id}/{paper.category_code}/{paper.subject_code}/{file_type}.pdf",
                }

        normalized = normalize_papers(
            source_exam_id=page.source_exam_id,
            year_ad=page.year_ad,
            exam_name_raw=page.exam_name_raw,
            papers=page.papers,
            alias_rules=[],
            mirror_base_url="",
            mirror_metadata=mirror_metadata,
        )

        self.assertIsInstance(normalized, NormalizedCatalog)
        self.assertEqual({paper.canonical_id for paper in normalized.papers}, {"ceec-ast"})
        self.assertEqual({paper.canonical_name for paper in normalized.papers}, {"分科測驗"})
        self.assertEqual(normalized.review_queue, [])


if __name__ == "__main__":
    unittest.main()
