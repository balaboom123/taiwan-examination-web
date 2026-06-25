"""CPC Corporation (中油) recruitment exam provider — client and HTML parser.

Two source pages are merged:
  - PhD exam papers:   https://www.cpc.com.tw/News_Content.aspx?n=32&s=826
  - Hiring outlines:   https://www.cpc.com.tw/News_Content.aspx?n=32&s=824

Both pages use an ASP.NET CMS that renders the inner content inside a div
(``ContentPlaceHolder1_contentText`` or ``mcnTextContent``).  Anchors point
to the download handler::

    https://ws.cpc.com.tw/Download.ashx?u=<b64-path>&n=<b64-filename>

The ``u`` and ``n`` query-string parameters are base64-encoded — they are
preserved verbatim; this module never decodes or re-encodes them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from app.models import ExamOption, ParsedPaper, SourceExamPage
from app.providers.base import DownloadedFile, ResponseMetadata

BASE_URL = "https://www.cpc.com.tw/"
DOWNLOAD_BASE_URL = "https://ws.cpc.com.tw/"
PHD_PAGE_URL = "https://www.cpc.com.tw/News_Content.aspx?n=32&s=826"
HIRING_PAGE_URL = "https://www.cpc.com.tw/News_Content.aspx?n=32&s=824"
USER_AGENT = "Mozilla/5.0 (compatible; cpc-recruit-mirror/1.0)"
CANONICAL_CATEGORY = "中油新進人員甄試"

_YEAR_RE = re.compile(r"(\d{2,3})\s*年")


def _normalize_text(text: str) -> str:
    return " ".join(unescape(text).split())


@dataclass(frozen=True)
class CpcRecruitEntry:
    """A single PDF download entry from one of the CPC exam pages."""

    year_roc: int
    year_ad: int
    label: str
    url: str
    source: str  # "phd" | "hiring"


class _ContentPageParser(HTMLParser):
    """Parse a CPC ``News_Content.aspx`` page and collect anchor links.

    CPC's ASP.NET CMS renders the body text inside a ``<div>`` whose id
    contains ``ContentPlaceHolder1_contentText`` or whose class contains
    ``mcnTextContent``.  Inside that container there are ``<table>`` rows
    with ``<a>`` anchors pointing to ``Download.ashx``.

    The parser uses an *inside-content-area* flag plus a depth counter so
    that nested ``<div>`` elements (e.g. additional wrappers) do not cause
    premature exit from the capture region.
    """

    # Attribute fragments that identify the outer content wrapper.
    _CONTENT_ID_FRAGMENT = "ContentPlaceHolder1_contentText"
    _CONTENT_CLASS = "mcnTextContent"

    def __init__(self) -> None:
        super().__init__()
        # Whether we are inside the relevant content area
        self._in_content: bool = False
        # Depth counter for div nesting inside the content area
        self._content_div_depth: int = 0
        # Anchor capture state
        self._in_anchor: bool = False
        self._current_href: str = ""
        self._anchor_parts: list[str] = []
        # Collected raw hrefs (absolute or relative) with link text
        self.links: list[tuple[str, str]] = []  # (href, label)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        if tag == "div":
            div_id = attrs_dict.get("id") or ""
            div_classes = (attrs_dict.get("class") or "").split()
            if (
                self._CONTENT_ID_FRAGMENT in div_id
                or self._CONTENT_CLASS in div_classes
            ):
                self._in_content = True
                self._content_div_depth = 1
                return
            if self._in_content:
                self._content_div_depth += 1
            return

        if not self._in_content:
            return

        if tag == "a":
            href = attrs_dict.get("href") or ""
            if href:
                self._in_anchor = True
                self._current_href = unescape(href)
                self._anchor_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_anchor:
            self._anchor_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self._in_content:
            self._content_div_depth -= 1
            if self._content_div_depth == 0:
                self._in_content = False
            return

        if tag == "a" and self._in_anchor:
            label = _normalize_text("".join(self._anchor_parts))
            href = self._current_href
            if label and href:
                self.links.append((href, label))
            self._in_anchor = False
            self._anchor_parts = []
            self._current_href = ""


def parse_employment_page(html: str, source: str = "phd") -> list[CpcRecruitEntry]:
    """Parse a CPC employment news-content page and return download entries.

    Args:
        html:   Raw HTML of the page.
        source: ``"phd"`` for the PhD exam papers page or ``"hiring"`` for
                the hiring-outline page.  Stored on each entry.

    Returns:
        List of :class:`CpcRecruitEntry` objects, one per valid anchor link
        that carries a ROC year number.
    """
    parser = _ContentPageParser()
    parser.feed(html)

    entries: list[CpcRecruitEntry] = []
    for href, label in parser.links:
        match = _YEAR_RE.search(label)
        if match is None:
            continue
        year_roc = int(match.group(1))
        entries.append(
            CpcRecruitEntry(
                year_roc=year_roc,
                year_ad=year_roc + 1911,
                label=label,
                url=href,
                source=source,
            )
        )
    return entries


class CpcRecruitClient:
    """HTTP client and data-aggregator for the CPC recruitment exam provider."""

    provider_id = "cpc_recruit"

    def _fetch_text(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            body = response.read()
            # CPC may serve Big5/CP950; detect from meta charset or fall back
            content_type: str = response.headers.get("Content-Type", "")
            return _decode_html_bytes(body, content_type)

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
            content_disposition = response.headers.get("Content-Disposition", "")
            file_name = _filename_from_disposition(content_disposition) or Path(
                unquote(urlparse(url).path)
            ).name or "download.pdf"
            return DownloadedFile(
                data=response.read(),
                content_type=response.headers.get("Content-Type", "application/octet-stream"),
                file_name=file_name,
            )

    def _iter_entries(self) -> list[CpcRecruitEntry]:
        """Fetch both pages and return a combined, de-duplicated entry list."""
        phd_html = self._fetch_text(PHD_PAGE_URL)
        hiring_html = self._fetch_text(HIRING_PAGE_URL)
        phd_entries = parse_employment_page(phd_html, source="phd")
        hiring_entries = parse_employment_page(hiring_html, source="hiring")
        return phd_entries + hiring_entries

    def discover_available_years(self) -> list[int]:
        return sorted(
            {entry.year_ad for entry in self._iter_entries()},
            reverse=True,
        )

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        year_roc = year_ad - 1911
        # Each ROC year may appear in both sources; emit one option per year.
        seen: set[int] = set()
        options: list[ExamOption] = []
        for entry in self._iter_entries():
            if entry.year_ad != year_ad:
                continue
            if entry.year_roc in seen:
                continue
            seen.add(entry.year_roc)
            options.append(
                ExamOption(
                    code=f"cpc-recruit-{entry.year_roc}",
                    year_ad=entry.year_ad,
                    year_roc=entry.year_roc,
                    label=f"{entry.year_roc}年中油公司新進人員甄試",
                )
            )
        return options

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        year_roc = year_ad - 1911
        entries = [
            e for e in self._iter_entries()
            if e.year_roc == year_roc
        ]
        if not entries:
            return SourceExamPage(
                source_exam_id=exam_code,
                year_ad=year_ad,
                year_roc=year_roc,
                exam_name_raw=exam_code,
                attachments=[],
                papers=[],
                provider_id=self.provider_id,
            )

        papers: list[ParsedPaper] = []
        for index, entry in enumerate(entries, start=1):
            # Determine file type from label heuristics
            label_lower = entry.label
            if any(kw in label_lower for kw in ("答案", "解答", "答題")):
                file_type = "answer"
            else:
                file_type = "question"

            subject_prefix = "phd" if entry.source == "phd" else "hire"
            papers.append(
                ParsedPaper(
                    category_raw=CANONICAL_CATEGORY,
                    category_code=str(year_roc),
                    subject_code=f"{subject_prefix}-{index:02d}",
                    subject_name_raw=entry.label,
                    files={file_type: entry.url},
                )
            )

        exam_name_raw = f"{year_roc}年中油公司新進人員甄試"
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_roc,
            exam_name_raw=exam_name_raw,
            attachments=[],
            papers=papers,
            provider_id=self.provider_id,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HEADER_CHARSET_RE = re.compile(r"charset=['\"]?\s*([a-zA-Z0-9_-]+)", re.IGNORECASE)
_HTML_CHARSET_RE = re.compile(rb"<meta[^>]+charset=['\"]?\s*([a-zA-Z0-9_-]+)", re.IGNORECASE)
_CONTENT_DISPOSITION_FILENAME_RE = re.compile(
    r'filename\*?=(?:UTF-8\'\'|")?([^";]+)', re.IGNORECASE
)


def _charset_from_content_type(content_type: str) -> str | None:
    match = _HEADER_CHARSET_RE.search(content_type)
    return match.group(1) if match else None


def _charset_from_html_bytes(body: bytes) -> str | None:
    match = _HTML_CHARSET_RE.search(body)
    return match.group(1).decode("ascii", "ignore") if match else None


def _decode_html_bytes(body: bytes, content_type: str) -> str:
    encodings = [
        _charset_from_content_type(content_type),
        _charset_from_html_bytes(body),
        "cp950",
        "big5",
        "utf-8",
    ]
    seen: set[str] = set()
    for enc in encodings:
        if not enc:
            continue
        key = enc.lower()
        if key in seen:
            continue
        seen.add(key)
        try:
            return body.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", "replace")


def _filename_from_disposition(header: str) -> str | None:
    match = _CONTENT_DISPOSITION_FILENAME_RE.search(header)
    if match:
        return unescape(unquote(match.group(1).strip().strip('"')))
    return None
