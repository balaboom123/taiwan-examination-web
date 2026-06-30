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

DOWNLOAD_URL = "https://elearning.hakka.gov.tw/hakka/download-files"
USER_AGENT = "Mozilla/5.0 (compatible; hakka-cert-mirror/1.0)"
CANONICAL_CATEGORY = "客語能力認證官方教材及試題"
MATERIALS_YEAR = 2026


@dataclass(frozen=True)
class HakkaDownload:
    category_code: str
    label: str
    file_type: str
    url: str


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._in_anchor = False
        self._href = ""
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        self._in_anchor = True
        self._href = dict(attrs).get("href", "") or ""
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._in_anchor:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._in_anchor:
            return
        label = " ".join(unescape("".join(self._parts)).split())
        self.links.append((label, self._href))
        self._in_anchor = False
        self._href = ""
        self._parts = []


def _quote_url_for_request(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            quote(unquote(parts.path), safe="/:%"),
            quote(unquote(parts.query), safe="=&:%"),
            quote(unquote(parts.fragment), safe=""),
        )
    )


def _slug(text: str, fallback: str) -> str:
    ascii_slug = re.sub(r"[^0-9A-Za-z]+", "-", text).strip("-").lower()
    if ascii_slug:
        return ascii_slug
    encoded = text.encode("utf-8").hex()[:24]
    return encoded or fallback


def _subject_code(url: str, label: str, fallback: str) -> str:
    stem = Path(unquote(urlparse(url).path)).stem
    label_slug = _slug(label, fallback)
    return f"{stem}-{label_slug}" if stem and stem != label_slug else label_slug


def _dialect_code(label: str) -> str:
    for token, code in (
        ("四縣", "sixian"),
        ("海陸", "hailu"),
        ("大埔", "dapu"),
        ("饒平", "raoping"),
        ("詔安", "zhaoan"),
    ):
        if token in label:
            return code
    return "general"


def parse_downloads(html: str, *, base_url: str = DOWNLOAD_URL) -> list[HakkaDownload]:
    parser = _AnchorParser()
    parser.feed(html)
    downloads: list[HakkaDownload] = []
    seen: set[str] = set()
    for label, href in parser.links:
        url = _quote_url_for_request(urljoin(base_url, href))
        parsed = urlparse(url)
        if parsed.netloc != "elearning.hakka.gov.tw" or not parsed.path.startswith("/hakka/files/downloads/"):
            continue
        # ponytail: Hakka audio ZIPs make a multi-GB public bundle; add them when bundles can shard by dialect/file type.
        if not parsed.path.lower().endswith(".pdf") or url in seen:
            continue
        seen.add(url)
        display_label = label or Path(unquote(parsed.path)).name
        downloads.append(HakkaDownload(category_code=_dialect_code(display_label), label=display_label, file_type="question", url=url))
    return downloads


class HakkaCertClient:
    provider_id = "hakka_cert"

    def _fetch_text(self, url: str) -> str:
        request = Request(_quote_url_for_request(url), headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", "replace")

    def _downloads(self) -> list[HakkaDownload]:
        return parse_downloads(self._fetch_text(DOWNLOAD_URL), base_url=DOWNLOAD_URL)

    def discover_available_years(self) -> list[int]:
        return [MATERIALS_YEAR]

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        if year_ad != MATERIALS_YEAR:
            return []
        return [ExamOption(code="hakka-cert-materials", year_ad=year_ad, year_roc=year_ad - 1911, label=CANONICAL_CATEGORY)]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        papers = [
            ParsedPaper(
                category_raw=f"{CANONICAL_CATEGORY}_{download.category_code}",
                category_code=download.category_code,
                subject_code=_subject_code(download.url, download.label, f"download-{index}"),
                subject_name_raw=download.label,
                files={download.file_type: download.url},
            )
            for index, download in enumerate(self._downloads(), start=1)
        ]
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw=CANONICAL_CATEGORY,
            attachments=[],
            papers=papers,
            provider_id=self.provider_id,
        )

    def head(self, url: str) -> ResponseMetadata:
        request = Request(_quote_url_for_request(url), headers={"User-Agent": USER_AGENT}, method="HEAD")
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
        request = Request(_quote_url_for_request(url), headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=120) as response:
            return DownloadedFile(
                data=response.read(),
                content_type=response.headers.get("Content-Type", "application/octet-stream"),
                file_name=Path(unquote(urlparse(url).path)).name,
            )
