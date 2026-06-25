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

BASE_URL = "https://cap.rcpet.edu.tw/"
MAIN_PAGE_URL = "https://cap.rcpet.edu.tw/examination.html"
USER_AGENT = "Mozilla/5.0 (compatible; rcpet-cap-mirror/1.0)"
_CAP_CANONICAL_NAME = "國中教育會考"

_GDRIVE_FILE_RE = re.compile(r"https?://drive\.google\.com/file/d/([^/]+)/")


def _resolve_gdrive_url(url: str) -> str:
    m = _GDRIVE_FILE_RE.match(url)
    if m:
        return f"https://drive.google.com/uc?id={m.group(1)}&export=download"
    return url

_SUBJECT_MAP: dict[str, tuple[str, str]] = {
    "寫作測驗": ("writing", "question"),
    "國文科": ("chinese", "question"),
    "英語科": ("english-reading", "question"),
    "英語（閱讀）": ("english-reading", "question"),
    "英語（聽力）": ("english-listening", "question"),
    "英語科聽力語音檔(壓縮檔)-備註": ("english-listening", "question"),
    "英語科聽力語音檔(mp3)-備註": ("english-listening", "question"),
    "數學科": ("math", "question"),
    "社會科": ("social", "question"),
    "自然科": ("science", "question"),
    "參考答案": ("all-subjects", "answer"),
    "試題說明": ("all-subjects", "question_alt"),
}

_SKIP_LABELS = re.compile(
    r"國中教育會考各科等級|各等級類別|各科計分與閱卷|試題疑義|無浮水印題本|各題通過率|各題鑑別度|數學非選擇題|寫作測驗各級分"
)

_OPTION_VALUE_RE = re.compile(r"^exam/(\d{3}c?)/")
_ROC_YEAR_RE = re.compile(r"^(\d{3})年")


@dataclass(frozen=True)
class DropdownEntry:
    year_dir: str
    page_url: str
    label: str
    year_roc: int
    year_ad: int


class _DropdownParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_select = False
        self._in_option = False
        self._option_value = ""
        self._option_text_parts: list[str] = []
        self.entries: list[DropdownEntry] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "select" and attrs_dict.get("id") == "exam":
            self._in_select = True
            return
        if tag == "option" and self._in_select:
            self._in_option = True
            self._option_value = attrs_dict.get("value", "")
            self._option_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_option:
            self._option_text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "select" and self._in_select:
            self._in_select = False
            return
        if tag == "option" and self._in_option:
            self._in_option = False
            label = " ".join("".join(self._option_text_parts).split())
            value = self._option_value
            match = _OPTION_VALUE_RE.match(value)
            if not match:
                return
            year_dir = match.group(1)
            roc_match = _ROC_YEAR_RE.match(label)
            if not roc_match:
                return
            year_roc = int(roc_match.group(1))
            self.entries.append(
                DropdownEntry(
                    year_dir=year_dir,
                    page_url=value,
                    label=label,
                    year_roc=year_roc,
                    year_ad=year_roc + 1911,
                )
            )


class _YearPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_ul = False
        self._ul_depth = 0
        self._in_li = False
        self._in_anchor = False
        self._anchor_href = ""
        self._anchor_text_parts: list[str] = []
        self._title_parts: list[str] = []
        self._in_h1 = False
        self.title = ""
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h1":
            self._in_h1 = True
            self._title_parts = []
            return
        if tag == "ul" and not self._in_ul:
            self._in_ul = True
            self._ul_depth = 1
            return
        if tag == "ul" and self._in_ul:
            self._ul_depth += 1
            return
        if tag == "li" and self._in_ul:
            self._in_li = True
            return
        if tag == "a" and self._in_li:
            self._in_anchor = True
            self._anchor_href = dict(attrs).get("href", "") or ""
            self._anchor_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_h1:
            self._title_parts.append(data)
        if self._in_anchor:
            self._anchor_text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1" and self._in_h1:
            self._in_h1 = False
            self.title = " ".join("".join(self._title_parts).split())
            return
        if tag == "ul" and self._in_ul:
            self._ul_depth -= 1
            if self._ul_depth == 0:
                self._in_ul = False
            return
        if tag == "li" and self._in_li:
            self._in_li = False
            return
        if tag == "a" and self._in_anchor:
            self._in_anchor = False
            label = " ".join("".join(self._anchor_text_parts).split())
            if label and self._anchor_href:
                self.links.append((label, self._anchor_href))


def parse_dropdown(html: str) -> list[DropdownEntry]:
    parser = _DropdownParser()
    parser.feed(unescape(html))
    return parser.entries


def parse_year_page(html: str, year_roc: int, base_url: str = "", year_dir: str = "") -> SourceExamPage:
    parser = _YearPageParser()
    parser.feed(unescape(html))

    year_ad = year_roc + 1911
    effective_dir = year_dir or str(year_roc)
    source_exam_id = f"cap-{effective_dir}"
    papers: list[ParsedPaper] = []

    for label, href in parser.links:
        if _SKIP_LABELS.search(label):
            continue

        mapping = _SUBJECT_MAP.get(label)
        if mapping is None:
            continue

        subject_slug, file_type = mapping
        url = urljoin(base_url, href) if base_url else href

        papers.append(
            ParsedPaper(
                category_raw=_CAP_CANONICAL_NAME,
                category_code=effective_dir,
                subject_code=subject_slug,
                subject_name_raw=label,
                files={file_type: url},
            )
        )

    return SourceExamPage(
        source_exam_id=source_exam_id,
        year_ad=year_ad,
        year_roc=year_roc,
        exam_name_raw=parser.title or f"{year_roc}年國中教育會考",
        attachments=[],
        papers=papers,
        provider_id="rcpet_cap",
    )


class RcpetCapClient:
    provider_id = "rcpet_cap"

    def _fetch_text(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", "replace")

    def head(self, url: str) -> ResponseMetadata:
        url = _resolve_gdrive_url(url)
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
        url = _resolve_gdrive_url(url)
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=120) as response:
            return DownloadedFile(
                data=response.read(),
                content_type=response.headers.get("Content-Type", "application/octet-stream"),
                file_name=Path(unquote(urlparse(url).path)).name,
            )

    def _get_dropdown_entries(self) -> list[DropdownEntry]:
        html = self._fetch_text(MAIN_PAGE_URL)
        return parse_dropdown(html)

    def discover_available_years(self) -> list[int]:
        entries = self._get_dropdown_entries()
        return sorted({e.year_ad for e in entries}, reverse=True)

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        entries = self._get_dropdown_entries()
        return [
            ExamOption(
                code=f"cap-{e.year_dir}",
                year_ad=e.year_ad,
                year_roc=e.year_roc,
                label=e.label,
            )
            for e in entries
            if e.year_ad == year_ad
        ]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        entries = self._get_dropdown_entries()
        entry = next(
            (e for e in entries if f"cap-{e.year_dir}" == exam_code and e.year_ad == year_ad),
            None,
        )
        if entry is None:
            return SourceExamPage(
                source_exam_id=exam_code,
                year_ad=year_ad,
                year_roc=year_ad - 1911,
                exam_name_raw="",
                attachments=[],
                papers=[],
                provider_id=self.provider_id,
            )

        page_url = urljoin(BASE_URL, entry.page_url)
        html = self._fetch_text(page_url)
        return parse_year_page(html, year_roc=entry.year_roc, base_url=page_url, year_dir=entry.year_dir)
