from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from app.models import ExamOption, ParsedPaper, SourceExamPage
from app.providers.base import DownloadedFile, ResponseMetadata

BASE_URL = "https://www.taisugar.com.tw/"
LISTING_URL = "https://www.taisugar.com.tw/chinese/News_Index.aspx?p=3&n=10080"
_LISTING_BASE_URL = "https://www.taisugar.com.tw/chinese/"
USER_AGENT = "Mozilla/5.0 (compatible; taisugar-recruit-mirror/1.0)"
CANONICAL_CATEGORY = "台糖新進工員甄試"

# Matches ROC year in news item title: "114年新進工員甄試試題" -> 114
_YEAR_RE = re.compile(r"(\d{2,3})\s*年")

# Pagination URL pattern: append &page=N
_PAGE_URL = "https://www.taisugar.com.tw/chinese/News_Index.aspx?p=3&n=10080&page={page}"

MAX_PAGES = 50


@dataclass(frozen=True)
class TaisugarNewsItem:
    """A news listing item that links to an exam-paper detail page."""
    title: str
    detail_url: str
    year_roc: int


@dataclass(frozen=True)
class TaisugarDownload:
    """A single ZIP download from a detail page."""
    label: str
    url: str


def _normalize_text(text: str) -> str:
    return " ".join(unescape(text).split())


class _NewsListingParser(HTMLParser):
    """Parse the Taisugar news listing page.

    Expected structure:
      <div class="wucNews_index">
        <ul>
          <li>
            <a href="News_detail.aspx?p=3&n=10080&s=[ID]" title="[Title]">
              <img ...>
              <h3>[Title]</h3>
              <span class="date">[Date]</span>
              [Summary text]
            </a>
          </li>
          ...
        </ul>
      </div>

    Only items whose title contains '甄試試題' are kept.
    """

    def __init__(self) -> None:
        super().__init__()
        self._in_news_list: bool = False
        self._div_depth_news: int = 0
        self._in_li: bool = False
        self._li_depth: int = 0
        self._in_anchor: bool = False
        self._current_href: str = ""
        self._current_title: str = ""
        self._in_h3: bool = False
        self._h3_parts: list[str] = []
        self.items: list[TaisugarNewsItem] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = (attrs_dict.get("class") or "").split()

        if tag == "div" and {"n_content", "wucNews_index"}.intersection(classes):
            self._in_news_list = True
            self._div_depth_news = 1
            return

        if self._in_news_list and tag == "div":
            self._div_depth_news += 1
            return

        if not self._in_news_list:
            return

        if tag == "li":
            self._in_li = True
            self._li_depth = 1
            self._current_href = ""
            self._current_title = ""
            self._h3_parts = []
            return

        if not self._in_li:
            return

        if tag == "li":
            # nested li — track depth
            self._li_depth += 1
            return

        if tag == "a" and not self._in_anchor:
            href = attrs_dict.get("href") or ""
            title = attrs_dict.get("title") or ""
            if "News_detail.aspx" in href:
                self._in_anchor = True
                self._current_href = href
                self._current_title = _normalize_text(title)
            return

        if self._in_anchor and tag == "h3":
            self._in_h3 = True
            self._h3_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_h3:
            self._h3_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self._in_news_list:
            self._div_depth_news -= 1
            if self._div_depth_news == 0:
                self._in_news_list = False
            return

        if tag == "h3" and self._in_h3:
            self._in_h3 = False
            return

        if tag == "a" and self._in_anchor:
            self._in_anchor = False
            return

        if tag == "li" and self._in_li:
            self._li_depth -= 1
            if self._li_depth == 0:
                self._flush_item()
                self._in_li = False

    def _flush_item(self) -> None:
        # Prefer title attribute; fall back to h3 text
        title = self._current_title
        if not title:
            title = _normalize_text("".join(self._h3_parts))
        if not title or "甄試試題" not in title:
            return
        href = self._current_href
        if not href:
            return
        match = _YEAR_RE.search(title)
        if match is None:
            return
        year_roc = int(match.group(1))
        # Make the detail URL absolute
        detail_url = urljoin(_LISTING_BASE_URL, href)
        self.items.append(
            TaisugarNewsItem(
                title=title,
                detail_url=detail_url,
                year_roc=year_roc,
            )
        )


class _NewsDetailParser(HTMLParser):
    """Parse a Taisugar news detail page for ZIP download links.

    Expected structure (may repeat):
      <p>相關檔案：</p>
      <p>
        <a href="../upload/UserFiles/News/[ID]/[filename].zip"
           title="(另存目標下載檔案)(NMb)">
          [Label](.ZIP)
          <img src="../images/icon_zip.png" alt="">
        </a>
      </p>

    We collect any <a> tag whose href ends with '.zip' (case-insensitive).
    Depth counters on <p> tags guard against malformed nesting.
    """

    def __init__(self) -> None:
        super().__init__()
        self._in_anchor: bool = False
        self._current_href: str = ""
        self._anchor_parts: list[str] = []
        self.downloads: list[TaisugarDownload] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        if tag == "a":
            href = attrs_dict.get("href") or ""
            if href.lower().endswith(".zip"):
                self._in_anchor = True
                self._current_href = href
                self._anchor_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_anchor:
            self._anchor_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_anchor:
            label = _normalize_text("".join(self._anchor_parts))
            url = urljoin(BASE_URL, self._current_href)
            self.downloads.append(TaisugarDownload(label=label, url=url))
            self._in_anchor = False
            self._anchor_parts = []
            self._current_href = ""


def parse_news_listing(html: str) -> list[TaisugarNewsItem]:
    """Parse the Taisugar news listing page and return exam-paper items."""
    parser = _NewsListingParser()
    parser.feed(html)
    return parser.items


def parse_news_detail(html: str) -> list[TaisugarDownload]:
    """Parse a Taisugar news detail page and return ZIP download links."""
    parser = _NewsDetailParser()
    parser.feed(html)
    return parser.downloads


class TaisugarRecruitClient:
    provider_id = "taisugar_recruit"

    def _fetch_text(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            raw = response.read()
            # Taisugar pages may be Big5 or UTF-8; try UTF-8 first
            for encoding in ("utf-8", "big5", "cp950"):
                try:
                    return raw.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return raw.decode("utf-8", "replace")

    def head(self, url: str) -> ResponseMetadata:
        request = Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
        with urlopen(request, timeout=60) as response:
            content_length = response.headers.get("Content-Length")
            return ResponseMetadata(
                url=url,
                status=response.status,
                content_length=int(content_length) if content_length else None,
                content_type=response.headers.get("Content-Type", ""),
                content_disposition=response.headers.get("Content-Disposition", ""),
                cache_control=response.headers.get("Cache-Control", ""),
            )

    def download_file(self, url: str) -> DownloadedFile:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=120) as response:
            return DownloadedFile(
                data=response.read(),
                content_type=response.headers.get("Content-Type", "application/octet-stream"),
                file_name=Path(unquote(urlparse(url).path)).name,
            )

    def _iter_listing_items(self) -> list[TaisugarNewsItem]:
        """Fetch all listing pages and return exam-paper news items.

        Pagination stops when a page returns no new items (empty or all already
        seen), preventing infinite loops when all pages return identical content.
        """
        items: list[TaisugarNewsItem] = []
        seen_urls: set[str] = set()
        page = 1
        while page <= MAX_PAGES:
            url = LISTING_URL if page == 1 else _PAGE_URL.format(page=page)
            html = self._fetch_text(url)
            page_items = parse_news_listing(html)
            # Stop if no items found or all items already seen (end of pagination)
            new_items = [i for i in page_items if i.detail_url not in seen_urls]
            if not new_items:
                break
            for item in new_items:
                seen_urls.add(item.detail_url)
            items.extend(new_items)
            page += 1
        return items

    def _fetch_downloads(self, detail_url: str) -> list[TaisugarDownload]:
        html = self._fetch_text(detail_url)
        return parse_news_detail(html)

    def discover_available_years(self) -> list[int]:
        return sorted(
            {item.year_roc + 1911 for item in self._iter_listing_items()},
            reverse=True,
        )

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        return [
            ExamOption(
                code=f"taisugar-recruit-{item.year_roc}",
                year_ad=item.year_roc + 1911,
                year_roc=item.year_roc,
                label=item.title,
            )
            for item in self._iter_listing_items()
            if item.year_roc + 1911 == year_ad
        ]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        news_item = next(
            item
            for item in self._iter_listing_items()
            if f"taisugar-recruit-{item.year_roc}" == exam_code
            and item.year_roc + 1911 == year_ad
        )
        downloads = self._fetch_downloads(news_item.detail_url)
        papers: list[ParsedPaper] = []
        for index, dl in enumerate(downloads, start=1):
            papers.append(
                ParsedPaper(
                    category_raw=CANONICAL_CATEGORY,
                    category_code=str(news_item.year_roc),
                    subject_code=f"taisugar-recruit-{news_item.year_roc}-{index:02d}",
                    subject_name_raw=dl.label,
                    files={"accessible_bundle": dl.url},
                )
            )
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=news_item.year_roc,
            exam_name_raw=news_item.title,
            attachments=[],
            papers=papers,
            provider_id=self.provider_id,
        )
