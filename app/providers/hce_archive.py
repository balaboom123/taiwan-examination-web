from __future__ import annotations

import re
import ssl
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from app.models import ExamOption, ParsedPaper, SourceExamPage
from app.providers.base import DownloadedFile, ResponseMetadata

USER_AGENT = "Mozilla/5.0 (compatible; hce-archive-mirror/1.0)"


@dataclass(frozen=True)
class HceYearPage:
    year_ad: int
    url: str

    @property
    def year_roc(self) -> int:
        return self.year_ad - 1911


@dataclass(frozen=True)
class HceArchiveConfig:
    provider_id: str
    canonical_slug: str
    listing_url: str
    exam_name: str
    category_code: str
    category_name: str
    subject_slugs: dict[str, str]
    listing_pattern: re.Pattern[str]
    combined_pdf_listing: bool = False

    def parse_listing(self, html: str) -> list[HceYearPage]:
        if self.combined_pdf_listing:
            return parse_combined_pdf_listing(html, self.listing_url, self)
        return parse_article_listing(html, self.listing_url, self)

    def parse_papers(self, html: str, base_url: str) -> list[ParsedPaper]:
        return parse_subject_file_page(html, base_url, self)


@dataclass
class _Link:
    label: str
    url: str


class _LinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.links: list[_Link] = []
        self._href = ""
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        self._href = dict(attrs).get("href", "") or ""
        self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._href:
            return
        self.links.append(_Link(_normalize_text(" ".join(self._text_parts)), urljoin(self.base_url, self._href)))
        self._href = ""
        self._text_parts = []


def _normalize_text(text: str) -> str:
    return " ".join(unescape(text).split())


def _links_from_html(html: str, base_url: str) -> list[_Link]:
    parser = _LinkParser(base_url)
    parser.feed(html)
    parser.close()
    return parser.links


def parse_article_listing(html: str, base_url: str, config: HceArchiveConfig) -> list[HceYearPage]:
    pages: list[HceYearPage] = []
    seen: set[int] = set()
    for link in _links_from_html(html, base_url):
        match = config.listing_pattern.search(link.label)
        if match is None:
            continue
        year_roc = int(match.group("year"))
        if year_roc in seen:
            continue
        seen.add(year_roc)
        pages.append(HceYearPage(year_ad=year_roc + 1911, url=link.url))
    return sorted(pages, key=lambda page: page.year_ad, reverse=True)


def parse_combined_pdf_listing(html: str, base_url: str, config: HceArchiveConfig) -> list[HceYearPage]:
    pages: list[HceYearPage] = []
    seen: set[int] = set()
    for link in _links_from_html(html, base_url):
        if not link.url.lower().endswith(".pdf"):
            continue
        match = config.listing_pattern.search(link.label) or config.listing_pattern.search(link.url)
        if match is None:
            continue
        year_roc = int(match.group("year"))
        if year_roc < 80 or year_roc > 199:
            continue
        if year_roc in seen:
            continue
        seen.add(year_roc)
        pages.append(HceYearPage(year_ad=year_roc + 1911, url=link.url))
    return sorted(pages, key=lambda page: page.year_ad, reverse=True)


def _candidate_file_url(link: _Link) -> bool:
    value = (link.url + " " + link.label).lower()
    return ".pdf" in value or "action=downloadfile" in value


def _asset_kind(label: str) -> tuple[str, str, str] | None:
    if "各科" in label and "答案" in label:
        return "all_answers", "all", "各科參考答案"
    if "答案" in label:
        return "answer", "", ""
    if "試題" in label:
        return "question", "", ""
    return None


def _subject_for(label: str, config: HceArchiveConfig) -> tuple[str, str] | None:
    for subject, slug in sorted(config.subject_slugs.items(), key=lambda item: len(item[0]), reverse=True):
        if subject in label:
            return slug, subject
    return None


def parse_subject_file_page(html: str, base_url: str, config: HceArchiveConfig) -> list[ParsedPaper]:
    grouped: dict[str, ParsedPaper] = {}
    for link in _links_from_html(html, base_url):
        if not _candidate_file_url(link):
            continue
        kind = _asset_kind(link.label)
        if kind is None:
            continue
        file_type, subject_code, subject_name = kind
        if subject_code != "all":
            subject = _subject_for(link.label, config)
            if subject is None:
                continue
            subject_code, subject_name = subject
        paper = grouped.setdefault(
            subject_code,
            ParsedPaper(
                category_raw=config.category_name,
                category_code=config.category_code,
                subject_code=subject_code,
                subject_name_raw=subject_name,
                files={},
            ),
        )
        paper.files[file_type] = link.url
    return list(grouped.values())


def _combined_pdf_paper(config: HceArchiveConfig, url: str) -> ParsedPaper:
    return ParsedPaper(
        category_raw=config.category_name,
        category_code=config.category_code,
        subject_code="all",
        subject_name_raw="各科試題與參考答案",
        files={"question_answer": url},
    )


def _ssl_context_for(url: str) -> ssl.SSLContext | None:
    host = urlparse(url).hostname or ""
    if host.endswith("cmu.edu.tw"):
        return ssl._create_unverified_context()
    return None


def _request_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            quote(parts.path, safe="/%"),
            quote(parts.query, safe="=&%"),
            parts.fragment,
        )
    )


def _fallback_file_name(url: str, content_disposition: str) -> str:
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?(?P<name>[^";]+)', content_disposition)
    if match is not None:
        return unquote(match.group("name"))
    name = Path(unquote(urlparse(url).path)).name
    return name if "." in name else "download.pdf"


class HceArchiveClient:
    def __init__(self, config: HceArchiveConfig) -> None:
        self.config = config
        self.provider_id = config.provider_id

    def _open(self, url: str, *, method: str = "GET", timeout: int = 60):
        request = Request(_request_url(url), headers={"User-Agent": USER_AGENT}, method=method)
        context = _ssl_context_for(url)
        if context is None:
            return urlopen(request, timeout=timeout)
        return urlopen(request, timeout=timeout, context=context)

    def _fetch_text(self, url: str) -> str:
        with self._open(url) as response:
            return response.read().decode("utf-8", "replace")

    def _year_pages(self) -> list[HceYearPage]:
        return self.config.parse_listing(self._fetch_text(self.config.listing_url))

    def discover_available_years(self) -> list[int]:
        return [page.year_ad for page in self._year_pages()]

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        return [
            ExamOption(
                code=f"{self.config.canonical_slug}-{page.year_roc}",
                year_ad=page.year_ad,
                year_roc=page.year_roc,
                label=f"{page.year_roc}學年度{self.config.exam_name}",
            )
            for page in self._year_pages()
            if page.year_ad == year_ad
        ]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        year_page = next(
            page
            for page in self._year_pages()
            if page.year_ad == year_ad and exam_code == f"{self.config.canonical_slug}-{page.year_roc}"
        )
        papers = (
            [_combined_pdf_paper(self.config, year_page.url)]
            if self.config.combined_pdf_listing
            else self.config.parse_papers(self._fetch_text(year_page.url), year_page.url)
        )
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_ad - 1911,
            exam_name_raw=f"{year_ad - 1911}學年度{self.config.exam_name}",
            attachments=[],
            papers=papers,
            provider_id=self.provider_id,
        )

    def head(self, url: str) -> ResponseMetadata:
        with self._open(url, method="HEAD") as response:
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
        with self._open(url, timeout=120) as response:
            content_disposition = response.headers.get("Content-Disposition", "")
            return DownloadedFile(
                data=response.read(),
                content_type=response.headers.get("Content-Type", "application/octet-stream"),
                file_name=_fallback_file_name(url, content_disposition),
            )


HCE_CONFIGS = {
    "hce_cmu": HceArchiveConfig(
        provider_id="hce_cmu",
        canonical_slug="hce-cmu",
        listing_url="https://adm21.cmu.edu.tw/?q=news_spbcm",
        exam_name="中國醫藥大學學士後中醫學系",
        category_code="post-bacc-chinese-medicine",
        category_name="中國醫藥大學學士後中醫學系",
        subject_slugs={"國文": "chinese", "化學": "chemistry", "英文": "english", "生物學": "biology"},
        listing_pattern=re.compile(r"(?P<year>\d{3})學年度學士後中醫學系.*試題及參考答案"),
    ),
    "hce_tcu": HceArchiveConfig(
        provider_id="hce_tcu",
        canonical_slug="hce-tcu",
        listing_url="https://admissions.tcu.edu.tw/?page_id=62",
        exam_name="慈濟大學學士後中醫學系",
        category_code="post-bacc-chinese-medicine",
        category_name="慈濟大學學士後中醫學系",
        subject_slugs={"國文": "chinese", "化學": "chemistry", "英文": "english", "生物學": "biology"},
        listing_pattern=re.compile(r"(?P<year>\d{3})學年度學士後中醫學系.*試題及參考答案"),
    ),
    "hce_nsysu": HceArchiveConfig(
        provider_id="hce_nsysu",
        canonical_slug="hce-nsysu",
        listing_url="https://lis.nsysu.edu.tw/p/412-1001-23442.php?Lang=zh-tw",
        exam_name="國立中山大學學士後醫學系",
        category_code="post-bacc-medicine",
        category_name="國立中山大學學士後醫學系",
        subject_slugs={},
        listing_pattern=re.compile(r"(?P<year>\d{3})(?:年|_|\.pdf)"),
        combined_pdf_listing=True,
    ),
    "hce_nthu": HceArchiveConfig(
        provider_id="hce_nthu",
        canonical_slug="hce-nthu",
        listing_url="https://adms.site.nthu.edu.tw/p/403-1207-6125-1.php?Lang=zh-tw",
        exam_name="國立清華大學學士後醫學系",
        category_code="post-bacc-medicine",
        category_name="國立清華大學學士後醫學系",
        subject_slugs={
            "英文": "english",
            "生物與生化": "biology-biochemistry",
            "化學與物理": "chemistry-physics",
            "資訊科學": "computer-science",
            "進階物理與線性代數": "advanced-physics-linear-algebra",
        },
        listing_pattern=re.compile(r"(?P<year>\d{3})學年度學士後醫學系.*各科試題及參考答案"),
    ),
}
