from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from app.models import ExamOption, ParsedPaper, SourceExamPage
from app.providers.base import DownloadedFile, ResponseMetadata

BASE_URL = "https://www.taipower.com.tw/"
DOWNLOAD_URL = "https://www.taipower.com.tw/tc/download.aspx?mid=262"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": BASE_URL,
}
CANONICAL_CATEGORY = "台電新進僱用人員甄試"
_YEAR_RE = re.compile(r"(\d{2,3})\s*年")
_MONTH_RE = re.compile(r"(\d{1,2})\s*月")


@dataclass(frozen=True)
class TaipowerRecruitDownload:
    label: str
    url: str


@dataclass(frozen=True)
class TaipowerRecruitEntry:
    year_roc: int
    year_ad: int
    title: str
    month: int | None
    downloads: list[TaipowerRecruitDownload]


def _normalize_text(text: str) -> str:
    return " ".join(unescape(text).split())


class _HiringPageParser(HTMLParser):
    """Parse the Taipower hiring exam download listing page.

    Structure (as of 2025):
      <ul>
        <li>
          <p class="title">NNN年[MM月]...</p>
          <div class="drawerBox">
            <ul class="fileDownload">
              <li>
                <span class="name">Label</span>
                <ul class="downloadFiles">
                  <li><a download href="/media/...?mediaDL=true">...</a></li>
                </ul>
              </li>
            </ul>
          </div>
        </li>
      </ul>
    """

    def __init__(self) -> None:
        super().__init__()
        self._in_title_p: bool = False
        self._title_parts: list[str] = []
        self._in_name_span: bool = False
        self._name_parts: list[str] = []
        self._current_title: str = ""
        self._current_name: str = ""
        self._current_downloads: list[TaipowerRecruitDownload] = []
        self.entries: list[TaipowerRecruitEntry] = []

    def _flush_entry(self) -> None:
        title = self._current_title
        if not title or not self._current_downloads:
            return
        year_match = _YEAR_RE.search(title)
        if year_match is None:
            return
        year_roc = int(year_match.group(1))
        month: int | None = None
        month_match = _MONTH_RE.search(title[year_match.end():])
        if month_match is not None:
            month = int(month_match.group(1))
        self.entries.append(
            TaipowerRecruitEntry(
                year_roc=year_roc,
                year_ad=year_roc + 1911,
                title=title,
                month=month,
                downloads=list(self._current_downloads),
            )
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = (attrs_dict.get("class") or "").split()

        if tag == "p" and "title" in classes:
            self._flush_entry()
            self._current_downloads = []
            self._in_title_p = True
            self._title_parts = []
            return

        if tag == "span" and "name" in classes:
            self._in_name_span = True
            self._name_parts = []
            return

        if tag == "a" and "download" in attrs_dict:
            href = attrs_dict.get("href") or ""
            if href:
                label = self._current_name or _normalize_text(unquote(Path(urlparse(href).path).stem))
                url = urljoin(BASE_URL, href)
                self._current_downloads.append(TaipowerRecruitDownload(label=label, url=url))

    def handle_data(self, data: str) -> None:
        if self._in_title_p:
            self._title_parts.append(data)
        elif self._in_name_span:
            self._name_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._in_title_p:
            self._current_title = _normalize_text("".join(self._title_parts))
            self._in_title_p = False

        if tag == "span" and self._in_name_span:
            self._current_name = _normalize_text("".join(self._name_parts))
            self._in_name_span = False

    def close(self) -> None:
        super().close()
        self._flush_entry()


_YEAR_TAB_RE = re.compile(
    r'<a\s+href="(/\d+/\d+/\d+/\d+/\?[^"]+q_attribute=\d+)"[^>]*>'
    r"(\d{2,3})年度?</a>"
)


def parse_hiring_page(html: str) -> list[TaipowerRecruitEntry]:
    """Parse the Taipower hiring exam download listing page."""
    parser = _HiringPageParser()
    parser.feed(html)
    parser.close()
    return parser.entries


def parse_year_tabs(html: str) -> list[tuple[int, str]]:
    """Extract (year_roc, relative_url) pairs from year navigation tabs."""
    results: list[tuple[int, str]] = []
    for m in _YEAR_TAB_RE.finditer(html):
        href = unescape(m.group(1))
        year_roc = int(m.group(2))
        results.append((year_roc, href))
    return results


def _exam_code(entry: TaipowerRecruitEntry) -> str:
    """Build the canonical exam code for an entry."""
    if entry.month is not None:
        return f"taipower-recruit-{entry.year_roc}-{entry.month}"
    return f"taipower-recruit-{entry.year_roc}"


def _quote_url_for_request(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            quote(unquote(parts.path), safe="/%"),
            quote(unquote(parts.query), safe="=&%"),
            quote(unquote(parts.fragment), safe="%"),
        )
    )


class TaipowerRecruitClient:
    provider_id = "taipower_recruit"

    def __init__(self) -> None:
        self._cached_entries: list[TaipowerRecruitEntry] | None = None

    def _fetch_text(self, url: str) -> str:
        request = Request(_quote_url_for_request(url), headers=REQUEST_HEADERS)
        with urlopen(request, timeout=60) as response:
            raw = response.read()
            for encoding in ("utf-8", "big5", "cp950"):
                try:
                    return raw.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    continue
            return raw.decode("utf-8", "replace")

    def head(self, url: str) -> ResponseMetadata:
        request = Request(_quote_url_for_request(url), headers=REQUEST_HEADERS, method="HEAD")
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
        request = Request(_quote_url_for_request(url), headers=REQUEST_HEADERS)
        with urlopen(request, timeout=120) as response:
            return DownloadedFile(
                data=response.read(),
                content_type=response.headers.get("Content-Type", "application/octet-stream"),
                file_name=Path(unquote(urlparse(url).path)).name,
            )

    def _iter_entries(self) -> list[TaipowerRecruitEntry]:
        if self._cached_entries is not None:
            return self._cached_entries
        main_html = self._fetch_text(DOWNLOAD_URL)
        entries = parse_hiring_page(main_html)
        seen_years = {e.year_roc for e in entries}
        for year_roc, rel_url in parse_year_tabs(main_html):
            if year_roc in seen_years:
                continue
            seen_years.add(year_roc)
            page_url = urljoin(BASE_URL, rel_url)
            page_html = self._fetch_text(page_url)
            entries.extend(parse_hiring_page(page_html))
        self._cached_entries = entries
        return entries

    def discover_available_years(self) -> list[int]:
        return sorted({entry.year_ad for entry in self._iter_entries()}, reverse=True)

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        seen: set[str] = set()
        result: list[ExamOption] = []
        for entry in self._iter_entries():
            if entry.year_ad != year_ad:
                continue
            code = _exam_code(entry)
            if code in seen:
                continue
            seen.add(code)
            result.append(
                ExamOption(
                    code=code,
                    year_ad=entry.year_ad,
                    year_roc=entry.year_roc,
                    label=entry.title,
                )
            )
        return result

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        matching = [
            item for item in self._iter_entries()
            if _exam_code(item) == exam_code and item.year_ad == year_ad
        ]
        if not matching:
            raise ValueError(f"No entries found for {exam_code} year {year_ad}")
        first = matching[0]
        papers: list[ParsedPaper] = []
        for file_index, download in enumerate(
            (dl for entry in matching for dl in entry.downloads), start=1
        ):
            if "答案" in download.label or "解答" in download.label:
                file_type = "answer"
            else:
                file_type = "question"
            papers.append(
                ParsedPaper(
                    category_raw=CANONICAL_CATEGORY,
                    category_code=str(first.year_roc),
                    subject_code=f"hiring-{file_index:02d}",
                    subject_name_raw=download.label,
                    files={file_type: download.url},
                )
            )
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=first.year_roc,
            exam_name_raw=first.title,
            attachments=[],
            papers=papers,
            provider_id=self.provider_id,
        )
