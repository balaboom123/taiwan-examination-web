import unittest
from unittest.mock import patch

from app.models import NormalizedCatalog
from app.normalizer import normalize_papers
from app.providers.base import SourceProvider
from app.providers.hce_archive import HCE_CONFIGS, HceArchiveClient, _request_url, parse_article_listing, parse_combined_pdf_listing
from app.providers.registry import get_provider


CMU_LISTING_HTML = """
<html><body>
  <a href="/?q=zh-hant/node/641">115學年度學士後中醫學系入學招生考試試題及參考答案公告</a>
</body></html>
"""

TCU_ARTICLE_HTML = """
<html><body>
  <a href="https://admissions.tcu.edu.tw/wp-content/uploads/2026/04/115國文試題.pdf">115後中醫_國文_試題</a>
  <a href="https://admissions.tcu.edu.tw/wp-content/uploads/2026/04/115國文_參考答案.pdf">115後中醫_國文_參考答案</a>
  <a href="https://admissions.tcu.edu.tw/wp-content/uploads/2026/04/115化學試題.pdf">115後中醫_化學_試題</a>
</body></html>
"""

NTHU_ARTICLE_HTML = """
<html><body>
  <a href="/app/index.php?Action=downloadfile&amp;file=english&amp;fname=x">[下載] 115學士後醫試題【0101英文】.pdf</a>
  <a href="/app/index.php?Action=downloadfile&amp;file=biology&amp;fname=x">[下載] 115學士後醫試題【0102生物與生化】.pdf</a>
  <a href="/app/index.php?Action=downloadfile&amp;file=answers&amp;fname=x">[下載] 115各科試題參考答案(公告).pdf</a>
</body></html>
"""

NSYSU_LISTING_HTML = """
<html><body>
  <a href="https://www3.nsysu.edu.tw/exam/bachelor/med/pbm/pbm_115.pdf">115年</a>
  <a href="https://www3.nsysu.edu.tw/exam/bachelor/med/pbm/pbm_114.pdf">114年</a>
</body></html>
"""


class HceArchiveParserTests(unittest.TestCase):
    def test_parse_article_listing_extracts_official_article_page(self) -> None:
        pages = parse_article_listing(CMU_LISTING_HTML, "https://adm21.cmu.edu.tw/?q=news_spbcm", HCE_CONFIGS["hce_cmu"])

        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].year_ad, 2026)
        self.assertEqual(pages[0].year_roc, 115)
        self.assertEqual(pages[0].url, "https://adm21.cmu.edu.tw/?q=zh-hant/node/641")

    def test_tcu_subject_file_page_extracts_question_and_answer_assets(self) -> None:
        papers = HCE_CONFIGS["hce_tcu"].parse_papers(
            TCU_ARTICLE_HTML,
            "https://admissions.tcu.edu.tw/?p=26534",
        )

        self.assertEqual(len(papers), 2)
        self.assertEqual(papers[0].category_code, "post-bacc-chinese-medicine")
        self.assertEqual(papers[0].subject_code, "chinese")
        self.assertEqual(papers[0].files["question"], "https://admissions.tcu.edu.tw/wp-content/uploads/2026/04/115國文試題.pdf")
        self.assertEqual(papers[0].files["answer"], "https://admissions.tcu.edu.tw/wp-content/uploads/2026/04/115國文_參考答案.pdf")
        self.assertEqual(papers[1].subject_code, "chemistry")
        self.assertEqual(papers[1].files["question"], "https://admissions.tcu.edu.tw/wp-content/uploads/2026/04/115化學試題.pdf")

    def test_nthu_subject_file_page_keeps_all_answers_asset(self) -> None:
        papers = HCE_CONFIGS["hce_nthu"].parse_papers(
            NTHU_ARTICLE_HTML,
            "https://adms.site.nthu.edu.tw/p/406-1207-305076,r6125.php?Lang=zh-tw",
        )

        by_subject = {paper.subject_code: paper for paper in papers}
        self.assertEqual(by_subject["english"].files["question"], "https://adms.site.nthu.edu.tw/app/index.php?Action=downloadfile&file=english&fname=x")
        self.assertEqual(by_subject["biology-biochemistry"].files["question"], "https://adms.site.nthu.edu.tw/app/index.php?Action=downloadfile&file=biology&fname=x")
        self.assertEqual(by_subject["all"].files["all_answers"], "https://adms.site.nthu.edu.tw/app/index.php?Action=downloadfile&file=answers&fname=x")

    def test_parse_combined_pdf_listing_extracts_year_files(self) -> None:
        pages = parse_combined_pdf_listing(NSYSU_LISTING_HTML, "https://lis.nsysu.edu.tw/p/412-1001-23442.php", HCE_CONFIGS["hce_nsysu"])

        self.assertEqual([page.year_roc for page in pages], [115, 114])
        self.assertEqual(pages[0].url, "https://www3.nsysu.edu.tw/exam/bachelor/med/pbm/pbm_115.pdf")

    def test_request_url_quotes_non_ascii_download_paths(self) -> None:
        self.assertEqual(
            _request_url("https://example.edu/files/115國文試題.pdf"),
            "https://example.edu/files/115%E5%9C%8B%E6%96%87%E8%A9%A6%E9%A1%8C.pdf",
        )


class HceArchiveProviderTests(unittest.TestCase):
    def test_cmu_client_fetches_source_page_from_listing(self) -> None:
        def fake_fetch(url: str) -> str:
            if "news_spbcm" in url:
                return CMU_LISTING_HTML
            return TCU_ARTICLE_HTML

        with patch.object(HceArchiveClient, "_fetch_text", side_effect=fake_fetch):
            page = HceArchiveClient(HCE_CONFIGS["hce_cmu"]).fetch_exam_page("hce-cmu-115", 2026)

        self.assertEqual(page.provider_id, "hce_cmu")
        self.assertEqual(page.source_exam_id, "hce-cmu-115")
        self.assertEqual(page.year_roc, 115)

    def test_nsysu_client_uses_combined_pdf_as_one_paper(self) -> None:
        with patch.object(HceArchiveClient, "_fetch_text", return_value=NSYSU_LISTING_HTML):
            page = HceArchiveClient(HCE_CONFIGS["hce_nsysu"]).fetch_exam_page("hce-nsysu-115", 2026)

        self.assertEqual(len(page.papers), 1)
        self.assertEqual(page.papers[0].category_code, "post-bacc-medicine")
        self.assertEqual(page.papers[0].subject_code, "all")
        self.assertEqual(page.papers[0].files["question_answer"], "https://www3.nsysu.edu.tw/exam/bachelor/med/pbm/pbm_115.pdf")

    def test_registry_returns_hce_providers(self) -> None:
        for provider_id in ("hce_cmu", "hce_tcu", "hce_nsysu", "hce_nthu"):
            with self.subTest(provider_id=provider_id):
                provider = get_provider(provider_id)
                self.assertIsInstance(provider, SourceProvider)
                self.assertEqual(provider.provider_id, provider_id)

    def test_hce_normalization_uses_stable_school_bundle_identity(self) -> None:
        with patch.object(HceArchiveClient, "_fetch_text", return_value=NSYSU_LISTING_HTML):
            page = HceArchiveClient(HCE_CONFIGS["hce_nsysu"]).fetch_exam_page("hce-nsysu-115", 2026)

        mirror_metadata = {
            ("post-bacc-medicine", "all", "question_answer"): {
                "checksum": "checksum",
                "storage_key": "providers/hce_nsysu/115/hce-nsysu-115/post-bacc-medicine/all/question_answer.pdf",
            }
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
        self.assertEqual({paper.canonical_id for paper in normalized.papers}, {"hce-nsysu"})
        self.assertEqual({paper.canonical_name for paper in normalized.papers}, {"國立中山大學學士後醫學系"})
        self.assertEqual(normalized.review_queue, [])


if __name__ == "__main__":
    unittest.main()
