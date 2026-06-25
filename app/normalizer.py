from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import replace
from pathlib import Path
from typing import Iterable

from app.models import AliasRule, NormalizedCatalog, NormalizedPaper, ParsedPaper, ReviewItem

KNOWN_CANONICAL_IDS = {
    "護理師": "nurse",
    "社會工作師": "social-worker",
    "營養師": "dietitian",
    "心理師": "psychologist",
    "諮商心理師": "counseling-psychologist",
    "臨床心理師": "clinical-psychologist",
}

KNOWN_PREFIXES = [
    r"^專門職業及技術人員(?:高等|普通)?考試",
    r"^專技(?:高考|普考)",
    r"^高等考試",
    r"^普通考試",
    r"^特種考試",
]
_CEEC_GSAT_CANONICAL_ID = "ceec-gsat"
_CEEC_GSAT_CANONICAL_NAME = "學科能力測驗"

_MOEA_RECRUIT_CANONICAL_ID = "moea-recruit"
_MOEA_RECRUIT_CANONICAL_NAME = "國營事業聯招（新進職員）"
_TAIPOWER_RECRUIT_CANONICAL_ID = "taipower-recruit"
_TAIPOWER_RECRUIT_CANONICAL_NAME = "台電新進僱用人員甄試"
_CPC_RECRUIT_CANONICAL_ID = "cpc-recruit"
_CPC_RECRUIT_CANONICAL_NAME = "中油新進人員甄試"
_TWC_RECRUIT_CANONICAL_ID = "twc-recruit"
_TWC_RECRUIT_CANONICAL_NAME = "台水評價職位人員甄試"
_TAISUGAR_RECRUIT_CANONICAL_ID = "taisugar-recruit"
_TAISUGAR_RECRUIT_CANONICAL_NAME = "台糖新進工員甄試"

_SOE_CANONICAL_MAP = {
    "moea-recruit-": (_MOEA_RECRUIT_CANONICAL_ID, _MOEA_RECRUIT_CANONICAL_NAME),
    "taipower-recruit-": (_TAIPOWER_RECRUIT_CANONICAL_ID, _TAIPOWER_RECRUIT_CANONICAL_NAME),
    "cpc-recruit-": (_CPC_RECRUIT_CANONICAL_ID, _CPC_RECRUIT_CANONICAL_NAME),
    "twc-recruit-": (_TWC_RECRUIT_CANONICAL_ID, _TWC_RECRUIT_CANONICAL_NAME),
    "taisugar-recruit-": (_TAISUGAR_RECRUIT_CANONICAL_ID, _TAISUGAR_RECRUIT_CANONICAL_NAME),
}


def legacy_fallback_canonical_id(candidate: str) -> str:
    return "canonical-" + candidate.encode("utf-8").hex()[:16]


def hashed_fallback_canonical_id(candidate: str) -> str:
    normalized_candidate = normalize_text(candidate)
    digest = hashlib.sha256(normalized_candidate.encode("utf-8")).hexdigest()[:16]
    return f"canonical-{digest}"


def load_alias_rules(path: Path) -> list[AliasRule]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [AliasRule(**item) for item in payload.get("rules", [])]


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = normalized.replace("＿", "_")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _match_alias(rule: AliasRule, raw_category: str, year_ad: int) -> bool:
    if rule.year_from is not None and year_ad < rule.year_from:
        return False
    if rule.year_to is not None and year_ad > rule.year_to:
        return False
    if rule.match_type == "exact":
        return normalize_text(raw_category) == normalize_text(rule.raw_pattern)
    if rule.match_type == "contains":
        return normalize_text(rule.raw_pattern) in normalize_text(raw_category)
    raise ValueError(f"Unsupported alias match type: {rule.match_type}")


_VARIANT_LEVEL_SUFFIX = re.compile(
    r"[（(](?:三等|四等|五等|高考|普考|一等|二等|二級|一級|簡任|薦任|委任|一般組|兩岸組[一二三])[）)]"
)
_VARIANT_MILITARY_SUFFIX = re.compile(
    r"[（(](?:中將轉任考試|少將轉任考試|中將轉任|少將轉任|上校轉任|中將|少將)[）)]"
)
_VARIANT_DESTINATION_SUFFIX = re.compile(
    r"[（(](?:退輔會|轉任退輔會|國防部|轉任國防部|轉任海委會|一般錄取分發區|蘭嶼錄取分發區)[）)]"
)
_VARIANT_MILITARY_PREFIX = re.compile(
    r"^[（(](?:中將轉任|少將轉任|上校轉任)[）)]"
)
_VARIANT_EXAM_TYPE_PREFIX = re.compile(
    r"^[（(](?:關務類|技術類)[）)]"
)
_VARIANT_LANGUAGE_SUFFIX = re.compile(
    r"[（(]選試[^）)]+[）)]"
)
_VARIANT_TRAILING = re.compile(r"(?:類科|科別)$")


def _strip_exam_family(text: str) -> str:
    value = normalize_text(text)
    value = re.sub(r"^\d+年", "", value)
    if "_" in value:
        value = value.split("_")[-1]
    for prefix in KNOWN_PREFIXES:
        value = re.sub(prefix, "", value)
    value = re.sub(r"^第[一二三四五六七八九十]+次", "", value)
    value = re.sub(r"考試$", "", value)
    value = _VARIANT_TRAILING.sub("", value)
    value = _VARIANT_LEVEL_SUFFIX.sub("", value)
    value = _VARIANT_MILITARY_SUFFIX.sub("", value)
    value = _VARIANT_DESTINATION_SUFFIX.sub("", value)
    value = _VARIANT_LANGUAGE_SUFFIX.sub("", value)
    value = _VARIANT_MILITARY_PREFIX.sub("", value)
    value = _VARIANT_EXAM_TYPE_PREFIX.sub("", value)
    return value.strip(" -_")


def _is_ambiguous(candidate: str) -> bool:
    return any(token in candidate for token in ("、", "暨", "及", "與"))


def _canonical_id(candidate: str) -> str:
    if candidate in KNOWN_CANONICAL_IDS:
        return KNOWN_CANONICAL_IDS[candidate]
    return hashed_fallback_canonical_id(candidate)


def _derive_canonical(
    source_exam_id: str,
    raw_category: str,
    exam_name_raw: str,
    year_ad: int,
    alias_rules: list[AliasRule],
) -> tuple[str, str, str, bool]:
    """Return (canonical_id, canonical_name, stripped_candidate, needs_review)."""
    for prefix, (canonical_id, canonical_name) in _SOE_CANONICAL_MAP.items():
        if source_exam_id.startswith(prefix):
            return canonical_id, canonical_name, canonical_name, False
    if source_exam_id.startswith("gsat-") and _CEEC_GSAT_CANONICAL_NAME in normalize_text(raw_category or exam_name_raw):
        return _CEEC_GSAT_CANONICAL_ID, _CEEC_GSAT_CANONICAL_NAME, _CEEC_GSAT_CANONICAL_NAME, False
    alias = next((rule for rule in alias_rules if _match_alias(rule, raw_category, year_ad)), None)
    candidate = _strip_exam_family(raw_category or exam_name_raw)
    if alias:
        return alias.canonical_id, alias.canonical_name, candidate, False
    canonical_name = candidate or normalize_text(raw_category or exam_name_raw)
    if _is_ambiguous(canonical_name):
        canonical_name = normalize_text(raw_category or exam_name_raw)
        return _canonical_id(canonical_name), canonical_name, candidate, True
    return _canonical_id(canonical_name), canonical_name, candidate, False


def normalize_papers(
    source_exam_id: str,
    year_ad: int,
    exam_name_raw: str,
    papers: Iterable[ParsedPaper],
    alias_rules: list[AliasRule],
    mirror_base_url: str,
    mirror_metadata: dict[tuple[str, str, str], dict[str, str]],
) -> NormalizedCatalog:
    year_roc = year_ad - 1911
    normalized_papers: list[NormalizedPaper] = []
    review_queue: list[ReviewItem] = []
    for paper in papers:
        raw_category = paper.category_raw or exam_name_raw
        canonical_id, canonical_name, candidate, needs_review = _derive_canonical(source_exam_id, raw_category, exam_name_raw, year_ad, alias_rules)
        if needs_review:
            review_queue.append(
                ReviewItem(
                    raw_category=raw_category,
                    normalized_candidate=candidate or canonical_name,
                    source_exam_id=source_exam_id,
                    year_roc=year_roc,
                )
            )

        for file_type, download_url_source in paper.files.items():
            metadata = mirror_metadata.get((paper.category_code, paper.subject_code, file_type), {})
            storage_key = metadata.get("storage_key", "")
            asset_name = metadata.get("asset_name") or storage_key
            download_url_mirror = f"{mirror_base_url.rstrip('/')}/{asset_name}" if mirror_base_url and asset_name else ""
            normalized_papers.append(
                NormalizedPaper(
                    canonical_id=canonical_id,
                    canonical_name=canonical_name,
                    year_roc=year_roc,
                    exam_name_raw=exam_name_raw,
                    category_raw=paper.category_raw,
                    category_code=paper.category_code,
                    source_exam_id=source_exam_id,
                    subject_code=paper.subject_code,
                    subject_name_raw=paper.subject_name_raw,
                    paper_code=f"{paper.category_code}-{paper.subject_code}-{file_type}",
                    file_type=file_type,
                    download_url_source=download_url_source,
                    download_url_mirror=download_url_mirror,
                    storage_key=storage_key,
                    checksum=metadata.get("checksum", ""),
                )
            )
    return NormalizedCatalog(papers=normalized_papers, review_queue=review_queue)


def renormalize_catalog(catalog: NormalizedCatalog, alias_rules: list[AliasRule]) -> NormalizedCatalog:
    papers: list[NormalizedPaper] = []
    for paper in catalog.papers:
        raw_category = paper.category_raw or paper.exam_name_raw
        canonical_id, canonical_name, _, _ = _derive_canonical(paper.source_exam_id, raw_category, paper.exam_name_raw, paper.year_roc + 1911, alias_rules)
        if canonical_id != paper.canonical_id or canonical_name != paper.canonical_name:
            paper = replace(paper, canonical_id=canonical_id, canonical_name=canonical_name)
        papers.append(paper)
    return NormalizedCatalog(papers=papers, review_queue=catalog.review_queue)
