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

BASE_URL = "https://www.taipower.com.tw/"
DOWNLOAD_URL = "https://www.taipower.com.tw/tc/download.aspx?mid=261"
USER_AGENT = "Mozilla/5.0 (compatible; moea-recruit-mirror/1.0)"
CANONICAL_CATEGORY = "國營事業聯招（新進職員）"
_YEAR_RE = re.compile(r"(\d{2,3})\s*年")


@dataclass(frozen=True)
class MoeaRecruitDownload:
    label: str
    url: str


@dataclass(frozen=True)
class MoeaRecruitEntry:
    year_roc: int
    year_ad: int
    title: str
    downloads: list[MoeaRecruitDownload]


def _normalize_text(text: str) -> str:
    return " ".join(unescape(text).split())


class _DownloadPageParser(HTMLParser):
    """Parse the Taipower download listing page.

    Expected structure:
      <div class="download-list">
        <div class="list-item">
          <div class="title">NNN年...</div>
          <div class="file">
            <a href="/media/...">label</a>
            ...
          </div>
        </div>
        ...
      </div>
    """

    def __init__(self) -> None:
        super().__init__()
        self._in_download_list = False
        self._in_list_item = False
        self._in_title = False
        self._in_file = False
        self._in_anchor = False
        # Depth counters for nested div tracking
        self._div_depth_title: int = 0
        self._div_depth_file: int = 0
        self._div_depth_item: int = 0
        self._div_depth_list: int = 0
        self._current_title: str = ""
        self._title_parts: list[str] = []
        self._current_href: str = ""
        self._anchor_parts: list[str] = []
        self._current_downloads: list[MoeaRecruitDownload] = []
        self.entries: list[MoeaRecruitEntry] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = (attrs_dict.get("class") or "").split()

        if tag == "div" and "download-list" in classes:
            self._in_download_list = True
            self._div_depth_list = 1
            return

        if not self._in_download_list:
            return

        if tag == "div" and "list-item" in classes:
            self._in_list_item = True
            self._div_depth_item = 1
            self._current_title = ""
            self._current_downloads = []
            return

        if not self._in_list_item:
            return

        if tag == "div" and "title" in classes:
            self._in_title = True
            self._div_depth_title = 1
            self._title_parts = []
            return

        if tag == "div" and "file" in classes:
            self._in_file = True
            self._div_depth_file = 1
            return

        # Handle nested divs within tracked sections
        if tag == "div":
            if self._in_title:
                self._div_depth_title += 1
            elif self._in_file:
                self._div_depth_file += 1
            elif self._in_list_item:
                self._div_depth_item += 1
            elif self._in_download_list:
                self._div_depth_list += 1

        if self._in_file and tag == "a":
            self._in_anchor = True
            self._current_href = attrs_dict.get("href") or ""
            self._anchor_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        elif self._in_anchor:
            self._anchor_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "div":
            if self._in_title:
                self._div_depth_title -= 1
                if self._div_depth_title == 0:
                    self._current_title = _normalize_text("".join(self._title_parts))
                    self._in_title = False
                return
            if self._in_file:
                self._div_depth_file -= 1
                if self._div_depth_file == 0:
                    self._in_file = False
                return
            if self._in_list_item:
                self._div_depth_item -= 1
                if self._div_depth_item == 0:
                    # Closing a list-item: flush the entry
                    self._flush_entry()
                    self._in_list_item = False
                return
            if self._in_download_list:
                self._div_depth_list -= 1
                if self._div_depth_list == 0:
                    self._in_download_list = False
                return

        if tag == "a" and self._in_anchor:
            label = _normalize_text("".join(self._anchor_parts))
            if label and self._current_href:
                url = urljoin(BASE_URL, self._current_href)
                self._current_downloads.append(MoeaRecruitDownload(label=label, url=url))
            self._in_anchor = False
            self._anchor_parts = []
            self._current_href = ""

    def _flush_entry(self) -> None:
        title = self._current_title
        if not title or not self._current_downloads:
            return
        match = _YEAR_RE.search(title)
        if match is None:
            return
        year_roc = int(match.group(1))
        self.entries.append(
            MoeaRecruitEntry(
                year_roc=year_roc,
                year_ad=year_roc + 1911,
                title=title,
                downloads=list(self._current_downloads),
            )
        )


def parse_download_page(html: str) -> list[MoeaRecruitEntry]:
    """Parse the Taipower MOEA joint exam download listing page."""
    parser = _DownloadPageParser()
    parser.feed(html)
    return parser.entries


class MoeaRecruitClient:
    provider_id = "moea_recruit"

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

    def _iter_entries(self) -> list[MoeaRecruitEntry]:
        html = self._fetch_text(DOWNLOAD_URL)
        return parse_download_page(html)

    def discover_available_years(self) -> list[int]:
        return sorted({entry.year_ad for entry in self._iter_entries()}, reverse=True)

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        return [
            ExamOption(
                code=f"moea-recruit-{entry.year_roc}",
                year_ad=entry.year_ad,
                year_roc=entry.year_roc,
                label=entry.title,
            )
            for entry in self._iter_entries()
            if entry.year_ad == year_ad
        ]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        entry = next(
            item for item in self._iter_entries()
            if f"moea-recruit-{item.year_roc}" == exam_code and item.year_ad == year_ad
        )
        papers: list[ParsedPaper] = []
        for index, download in enumerate(entry.downloads, start=1):
            if "答案" in download.label or "解答" in download.label:
                file_type = "answer"
            else:
                file_type = "question"
            papers.append(
                ParsedPaper(
                    category_raw=CANONICAL_CATEGORY,
                    category_code=str(entry.year_roc),
                    subject_code=f"joint-{index:02d}",
                    subject_name_raw=download.label,
                    files={file_type: download.url},
                )
            )
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=entry.year_roc,
            exam_name_raw=entry.title,
            attachments=[],
            papers=papers,
            provider_id=self.provider_id,
        )
