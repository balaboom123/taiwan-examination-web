"""Tests for the taisugar_recruit provider.

Taiwan Sugar Corporation (台糖公司) publishes recruitment exam papers on:
  https://www.taisugar.com.tw/chinese/News_Index.aspx?p=3&n=10080

Two-phase scraping:
  1. Parse the news listing page to find items with title containing "甄試試題".
  2. Fetch each matching detail page to extract ZIP download links.

The listing uses a <div class="wucNews_index"> container with <li> items:
  <li>
    <a href="News_detail.aspx?p=3&n=10080&s=[ID]" title="[Title]">
      <img ...>
      <h3>[Title]</h3>
      <span class="date">[Date]</span>
      [Summary]
    </a>
  </li>

Detail pages contain ZIP download links under a "相關檔案：" heading:
  <p>相關檔案：</p>
  <p>
    <a href="../upload/UserFiles/News/[ID]/[filename].zip" title="...">
      [label](.ZIP)
      <img src="../images/icon_zip.png">
    </a>
  </p>

Each year may have two ZIP files (新進工員 + 產學合作 tracks).
"""
import unittest
from unittest.mock import MagicMock, patch

from app.providers.taisugar_recruit.client import (
    TaisugarRecruitClient,
    TaisugarDownload,
    TaisugarNewsItem,
    parse_news_detail,
    parse_news_listing,
)


# ---------------------------------------------------------------------------
# HTML fixtures — listing page
# ---------------------------------------------------------------------------

# Representative subset of the real News_Index page structure.
# The container is <div class="wucNews_index"> with <ul><li> news items.
# We include one exam-paper entry (甄試試題) and two non-exam entries to test
# that filtering works correctly.
LISTING_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>台糖招募資訊</title></head>
<body>
<div class="wucNews_index">
  <ul>
    <li>
      <a href="News_detail.aspx?p=3&n=10080&s=14933" title="115年新進工員暨產學合作班甄試錄取名單及分發單位志願選填表公告">
        <img src="../images/page/taisugar.png" alt="">
        <h3>115年新進工員暨產學合作班甄試錄取名單及分發單位志願選填表公告</h3>
        <span class="date">2026-06-24</span>
        公告錄取名單...
      </a>
    </li>
    <li>
      <a href="News_detail.aspx?p=3&n=10080&s=14062" title="114年新進工員(含產學合作)甄試試題">
        <img src="../images/page/taisugar.png" alt="">
        <h3>114年新進工員(含產學合作)甄試試題</h3>
        <span class="date">2025-07-25</span>
        114年新進工員(含產學合作)甄試試題，請參閱相關檔案附件。
      </a>
    </li>
    <li>
      <a href="News_detail.aspx?p=3&n=10080&s=13899" title="114年新進工員甄試簡章公告">
        <img src="../images/page/taisugar.png" alt="">
        <h3>114年新進工員甄試簡章公告</h3>
        <span class="date">2025-03-10</span>
        簡章公告...
      </a>
    </li>
    <li>
      <a href="News_detail.aspx?p=3&n=10080&s=11543" title="111年新進工員(含產學)甄試試題">
        <img src="../images/page/taisugar.png" alt="">
        <h3>111年新進工員(含產學)甄試試題</h3>
        <span class="date">2023-02-06</span>
        111年新進工員(含產學)甄試試題，請參閱相關檔案附件。
      </a>
    </li>
  </ul>
</div>
</body>
</html>
"""

# Page with no exam-paper items — should return empty list after filtering
LISTING_PAGE_NO_EXAM_HTML = """
<!DOCTYPE html>
<html>
<body>
<div class="wucNews_index">
  <ul>
    <li>
      <a href="News_detail.aspx?p=3&n=10080&s=14933" title="115年甄試錄取名單公告">
        <h3>115年甄試錄取名單公告</h3>
        <span class="date">2026-06-24</span>
      </a>
    </li>
    <li>
      <a href="News_detail.aspx?p=3&n=10080&s=13899" title="114年新進工員甄試簡章公告">
        <h3>114年新進工員甄試簡章公告</h3>
        <span class="date">2025-03-10</span>
      </a>
    </li>
  </ul>
</div>
</body>
</html>
"""

# Empty listing — no items at all
LISTING_PAGE_EMPTY_HTML = """
<!DOCTYPE html>
<html>
<body>
<div class="wucNews_index">
  <ul></ul>
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# HTML fixtures — detail page
# ---------------------------------------------------------------------------

# Represents s=11543: 111年 page with two ZIP files (新進工員 + 產學合作).
DETAIL_PAGE_TWO_ZIPS_HTML = """
<!DOCTYPE html>
<html>
<head><title>111年新進工員(含產學)甄試試題</title></head>
<body>
<div id="wrapper">
  <div class="content-area">
    <h2>111年新進工員(含產學)甄試試題</h2>
    <p>111年新進工員(含產學)甄試試題，請參閱相關檔案附件。</p>
    <p>相關檔案：</p>
    <p>
      <a href="../upload/UserFiles/News/11543/638382326576030861.zip"
         title="(另存目標下載檔案)(12Mb)">
        111年度新進工員甄試試題及解答(12Mb)(.ZIP)
        <img src="../images/icon_zip.png" alt="">
      </a>
    </p>
    <p>
      <a href="../upload/UserFiles/News/11543/638382326767185760.zip"
         title="(另存目標下載檔案)(7Mb)">
        111年度產學合作甄試試題及解答(7Mb)(.ZIP)
        <img src="../images/icon_zip.png" alt="">
      </a>
    </p>
  </div>
</div>
</body>
</html>
"""

# Represents s=14062: 114年 page with a single combined ZIP file.
DETAIL_PAGE_ONE_ZIP_HTML = """
<!DOCTYPE html>
<html>
<head><title>114年新進工員(含產學合作)甄試試題</title></head>
<body>
<div id="wrapper">
  <div class="content-area">
    <h2>114年新進工員(含產學合作)甄試試題</h2>
    <p>114年新進工員(含產學合作)甄試試題，請參閱相關檔案附件。</p>
    <p>相關檔案：</p>
    <p>
      <a href="../upload/UserFiles/News/14062/638889473019415029.zip"
         title="(另存目標下載檔案)(6Mb)">
        試題及解答(6Mb)(.ZIP)
        <img src="../images/icon_zip.png" alt="">
      </a>
    </p>
  </div>
</div>
</body>
</html>
"""

# Detail page with no ZIP downloads — should return empty list
DETAIL_PAGE_NO_ZIP_HTML = """
<!DOCTYPE html>
<html>
<body>
<div class="content-area">
  <h2>報名表下載</h2>
  <p>相關檔案：</p>
  <p>
    <a href="../upload/UserFiles/News/12345/form.pdf">報名表.pdf</a>
  </p>
</div>
</body>
</html>
"""

# Non-.zip link mixed with ZIP links — only ZIP should be extracted
DETAIL_PAGE_MIXED_HTML = """
<!DOCTYPE html>
<html>
<body>
<div class="content-area">
  <p>相關檔案：</p>
  <p>
    <a href="../upload/UserFiles/News/11543/638382326576030861.zip"
       title="(另存目標下載檔案)(12Mb)">
      111年度新進工員甄試試題及解答(12Mb)(.ZIP)
      <img src="../images/icon_zip.png" alt="">
    </a>
  </p>
  <p>
    <a href="../upload/UserFiles/News/11543/notice.pdf">公告通知.pdf</a>
  </p>
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Listing parser tests
# ---------------------------------------------------------------------------

class TaisugarNewsListingParserTests(unittest.TestCase):

    def test_parse_listing_extracts_exam_items_only(self) -> None:
        """Only items with '甄試試題' in title should be returned."""
        items = parse_news_listing(LISTING_PAGE_HTML)

        # Two exam-paper items in the fixture: s=14062 and s=11543
        self.assertEqual(len(items), 2)

    def test_parse_listing_extracts_title(self) -> None:
        items = parse_news_listing(LISTING_PAGE_HTML)

        titles = [item.title for item in items]
        self.assertIn("114年新進工員(含產學合作)甄試試題", titles)
        self.assertIn("111年新進工員(含產學)甄試試題", titles)

    def test_parse_listing_extracts_detail_url(self) -> None:
        items = parse_news_listing(LISTING_PAGE_HTML)

        item_114 = next(i for i in items if "114" in i.title)
        self.assertIn("News_detail.aspx", item_114.detail_url)
        self.assertIn("s=14062", item_114.detail_url)

    def test_parse_listing_detail_url_is_absolute(self) -> None:
        items = parse_news_listing(LISTING_PAGE_HTML)

        for item in items:
            self.assertTrue(
                item.detail_url.startswith("https://"),
                f"Expected absolute URL, got: {item.detail_url}",
            )

    def test_parse_listing_extracts_year_roc(self) -> None:
        items = parse_news_listing(LISTING_PAGE_HTML)

        years = {item.year_roc for item in items}
        self.assertIn(114, years)
        self.assertIn(111, years)

    def test_parse_listing_filters_non_exam_items(self) -> None:
        """Non-exam-paper news items (no '甄試試題') should be excluded."""
        items = parse_news_listing(LISTING_PAGE_HTML)

        for item in items:
            self.assertIn("甄試試題", item.title)

    def test_parse_listing_no_exam_items_returns_empty(self) -> None:
        items = parse_news_listing(LISTING_PAGE_NO_EXAM_HTML)

        self.assertEqual(items, [])

    def test_parse_listing_empty_page_returns_empty(self) -> None:
        items = parse_news_listing(LISTING_PAGE_EMPTY_HTML)

        self.assertEqual(items, [])

    def test_parse_listing_plain_html_returns_empty(self) -> None:
        items = parse_news_listing("<html><body></body></html>")

        self.assertEqual(items, [])


# ---------------------------------------------------------------------------
# Detail page parser tests
# ---------------------------------------------------------------------------

class TaisugarNewsDetailParserTests(unittest.TestCase):

    def test_parse_detail_two_zips(self) -> None:
        """Detail page with two ZIP files should yield two downloads."""
        downloads = parse_news_detail(DETAIL_PAGE_TWO_ZIPS_HTML)

        self.assertEqual(len(downloads), 2)

    def test_parse_detail_extracts_zip_urls(self) -> None:
        downloads = parse_news_detail(DETAIL_PAGE_TWO_ZIPS_HTML)

        urls = [d.url for d in downloads]
        self.assertTrue(all(u.endswith(".zip") for u in urls))
        self.assertTrue(all("taisugar.com.tw" in u for u in urls))

    def test_parse_detail_url_contains_news_id(self) -> None:
        downloads = parse_news_detail(DETAIL_PAGE_TWO_ZIPS_HTML)

        for d in downloads:
            self.assertIn("/News/11543/", d.url)

    def test_parse_detail_extracts_label(self) -> None:
        downloads = parse_news_detail(DETAIL_PAGE_TWO_ZIPS_HTML)

        labels = [d.label for d in downloads]
        # Both labels should be non-empty
        self.assertTrue(all(label.strip() for label in labels))

    def test_parse_detail_label_identifies_tracks(self) -> None:
        """Labels should distinguish the two exam tracks."""
        downloads = parse_news_detail(DETAIL_PAGE_TWO_ZIPS_HTML)

        labels_combined = " ".join(d.label for d in downloads)
        self.assertIn("新進工員", labels_combined)
        self.assertIn("產學合作", labels_combined)

    def test_parse_detail_one_zip(self) -> None:
        """Detail page with one ZIP file should yield one download."""
        downloads = parse_news_detail(DETAIL_PAGE_ONE_ZIP_HTML)

        self.assertEqual(len(downloads), 1)

    def test_parse_detail_one_zip_url(self) -> None:
        downloads = parse_news_detail(DETAIL_PAGE_ONE_ZIP_HTML)

        self.assertIn("638889473019415029.zip", downloads[0].url)
        self.assertTrue(downloads[0].url.startswith("https://"))

    def test_parse_detail_skips_non_zip_links(self) -> None:
        """Non-ZIP links (e.g., .pdf) should not appear in results."""
        downloads = parse_news_detail(DETAIL_PAGE_MIXED_HTML)

        self.assertEqual(len(downloads), 1)
        self.assertTrue(downloads[0].url.endswith(".zip"))

    def test_parse_detail_no_zip_returns_empty(self) -> None:
        downloads = parse_news_detail(DETAIL_PAGE_NO_ZIP_HTML)

        self.assertEqual(downloads, [])

    def test_parse_detail_empty_html_returns_empty(self) -> None:
        downloads = parse_news_detail("<html><body></body></html>")

        self.assertEqual(downloads, [])


# ---------------------------------------------------------------------------
# TaisugarNewsItem dataclass tests
# ---------------------------------------------------------------------------

class TaisugarNewsItemTests(unittest.TestCase):

    def test_news_item_fields(self) -> None:
        item = TaisugarNewsItem(
            title="111年新進工員(含產學)甄試試題",
            detail_url="https://www.taisugar.com.tw/chinese/News_detail.aspx?p=3&n=10080&s=11543",
            year_roc=111,
        )

        self.assertEqual(item.title, "111年新進工員(含產學)甄試試題")
        self.assertEqual(item.year_roc, 111)
        self.assertTrue(item.detail_url.startswith("https://"))


# ---------------------------------------------------------------------------
# TaisugarDownload dataclass tests
# ---------------------------------------------------------------------------

class TaisugarDownloadTests(unittest.TestCase):

    def test_download_fields(self) -> None:
        dl = TaisugarDownload(
            label="111年度新進工員甄試試題及解答(12Mb)(.ZIP)",
            url="https://www.taisugar.com.tw/upload/UserFiles/News/11543/638382326576030861.zip",
        )

        self.assertEqual(dl.label, "111年度新進工員甄試試題及解答(12Mb)(.ZIP)")
        self.assertTrue(dl.url.endswith(".zip"))


# ---------------------------------------------------------------------------
# Client integration tests (mocked _fetch_text)
# ---------------------------------------------------------------------------

class TaisugarRecruitClientTests(unittest.TestCase):

    def _make_client_with_listing_and_detail(
        self,
        listing_html: str,
        detail_html: str,
    ) -> TaisugarRecruitClient:
        """Return a client that returns listing_html for listing URLs and detail_html for detail URLs."""
        client = TaisugarRecruitClient()

        def fake_fetch(url: str) -> str:
            if "News_Index" in url:
                return listing_html
            return detail_html

        client._fetch_text = fake_fetch  # type: ignore[method-assign]
        return client

    def test_discover_available_years_returns_sorted_descending(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        years = client.discover_available_years()

        # 114→2025, 111→2022 from the fixture
        self.assertEqual(years, [2025, 2022])

    def test_discover_exams_returns_exam_options_for_year(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        exams = client.discover_exams(2025)

        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0].code, "taisugar-recruit-114")
        self.assertEqual(exams[0].year_ad, 2025)
        self.assertEqual(exams[0].year_roc, 114)

    def test_discover_exams_returns_empty_for_unknown_year(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        exams = client.discover_exams(2000)

        self.assertEqual(exams, [])

    def test_fetch_exam_page_builds_source_exam_page(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        page = client.fetch_exam_page("taisugar-recruit-111", 2022)

        self.assertEqual(page.provider_id, "taisugar_recruit")
        self.assertEqual(page.source_exam_id, "taisugar-recruit-111")
        self.assertEqual(page.year_ad, 2022)
        self.assertEqual(page.year_roc, 111)

    def test_fetch_exam_page_two_zips_produces_two_papers(self) -> None:
        """Each ZIP file becomes a separate ParsedPaper."""
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        page = client.fetch_exam_page("taisugar-recruit-111", 2022)

        self.assertEqual(len(page.papers), 2)

    def test_fetch_exam_page_paper_has_accessible_bundle_file_type(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        page = client.fetch_exam_page("taisugar-recruit-111", 2022)

        for paper in page.papers:
            self.assertIn("accessible_bundle", paper.files)

    def test_fetch_exam_page_paper_url_points_to_zip(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        page = client.fetch_exam_page("taisugar-recruit-111", 2022)

        for paper in page.papers:
            url = paper.files["accessible_bundle"]
            self.assertTrue(url.endswith(".zip"))
            self.assertIn("taisugar.com.tw", url)

    def test_fetch_exam_page_paper_category_raw(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        page = client.fetch_exam_page("taisugar-recruit-111", 2022)

        for paper in page.papers:
            self.assertEqual(paper.category_raw, "台糖新進工員甄試")

    def test_fetch_exam_page_one_zip_produces_one_paper(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_ONE_ZIP_HTML
        )
        page = client.fetch_exam_page("taisugar-recruit-114", 2025)

        self.assertEqual(len(page.papers), 1)

    def test_fetch_exam_page_exam_name_raw_contains_year(self) -> None:
        client = self._make_client_with_listing_and_detail(
            LISTING_PAGE_HTML, DETAIL_PAGE_TWO_ZIPS_HTML
        )
        page = client.fetch_exam_page("taisugar-recruit-111", 2022)

        self.assertIn("111", page.exam_name_raw)


# ---------------------------------------------------------------------------
# Registry test
# ---------------------------------------------------------------------------

class TaisugarRecruitRegistryTests(unittest.TestCase):

    def test_registry_returns_taisugar_recruit_provider(self) -> None:
        from app.providers.registry import get_provider
        from app.providers.base import SourceProvider

        provider = get_provider("taisugar_recruit")

        self.assertIsInstance(provider, SourceProvider)
        self.assertEqual(provider.provider_id, "taisugar_recruit")


if __name__ == "__main__":
    unittest.main()
