from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from app.models import ExamOption, ParsedPaper, SourceExamPage
from app.providers.base import DownloadedFile, ResponseMetadata

BASE_URL = "https://www.tabf.org.tw/"
USER_AGENT = "Mozilla/5.0 (compatible; tabf-cert-mirror/1.0)"


class TabfCertClient:
    provider_id = "tabf_cert"

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

    def discover_available_years(self) -> list[int]:
        raise NotImplementedError("TABF client requires web research — see design spec")

    def discover_exams(self, year_ad: int) -> list[ExamOption]:
        raise NotImplementedError("TABF client requires web research — see design spec")

    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage:
        raise NotImplementedError("TABF client requires web research — see design spec")
