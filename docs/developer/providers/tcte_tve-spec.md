# Provider Spec: `tcte_tve`

## Summary

- `provider_id`: `tcte_tve`
- status: implemented
- target site: `default`
- source family: Testing Center for Technological and Vocational Education 四技二專統一入學測驗 archive
- Shuati bucket: `/exams/tve`
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

- source domain: `www.tcte.edu.tw`
- source page: `https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y`
- yearly paper pages: `https://web1.tcte.edu.tw/EXAM/<roc_year>_4y/`
- source access: public web pages plus linked Word/PDF files
- source cadence: yearly archive updates after the exam and answer-confirmation process
- authentication: none
- rate-limit posture: conservative scheduled sync; fetch listing pages and direct links only

TCTE lists yearly rows for 四技二專報名人數、簡章、試題 and links to each year's "試題答案及組距" page.

## Discovery Model

The provider crawls the year table, follows each year's paper page, and mirrors question and standard-answer assets for common subjects and group/category professional subjects.

Provider-owned outputs live under:

- `data/providers/tcte_tve/`
- `mirror/providers/tcte_tve/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-tcte-tve.yml`

The primary operator command is:

```bash
python -m app sync-full --provider tcte_tve --site-id default
```

## Implementation Status

- provider package: `app/providers/tcte_tve/`
- focused tests: `tests/test_tcte_tve.py`
- published bundle: `tcte-tve`
- local synced coverage: ROC 92-115 / AD 2003-2026, 2,956 normalized paper records
- ROC 90-91 raw pages remain retained but outside normalized paper scope: the documented direct pages `https://web1.tcte.edu.tw/EXAM/90_4y/` and `https://web1.tcte.edu.tw/EXAM/91_4y/` returned HTTP 404 (236 bytes, SHA-256 `9448f8a1159c9b14e3e1b9d8eab1a6ddf88d26e1f888a34cef430c756e4e6e1e`) on 2026-07-29. The reviewed event blockers are recorded in `catalog/source-coverage/tcte_tve.json`; ROC 90/91 remain outside the per-subject denominator until a current official replacement is verified.

## Normalization Rules

- all normalized records carry `provider_id = "tcte_tve"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `tcte-tve`
  - `canonical_name`: `四技二專統一入學測驗`
- ROC years from URL paths are converted to Gregorian years by adding 1911

## Publication Integration

Register the provider in:

- `app/providers/registry.py`
- `app/site_registry.py`
- `app/normalizer.py`
- `frontend/src/lib/exam-classification.ts`

Keep one public bundle until real bundle size shows that group-level bundles are needed.

## Non-Goals

- no 二技 provider in this source
- no exam-outline-only assets
- no browser automation
- no Shuati crawling
