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

BASE_URL = "https://www.ceec.edu.tw/"
LISTING_URL = "https://www.ceec.edu.tw/xmfile?xsmsid=0J052427633128416650"
USER_AGENT = "Mozilla/5.0 (compatible; ceec-ast-mirror/1.0)"
_TOTAL_PAGES_RE = re.compile("共\\s*(\\d+)\\s*頁")
_ENTRY_HEADER_RE = re.compile(
    r"(?P<roc_year>\d{3})-\d{2}-\d{2}\s+(?P<title>\d{3}\s*學年度分科測驗[－-].+)"
)
_ENTRY_DATE_RE = re.compile(r"(?P<roc_year>\d{3})-\d{2}-\d{2}$")
_ENTRY_TITLE_RE = re.compile(r"(?P<title>(?P<roc_year>\d{3})\s*學年度分科測驗[－-].+)$")
_YEAR_BLOCK_RE = re.compile("選擇年度(?P<body>.*?)(?:※本試題為PDF|發佈日期)", re.S)
_YEAR_RE = re.compile(r"\b(\d{2,3})\b")
_CEEC_CATEGORY_NAME = "分科測驗"
_PAGINATION_LABELS = {"第一頁", "上一頁", "下一頁", "最後頁"}
_SUBJECT_SLUGS = {
    "國文": "chinese",
    "英文": "english",
    "數學甲": "math-a",
    "數學乙": "math-b",
    "歷史": "history",
    "地理": "geography",
    "公民與社會": "civics-society",
    "物理": "physics",
    "化學": "chemistry",
    "生物": "biology",
}


@dataclass(frozen=True)
class CeecAstDownload:
    label: str
    url: str


@dataclass(frozen=True)
class CeecAstEntry:
    source_exam_id: str
    year_ad: int
    title: str
    downloads: list[CeecAstDownload]


@dataclass(frozen=True)
class CeecAstListingPage:
    total_pages: int
    entries: list[CeecAstEntry]


class _ListingTokenParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tokens: list[tuple[str, str, str]] = []
        self._anchor_href = ""
        self._anchor_text_parts: list[str] = []
        self._in_anchor = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        self._in_anchor = True
        self._anchor_href = dict(attrs).get("href", "") or ""
        self._anchor_text_parts = []

    def handle_data(self, data: str) -> None:
        text = _normalize_text(data)
        if not text:
            return
        if self._in_anchor:
            self._anchor_text_parts.append(text)
            return
        self.tokens.append(("text", text, ""))

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._in_anchor:
            return
        label = _normalize_text(" ".join(self._anchor_text_parts))
        if label:
            self.tokens.append(("link", label, self._anchor_href))
        self._anchor_href = ""
        self._anchor_text_parts = []
        self._in_anchor = False


def _normalize_text(text: str) -> str:
    return " ".join(unescape(text).split())


def _plain_text_from_html(html: str) -> str:
    return _normalize_text(re.sub(r"<[^>]+>", " ", html))


def _subject_tail(title: str) -> str:
    parts = re.split("[－-]", _normalize_text(title), maxsplit=1)
    return parts[1] if len(parts) == 2 else parts[0]


def _slug_from_title(title: str) -> str:
    subject = _subject_tail(title)
    mapped = _SUBJECT_SLUGS.get(subject)
    if mapped:
        return mapped
    ascii_slug = re.sub(r"[^0-9A-Za-z]+", "-", subject).strip("-").lower()
    if ascii_slug:
        return ascii_slug
    return "subject-" + subject.encode("utf-8").hex()[:16]


def _entry_from_title(roc_year: int, title: str) -> CeecAstEntry:
    normalized_title = _normalize_text(title)
    return CeecAstEntry(
        source_exam_id=f"ceec-ast-{roc_year}-{_slug_from_title(normalized_title)}",
        year_ad=roc_year + 1911,
        title=normalized_title,
        downloads=[],
    )


def _available_years_from_text(text: str) -> list[int]:
    block = _YEAR_BLOCK_RE.search(text)
    if block is None:
        return []
    years: list[int] = []
    for match in _YEAR_RE.findall(block.group("body")):
        year_roc = int(match)
        if year_roc >= 80:
            years.append(year_roc + 1911)
    return sorted(dict.fromkeys(years), reverse=True)


def parse_listing_page(html: str) -> CeecAstListingPage:
    normalized_html = unescape(html)
    plain_text = _plain_text_from_html(normalized_html)
    total_pages_match = _TOTAL_PAGES_RE.search(plain_text)
    total_pages = int(total_pages_match.group(1)) if total_pages_match else 1
    parser = _ListingTokenParser()
    parser.feed(normalized_html)
    entries: list[CeecAstEntry] = []
    current_entry: CeecAstEntry | None = None
    pending_roc_year: int | None = None
    for token_type, token_text, token_href in parser.tokens:
        if token_type == "text":
            match = _ENTRY_HEADER_RE.match(token_text)
            if match is not None:
                if current_entry is not None and current_entry.downloads:
                    entries.append(current_entry)
                pending_roc_year = None
                current_entry = _entry_from_title(int(match.group("roc_year")), match.group("title"))
                continue
            date_match = _ENTRY_DATE_RE.match(token_text)
            if date_match is not None:
                if current_entry is not None and current_entry.downloads:
                    entries.append(current_entry)
                    current_entry = None
                pending_roc_year = int(date_match.group("roc_year"))
                continue
            title_match = _ENTRY_TITLE_RE.match(token_text)
            if pending_roc_year is not None and title_match is not None:
                current_entry = _entry_from_title(pending_roc_year, title_match.group("title"))
                pending_roc_year = None
                continue
            pending_roc_year = None
            continue
        if current_entry is None:
            pending_roc_year = None
            continue
        if token_text in _PAGINATION_LABELS or token_text.isdigit():
            if current_entry.downloads:
                entries.append(current_entry)
                current_entry = None
            continue
        current_entry.downloads.append(CeecAstDownload(label=token_text, url=urljoin(BASE_URL, token_href)))
    if current_entry is not None and current_entry.downloads:
        entries.append(current_entry)
    return CeecAstListingPage(total_pages=total_pages, entries=entries)


class CeecAstClient:
    provider_id = "ceec_ast"

    def _fetch_text(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", "replace")

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

    def _iter_entries(self) -> list[CeecAstEntry]:
        first_page_html = self._fetch_text(LISTING_URL)
        first_page = parse_listing_page(first_page_html)
        entries = list(first_page.entries)
        for page_number in range(2, first_page.total_pages + 1):
            page = parse_listing_page(self._fetch_text(f"{LISTING_URL}&page={page_number}"))
            entries.extend(page.entries)

        deduped: list[CeecAstEntry] = []
        seen: set[tuple[int, str]] = set()
        for entry in entries:
            key = (entry.year_ad, entry.source_exam_id)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(entry)
        return deduped

    def discover_available_years(self) -> list[int]:
        first_page_html = self._fetch_text(LISTING_URL)
        years = _available_years_from_text(_plain_text_from_html(first_page_html))
        if years:
            return years
        return sorted({entry.year_ad for entry in parse_listing_page(first_page_html).entries}, reverse=True)

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        return [
            ExamOption(code=entry.source_exam_id, year_ad=entry.year_ad, year_roc=entry.year_ad - 1911, label=entry.title)
            for entry in self._iter_entries()
            if entry.year_ad == year_ad
        ]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        entry = next(item for item in self._iter_entries() if item.source_exam_id == exam_code and item.year_ad == year_ad)
        subject_tail = _subject_tail(entry.title)
        subject_slug = _slug_from_title(entry.title)
        papers: list[ParsedPaper] = []
        question_seen = 0
        for index, download in enumerate(entry.downloads, start=1):
            if download.label == "試題內容":
                question_seen += 1
                file_type = "question" if question_seen == 1 else "question_alt"
            elif download.label == "答題卷":
                file_type = "answer_sheet"
            elif "評分原則" in download.label:
                file_type = "corrected_answer"
            elif "答案" in download.label:
                file_type = "answer"
            else:
                file_type = "corrected_answer"
            papers.append(
                ParsedPaper(
                    category_raw=_CEEC_CATEGORY_NAME,
                    category_code=str(year_ad - 1911),
                    subject_code=f"{subject_slug}-{index:02d}",
                    subject_name_raw=f"{subject_tail} {download.label}",
                    files={file_type: download.url},
                )
            )
        return SourceExamPage(
            source_exam_id=entry.source_exam_id,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw=entry.title,
            attachments=[],
            papers=papers,
            provider_id=self.provider_id,
        )
