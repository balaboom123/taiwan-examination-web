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

DOWNLOAD_URL = "https://tocfl.edu.tw/tocfl/index.php/exam/download"
USER_AGENT = "Mozilla/5.0 (compatible; tocfl-cert-mirror/1.0)"
CANONICAL_CATEGORY = "TOCFL華語文能力測驗官方參考資料"
MATERIALS_YEAR = 2026


@dataclass(frozen=True)
class TocflDownload:
    label: str
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


def _slug(text: str, fallback: str) -> str:
    ascii_slug = re.sub(r"[^0-9A-Za-z]+", "-", text).strip("-").lower()
    if ascii_slug:
        return ascii_slug
    encoded = text.encode("utf-8").hex()[:24]
    return encoded or fallback


def parse_downloads(html: str, *, base_url: str = DOWNLOAD_URL) -> list[TocflDownload]:
    parser = _AnchorParser()
    parser.feed(html)
    downloads: list[TocflDownload] = []
    seen: set[str] = set()
    for label, href in parser.links:
        url = urljoin(base_url, href)
        if not url.lower().endswith((".pdf", ".zip")) or url in seen:
            continue
        seen.add(url)
        downloads.append(TocflDownload(label=label or Path(urlparse(url).path).name, url=url))
    return downloads


class TocflCertClient:
    provider_id = "tocfl_cert"

    def _fetch_text(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", "replace")

    def _downloads(self) -> list[TocflDownload]:
        return parse_downloads(self._fetch_text(DOWNLOAD_URL), base_url=DOWNLOAD_URL)

    def discover_available_years(self) -> list[int]:
        return [MATERIALS_YEAR]

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        if year_ad != MATERIALS_YEAR:
            return []
        return [ExamOption(code="tocfl-cert-materials", year_ad=year_ad, year_roc=year_ad - 1911, label="TOCFL官方參考資料")]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        papers = [
            ParsedPaper(
                category_raw=CANONICAL_CATEGORY,
                category_code="tocfl-reference",
                subject_code=_slug(download.label, f"download-{index}"),
                subject_name_raw=download.label,
                files={"question": download.url},
            )
            for index, download in enumerate(self._downloads(), start=1)
        ]
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw="TOCFL華語文能力測驗官方參考資料",
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
