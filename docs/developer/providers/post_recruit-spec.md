# Provider Spec: `post_recruit`

## Summary

- `provider_id`: `post_recruit`
- status: implemented
- target site: `default`
- source family: Chunghwa Post recruitment or its named commissioned exam host
- Shuati bucket: `/exams/post_recruit`
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Overview

Source proof passed on 2026-07-05.

- accepted source owner: Chunghwa Post, linking to TABF as commissioned exam host
- Chunghwa Post source page: `https://www.post.gov.tw/post/internet/Group/index.jsp?ID=1467343194090`
- TABF history-paper page: `https://svc.tabf.org.tw/115post02//Paper/Year`
- accepted coverage in local data: 112-114年 / 2023-2025
- accepted file type: public direct PDF links under TABF `_File/Download/.../HistoryPaper/`

The accepted source must be Chunghwa Post or a host explicitly named by Chunghwa Post for the recruitment year. A cram-school mirror is not an accepted source even if it has complete PDFs.

Accepted source properties:

- source access: public pages plus direct downloadable files
- authentication: none
- file types: PDF, ZIP, or official document formats that can be mirrored without browser-only steps
- cadence: irregular recruitment cycles
- rejection rule: no provider if the only available source is a third-party mirror

## Discovery Model

The provider, if accepted, crawls official recruitment-year pages and mirrors first-test written-paper assets by level and subject.

Provider-owned outputs live under:

- `data/providers/post_recruit/`
- `mirror/providers/post_recruit/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-post-recruit.yml`

The primary operator command is:

```bash
python -m app sync-full --provider post_recruit --site-id default
```

## Implementation Status

- provider package: `app/providers/post_recruit/`
- focused tests: `tests/test_post_recruit.py`
- published bundle: `post-recruit`
- local synced coverage: 112-114年 / 2023-2025, 112 files

## Normalization Rules

- all normalized records carry `provider_id = "post_recruit"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `post-recruit`
  - `canonical_name`: `中華郵政職階人員甄試`

## Publication Integration

Register the provider only after source proof passes:

- `app/providers/registry.py`
- `app/site_registry.py`
- `app/normalizer.py`
- `frontend/src/lib/exam-classification.ts`

## Non-Goals

- no third-party mirrors
- no oral-test, physical-test, admission-ticket, score-list, or roster files
- no browser automation
- no Shuati crawling
