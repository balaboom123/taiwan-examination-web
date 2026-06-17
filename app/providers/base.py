from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.models import ExamOption, SourceExamPage


@dataclass
class DownloadedFile:
    data: bytes
    content_type: str
    file_name: str


@dataclass
class ResponseMetadata:
    url: str
    status: int
    content_length: int | None = None
    content_type: str = ""
    content_disposition: str = ""
    cache_control: str = ""


@runtime_checkable
class SourceProvider(Protocol):
    provider_id: str

    def discover_available_years(self) -> list[int]: ...
    def discover_exams(self, year_ad: int) -> list[ExamOption]: ...
    def fetch_exam_page(self, exam_code: str, year_ad: int) -> SourceExamPage: ...
    def head(self, url: str) -> ResponseMetadata: ...
    def download_file(self, url: str) -> DownloadedFile: ...
