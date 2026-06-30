# Provider Spec: `teacher_recruit_taipei_elementary`

## 1. Summary

- provider_id: `teacher_recruit_taipei_elementary`
- status: implemented
- owner: project crawler pipeline
- target site_id: `default`
- source family: Taipei city public elementary teacher joint recruitment

## 2. Source Overview

- source name: 臺北市公立國民小學教師聯合甄選公告
- source URL: `https://www.gov.taipei/News_Content.aspx?n=D0042A87C2F0270A&sms=78D644F2755ACCAA&s=0E5FFDCD602F05C2`
- source domain: `www.gov.taipei` with file downloads from `www-ws.gov.taipei`
- source type: public official article page plus direct `Download.ashx` PDF links
- source update cadence: annual recruitment announcement when Taipei publishes elementary teacher-selection papers
- source scope: current reviewed article, 114學年度 / AD 2025

The official article is published by 臺北市政府教育局國小教育科 and exposes 12 subject PDFs. Each PDF file name ends in `含答案`, so the provider stores them as combined `question_answer` files rather than trying to split questions and answers.

## 3. Stable Identity Model

- source exam id: `teacher-recruit-taipei-elementary-<roc_year>`
- canonical bundle id: `teacher-recruit-taipei-elementary`
- canonical name: `臺北市國小教師甄試`
- year semantics: source title uses school year; provider records AD year from the article map and ROC year as `year_ad - 1911`
- category semantics: all papers use `臺北市國小教師甄試`
- subject semantics: subject is decoded from the official download filename after removing leading sequence numbers and trailing `_含答案`

Known subject code mapping:

| source filename subject | subject_code |
|---|---|
| `基礎類科知能` | `basic-category-knowledge` |
| `普通科` | `general` |
| `英語科` | `english` |
| `體育科` | `physical-education` |
| `音樂科` | `music` |
| `視覺藝術科` | `visual-arts` |
| `輔導科` | `counseling` |
| `資訊科技科` | `information-technology` |
| `閩南語` | `taiwanese-minnan` |
| `特教科(身障)` | `special-education-disability` |
| `特教科(資優)` | `special-education-gifted` |
| `自然科` | `science` |

Unknown subjects fall back to a stable SHA-1 based `subject-<hash>` code.

## 4. Discovery Model

- available years are enumerated from an explicit official article map
- exams are one `ExamOption` per mapped year
- the provider does not crawl the general Taipei news listing because that listing is a city-wide announcement stream, not a teacher-paper archive
- add future years only after confirming the new official article exposes public `Download.ashx` paper PDFs

## 5. Download And Mirror Model

- mirror root: `mirror/providers/teacher_recruit_taipei_elementary/`
- provider data root: `data/providers/teacher_recruit_taipei_elementary/`
- mirror key pattern: `providers/teacher_recruit_taipei_elementary/<roc_year>/<source_exam_id>/<category_code>/<subject_code>/question_answer.pdf`
- expected file type: PDF
- validation: existing `question_answer` extension validation accepts `.pdf`, `.zip`, and `.rar`; this provider should normally mirror `.pdf`
- filename decoding: prefer the base64 `n` query parameter, fall back to base64 `u` path, then URL path basename

## 6. Normalization Contract

- source prefix `teacher-recruit-taipei-elementary-` maps to canonical id `teacher-recruit-taipei-elementary`
- canonical display name is `臺北市國小教師甄試`
- public feed inclusion uses `public_min_years_by_canonical_prefix["teacher-recruit-taipei-elementary"] = 1`
- no provider-specific fields leak into public feeds

## 7. CI/CD Plan

- workflow: `.github/workflows/sync-teacher-recruit-taipei-elementary.yml`
- schedule: Tuesday `05:55` UTC, provider-only refresh
- command: `python -m app sync-full --provider teacher_recruit_taipei_elementary --site-id default`
- no direct `publish-site`, LootLabs sync, or release upload in the provider-only workflow

## 8. Operator Runbook

Standard crawl:

```powershell
uv run python -m app sync-full --provider teacher_recruit_taipei_elementary --site-id default
```

Verification:

```powershell
uv run python -m pytest -q tests/test_teacher_recruit_taipei_elementary.py tests/test_normalizer.py tests/test_site_registry.py tests/test_workflows.py
```

Expected generated outputs:

- `data/providers/teacher_recruit_taipei_elementary/exams/2025.json`
- `data/providers/teacher_recruit_taipei_elementary/papers/2025.json`
- `data/providers/teacher_recruit_taipei_elementary/aliases.json`
- `data/providers/teacher_recruit_taipei_elementary/review-queue.json`
- `data/providers/teacher_recruit_taipei_elementary/sync-failures.json`
- mirror PDFs under `mirror/providers/teacher_recruit_taipei_elementary/`
- refreshed default site bundle metadata after `--site-id default`

## 9. Recovery Scenarios

- source unavailable: keep prior provider state; rerun after official site recovers
- article removed or schema drift: parser tests should be updated only after a new official article surface is reviewed
- invalid payload or HTML placeholder: existing sync validation rejects non-PDF payloads for `question_answer`
- future-year article found: add the official article URL to `ARTICLE_URLS_BY_YEAR`, add a fixture test, then crawl

## 10. Testing Plan

- parser test decodes `Download.ashx` base64 filenames
- parser test keeps only `含答案` PDFs and skips ODT appeal files
- client test emits one `SourceExamPage` with one `question_answer` paper per subject
- normalizer test maps `teacher-recruit-taipei-elementary-*` to the stable canonical bundle
- site registry test includes the provider and public minimum-year override
- workflow test confirms provider-only scheduled sync

## 11. Scope Notes

This provider is current-year scoped. It improves official 教甄 coverage but does not change the product claim that 教甄 remains scattered by county, city, recruitment committee, and school.
