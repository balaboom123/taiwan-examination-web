from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.parse import unquote, urlencode, urljoin, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

from app.models import ExamOption, ParsedPaper, SourceExamPage
from app.providers.base import DownloadedFile, ResponseMetadata

BASE_URL = "https://tqa.rcpet.edu.tw/TEA_Exam/"
LISTING_URL = urljoin(BASE_URL, "TEA03.aspx")
USER_AGENT = "Mozilla/5.0 (compatible; teacher-qual-mirror/1.0)"
CANONICAL_CATEGORY = "教師資格考試"
ALL_SUBJECT_CODE = "all-categories"
ALL_SUBJECT_NAME = "全部類科試題及參考答案"


@dataclass(frozen=True)
class TeacherQualDownload:
    label: str
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


class _SelectParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.selects: dict[str, list[tuple[str, str]]] = {}
        self._select_name = ""
        self._option_value: str | None = None
        self._option_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "select":
            self._select_name = attrs_dict.get("name") or attrs_dict.get("id") or ""
            return
        if tag == "option" and self._select_name:
            self._option_value = attrs_dict.get("value", "") or ""
            self._option_parts = []

    def handle_data(self, data: str) -> None:
        if self._option_value is not None:
            self._option_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "option" and self._select_name and self._option_value is not None:
            label = _normalize_text("".join(self._option_parts))
            self.selects.setdefault(self._select_name, []).append((self._option_value, label))
            self._option_value = None
            self._option_parts = []
            return
        if tag == "select":
            self._select_name = ""


def _select_options(html: str, name: str) -> list[tuple[str, str]]:
    parser = _SelectParser()
    parser.feed(html)
    return [(value, label) for value, label in parser.selects.get(name, []) if value]


def parse_available_years(html: str) -> list[int]:
    years: list[int] = []
    for value, _label in _select_options(html, "ctl00$ContentPlaceHolder1$schyy"):
        if value.isdigit():
            years.append(int(value) + 1911)
    return sorted(dict.fromkeys(years), reverse=True)


def parse_subject_options(html: str) -> list[tuple[str, str]]:
    return _select_options(html, "ctl00$ContentPlaceHolder1$exid")


def parse_downloads(html: str, *, year_roc: int) -> list[TeacherQualDownload]:
    parser = _TokenParser()
    parser.feed(html)
    downloads: list[TeacherQualDownload] = []
    context: list[str] = []
    in_year_section = False
    year_heading = f"{year_roc}年試題及參考答案"
    for token_type, token_text, token_href in parser.tokens:
        if token_type == "text":
            if token_text == year_heading:
                in_year_section = True
                context = [token_text]
                continue
            if token_text == "樣卷":
                in_year_section = False
                context = []
                continue
            if in_year_section:
                context.append(token_text)
                context = context[-4:]
            continue
        if not in_year_section or "ShowPicOut2.aspx" not in token_href:
            continue
        label = _normalize_text(" ".join(context))
        if not label:
            label = ALL_SUBJECT_NAME
        downloads.append(TeacherQualDownload(label=label, url=urljoin(BASE_URL, token_href)))
    return downloads


def _hidden_fields(html: str) -> dict[str, str]:
    return dict(
        re.findall(
            r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"',
            html,
        )
    )


class TeacherQualClient:
    provider_id = "teacher_qual"

    def _fetch_text(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            raw = response.read()
        for encoding in ("utf-8-sig", "utf-16", "utf-8", "big5", "cp950"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", "replace")

    def _listing_for_year(self, year_roc: int) -> str:
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        headers = {"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"}

        def fetch(data: dict[str, str] | None = None) -> str:
            body = urlencode(data).encode("utf-8") if data is not None else None
            request = Request(LISTING_URL, data=body, headers=headers)
            with opener.open(request, timeout=60) as response:
                return response.read().decode("utf-8", "replace")

        initial_html = fetch()
        year_html = fetch(
            {
                **_hidden_fields(initial_html),
                "__EVENTTARGET": "ctl00$ContentPlaceHolder1$schyy",
                "__EVENTARGUMENT": "",
                "ctl00$ContentPlaceHolder1$schyy": f"{year_roc:03d}",
                "ctl00$ContentPlaceHolder1$exid": "",
            }
        )
        subjects = parse_subject_options(year_html)
        selected_subject = "99" if any(value == "99" for value, _label in subjects) else (subjects[0][0] if subjects else "")
        if not selected_subject:
            return year_html
        return fetch(
            {
                **_hidden_fields(year_html),
                "__EVENTTARGET": "ctl00$ContentPlaceHolder1$exid",
                "__EVENTARGUMENT": "",
                "ctl00$ContentPlaceHolder1$schyy": f"{year_roc:03d}",
                "ctl00$ContentPlaceHolder1$exid": selected_subject,
            }
        )

    def discover_available_years(self) -> list[int]:
        return parse_available_years(self._fetch_text(LISTING_URL))

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        if year_ad not in self.discover_available_years():
            return []
        year_roc = year_ad - 1911
        return [
            ExamOption(
                code=f"teacher-qual-{year_roc}",
                year_ad=year_ad,
                year_roc=year_roc,
                label=f"{year_roc}年教師資格考試歷屆試題及參考答案",
            )
        ]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        year_roc = year_ad - 1911
        downloads = parse_downloads(self._listing_for_year(year_roc), year_roc=year_roc)
        papers = [
            ParsedPaper(
                category_raw=CANONICAL_CATEGORY,
                category_code=str(year_roc),
                subject_code=ALL_SUBJECT_CODE,
                subject_name_raw=download.label or ALL_SUBJECT_NAME,
                files={"question": download.url},
            )
            for download in downloads
        ]
        return SourceExamPage(
            source_exam_id=exam_code,
            year_ad=year_ad,
            year_roc=year_roc,
            exam_name_raw=f"{year_roc}年教師資格考試歷屆試題及參考答案",
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
