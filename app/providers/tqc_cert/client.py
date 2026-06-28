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

BASE_URL = "https://www.tqc.org.tw/TQCNet/"
EXAM_PAPER_URL = urljoin(BASE_URL, "ExamPaper.aspx")
USER_AGENT = "Mozilla/5.0 (compatible; tqc-cert-mirror/1.0)"
CANONICAL_CATEGORY = "TQC範例試卷"
MATERIALS_YEAR = 2026


@dataclass(frozen=True)
class TqcExamPaper:
    title: str
    category: str
    published_year: int
    url: str


def _normalize_text(text: str) -> str:
    return " ".join(unescape(text).split())


class _TokenParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tokens: list[tuple[str, str, str]] = []
        self._in_anchor = False
        self._href = ""
        self._anchor_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        self._in_anchor = True
        self._href = dict(attrs).get("href", "") or ""
        self._anchor_parts = []

    def handle_data(self, data: str) -> None:
        text = _normalize_text(data)
        if not text:
            return
        if self._in_anchor:
            self._anchor_parts.append(text)
        else:
            self.tokens.append(("text", text, ""))

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._in_anchor:
            return
        self.tokens.append(("link", _normalize_text(" ".join(self._anchor_parts)), self._href))
        self._in_anchor = False
        self._href = ""
        self._anchor_parts = []


def _slug(text: str, fallback: str) -> str:
    ascii_slug = re.sub(r"[^0-9A-Za-z]+", "-", text).strip("-").lower()
    if ascii_slug:
        return ascii_slug
    encoded = text.encode("utf-8").hex()[:24]
    return encoded or fallback


def parse_exam_papers(html: str) -> list[TqcExamPaper]:
    parser = _TokenParser()
    parser.feed(html)
    entries: list[TqcExamPaper] = []
    text_window: list[str] = []
    for token_type, token_text, token_href in parser.tokens:
        if token_type == "text":
            text_window.append(token_text)
            text_window = text_window[-4:]
            continue
        if "/user/Example/" not in token_href or not token_href.lower().endswith(".pdf"):
            continue
        if len(text_window) < 3:
            continue
        title, category, published = text_window[-3], text_window[-2], text_window[-1]
        year_match = re.match(r"(\d{4})/", published)
        entries.append(
            TqcExamPaper(
                title=title,
                category=category,
                published_year=int(year_match.group(1)) if year_match else 0,
                url=urljoin(EXAM_PAPER_URL, token_href),
            )
        )
    return entries


class TqcCertClient:
    provider_id = "tqc_cert"

    def __init__(self) -> None:
        self._cached_entries: list[TqcExamPaper] | None = None

    def _fetch_text(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            raw = response.read()
        for encoding in ("utf-8", "big5", "cp950"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", "replace")

    def _entries(self) -> list[TqcExamPaper]:
        if self._cached_entries is None:
            self._cached_entries = parse_exam_papers(self._fetch_text(EXAM_PAPER_URL))
        return self._cached_entries

    def _entry_year(self, entry: TqcExamPaper) -> int:
        return entry.published_year or MATERIALS_YEAR

    def discover_available_years(self) -> list[int]:
        years = {self._entry_year(entry) for entry in self._entries()}
        return sorted(years, reverse=True)

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        if year_ad not in self.discover_available_years():
            return []
        return [ExamOption(code=f"tqc-cert-samples-{year_ad}", year_ad=year_ad, year_roc=year_ad - 1911, label=f"{year_ad} TQC範例試卷")]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        entries = [entry for entry in self._entries() if self._entry_year(entry) == year_ad]
        papers = [
            ParsedPaper(
                category_raw=f"{CANONICAL_CATEGORY}_{entry.category}",
                category_code=_slug(entry.category, f"category-{index}"),
                subject_code=_slug(entry.title, f"sample-{index}"),
                subject_name_raw=entry.title,
                files={"question": entry.url},
            )
            for index, entry in enumerate(entries, start=1)
        ]
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="TQC官方範例試卷",
            attachments=[],
            papers=papers,
            provider_id=self.provider_id,
        )

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
