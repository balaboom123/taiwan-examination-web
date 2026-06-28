from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlparse, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from app.models import ExamOption, ParsedPaper, SourceExamPage
from app.providers.base import DownloadedFile, ResponseMetadata

USER_AGENT = "Mozilla/5.0 (compatible; ipas-cert-mirror/1.0)"
CANONICAL_CATEGORY = "iPAS產業人才能力鑑定官方下載"
MATERIALS_YEAR = 2026


@dataclass(frozen=True)
class IpasDownload:
    cert_code: str
    label: str
    url: str


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


def parse_certification_codes(html: str) -> list[str]:
    codes = set(re.findall(r"/certification/([A-Z0-9]+)/news", html))
    return sorted(codes)


def parse_pdf_downloads(html: str, *, cert_code: str = "") -> list[IpasDownload]:
    urls = sorted(set(re.findall(r"https://www\.ipas\.org\.tw/api/proxy/uploads/[^\"'<>]+?\.pdf", html)))
    downloads: list[IpasDownload] = []
    for url in urls:
        label = Path(unquote(urlparse(url).path)).name
        downloads.append(IpasDownload(cert_code=cert_code, label=label, url=_quote_url_for_request(url)))
    return downloads


class IpasCertClient:
    provider_id = "ipas_cert"
    HOME_URL = "https://www.ipas.org.tw/"

    def _fetch_text(self, url: str) -> str:
        request = Request(_quote_url_for_request(url), headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", "replace")

    def _downloads(self) -> list[IpasDownload]:
        codes = parse_certification_codes(self._fetch_text(self.HOME_URL))
        downloads: list[IpasDownload] = []
        for code in codes:
            html = self._fetch_text(f"https://www.ipas.org.tw/certification/{code}/downloads")
            downloads.extend(parse_pdf_downloads(html, cert_code=code))
        return downloads

    def discover_available_years(self) -> list[int]:
        return [MATERIALS_YEAR]

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        if year_ad != MATERIALS_YEAR:
            return []
        return [ExamOption(code="ipas-cert-downloads", year_ad=year_ad, year_roc=year_ad - 1911, label="iPAS官方下載")]

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        papers = [
            ParsedPaper(
                category_raw=f"{CANONICAL_CATEGORY}_{download.cert_code}",
                category_code=download.cert_code.lower(),
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
            exam_name_raw="iPAS產業人才能力鑑定官方下載",
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
