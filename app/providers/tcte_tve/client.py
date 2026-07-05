from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from app.models import ExamOption, ParsedPaper, SourceExamPage
from app.providers.base import DownloadedFile, ResponseMetadata

LISTING_URL = "https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y"
USER_AGENT = "Mozilla/5.0 (compatible; tcte-tve-mirror/1.0)"
_YEAR_PAGE_RE = re.compile(r"/EXAM/(?P<roc_year>\d{2,3})_4y/?(?:\?|$)")
_ONCLICK_RE = re.compile(r"location\.href=['\"](?P<href>[^'\"]+)['\"]")
_TCTE_CATEGORY_NAME = "四技二專統一入學測驗"
_COMMON_SUBJECT_SLUGS = {
    "國文科": "chinese",
    "英文科": "english",
    "數學(A)": "math-a",
    "數學(B)": "math-b",
    "數學(C)": "math-c",
}


@dataclass(frozen=True)
class TcteYearPage:
    year_ad: int
    url: str

    @property
    def year_roc(self) -> int:
        return self.year_ad - 1911

    @property
    def code(self) -> str:
        return f"tcte-tve-{self.year_roc}"


@dataclass
class _Cell:
    text_parts: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return _normalize_text(" ".join(self.text_parts))


class _LinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href", "") or ""
        if href:
            self.links.append(urljoin(self.base_url, href))


class _TableParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.rows: list[list[_Cell]] = []
        self._row: list[_Cell] | None = None
        self._cell: _Cell | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._close_row()
            self._row = []
            return
        if tag in {"td", "th"} and self._row is not None:
            self._close_cell()
            self._cell = _Cell()
            return
        if tag == "input" and self._cell is not None:
            onclick = dict(attrs).get("onclick", "") or ""
            match = _ONCLICK_RE.search(onclick)
            if match is not None:
                self._cell.links.append(urljoin(self.base_url, match.group("href")))

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"}:
            self._close_cell()
        elif tag == "tr":
            self._close_row()

    def close(self) -> None:
        self._close_row()
        super().close()

    def _close_cell(self) -> None:
        if self._row is not None and self._cell is not None:
            self._row.append(self._cell)
        self._cell = None

    def _close_row(self) -> None:
        self._close_cell()
        if self._row is not None and self._row:
            self.rows.append(self._row)
        self._row = None


def _normalize_text(text: str) -> str:
    return " ".join(unescape(text).split())


def _plain_text_from_html(html: str) -> str:
    return _normalize_text(re.sub(r"<[^>]+>", " ", html))


def _category_code(group: str) -> str:
    if group == "共同科目":
        return "common"
    match = re.match(r"(?P<code>\d{2})", group)
    if match is not None:
        return match.group("code")
    return "group-" + group.encode("utf-8").hex()[:8]


def _subject_slug(subject: str) -> str:
    if subject in _COMMON_SUBJECT_SLUGS:
        return _COMMON_SUBJECT_SLUGS[subject]
    if "一" in subject:
        return "professional-1"
    if "二" in subject:
        return "professional-2"
    ascii_slug = re.sub(r"[^0-9A-Za-z]+", "-", subject).strip("-").lower()
    if ascii_slug:
        return ascii_slug
    return "subject-" + subject.encode("utf-8").hex()[:12]


def parse_listing_page(html: str) -> list[TcteYearPage]:
    parser = _LinkParser(LISTING_URL)
    parser.feed(html)
    pages: list[TcteYearPage] = []
    seen: set[int] = set()
    for url in parser.links:
        match = _YEAR_PAGE_RE.search(url)
        if match is None:
            continue
        year_roc = int(match.group("roc_year"))
        if year_roc in seen:
            continue
        seen.add(year_roc)
        pages.append(TcteYearPage(year_ad=year_roc + 1911, url=url.split("?")[0].rstrip("/")))
    return sorted(pages, key=lambda page: page.year_ad, reverse=True)


def parse_year_page(html: str, base_url: str) -> list[ParsedPaper]:
    parser = _TableParser(base_url)
    parser.feed(html)
    parser.close()
    papers: list[ParsedPaper] = []
    current_group = ""
    for row in parser.rows:
        cells = [cell for cell in row if cell.text or cell.links]
        if len(cells) < 3:
            continue
        first_text = cells[0].text
        has_group = first_text == "共同科目" or re.match(r"^\d{2}", first_text) is not None
        if has_group and len(cells) >= 4:
            current_group = first_text
            subject, question_cell, answer_cell = cells[1], cells[2], cells[3]
        else:
            subject, question_cell, answer_cell = cells[0], cells[1], cells[2]
        if not current_group or not question_cell.links:
            continue
        subject_name = subject.text
        files = {"question": question_cell.links[0]}
        if len(question_cell.links) > 1:
            files["question_alt"] = question_cell.links[1]
        if answer_cell.links:
            files["answer"] = answer_cell.links[0]
        code = _category_code(current_group)
        papers.append(
            ParsedPaper(
                category_raw=_TCTE_CATEGORY_NAME,
                category_code=code,
                subject_code=_subject_slug(subject_name),
                subject_name_raw=f"{current_group} {subject_name}",
                files=files,
            )
        )
    return papers


class TcteTveClient:
    provider_id = "tcte_tve"

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

    def _year_pages(self) -> list[TcteYearPage]:
        return parse_listing_page(self._fetch_text(LISTING_URL))

    def discover_available_years(self) -> list[int]:
        return [page.year_ad for page in self._year_pages()]

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        return [
            ExamOption(
                code=page.code,
                year_ad=page.year_ad,
                year_roc=page.year_roc,
                label=f"{page.year_roc}學年度四技二專統一入學測驗",
            )
            for page in self._year_pages()
            if page.year_ad == year_ad
        ]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        year_page = next(page for page in self._year_pages() if page.code == exam_code and page.year_ad == year_ad)
        exam_name = f"{year_page.year_roc}學年度四技二專統一入學測驗"
        return SourceExamPage(
            source_exam_id=year_page.code,
            year_ad=year_ad,
            year_roc=year_page.year_roc,
            exam_name_raw=exam_name,
            attachments=[],
            papers=parse_year_page(self._fetch_text(year_page.url + "/"), year_page.url + "/"),
            provider_id=self.provider_id,
        )
