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
- yearly paper pages: `https://web1.tcte.edu.tw/EXAM/<roc_year:03d>_4y/`
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
- source manifest: 26 official listing events for ROC 90-115 / AD 2001-2026, captured 2026-07-30
- local synced coverage: ROC 90-115 / AD 2001-2026, 26 events and 3,079 normalized asset records
- all ROC 92-115 event metadata and paper/file URLs reconcile exactly with the current official pages
- ROC 90 resolves at the official padded path `https://web1.tcte.edu.tw/EXAM/090_4y/`: 46 parsed paper groups and 75 asset references (72 unique URLs), including multipart JPEG questions and the official HTML answer table
- ROC 91 resolves at `https://web1.tcte.edu.tw/EXAM/091_4y/`: 48 retained PDF question/answer asset records. The duplicate XLS representation of the same all-subject answer is intentionally excluded in favor of the official PDF.
- the former ROC 90/91 blockers tested unpadded `/90_4y/` and `/91_4y/` paths, which still return HTTP 404. They were retired after the current official listing proved the padded paths and both padded pages returned HTTP 200 on 2026-07-30.

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
