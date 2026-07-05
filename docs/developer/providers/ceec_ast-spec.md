# Provider Spec: `ceec_ast`

## Summary

- `provider_id`: `ceec_ast`
- status: implemented
- target site: `default`
- source family: College Entrance Examination Center 分科測驗 archive
- Shuati bucket: `/exams/ast`
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

- source domain: `www.ceec.edu.tw`
- source page: `https://www.ceec.edu.tw/xmfile?xsmsid=0J052427633128416650`
- source access: public web pages plus linked PDF files
- source cadence: yearly archive updates with occasional late-file corrections
- authentication: none
- rate-limit posture: conservative scheduled sync; fetch static pages and direct downloads only

CEEC lists 分科測驗 under "分科測驗(110前指考)" and exposes "歷年試題及答題卷" with general, special, and special-answer-sheet pages. The first provider should mirror the general-paper archive only.

## Discovery Model

The provider crawls the general-paper listing, groups rows by academic year and subject, and mirrors linked PDF assets for question papers, answer sheets, answers, and scoring principles.

Provider-owned outputs live under:

- `data/providers/ceec_ast/`
- `mirror/providers/ceec_ast/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-ceec-ast.yml`

The primary operator command is:

```bash
python -m app sync-full --provider ceec_ast --site-id default
```

## Implementation Status

- provider package: `app/providers/ceec_ast/`
- focused tests: `tests/test_ceec_ast.py`
- published bundle: `ceec-ast`
- local synced coverage: 111-114學年度 / 2022-2025, 145 files

## Normalization Rules

- all normalized records carry `provider_id = "ceec_ast"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `ceec-ast`
  - `canonical_name`: `分科測驗`
- year values are stored as Gregorian integers; ROC year is derived as Gregorian year minus 1911

## Publication Integration

Register the provider in:

- `app/providers/registry.py`
- `app/site_registry.py`
- `app/normalizer.py`
- `frontend/src/lib/exam-classification.ts`

Do not split public bundles by subject until generated bundle size or UX feedback proves that one bundle is painful.

## Non-Goals

- no paid CEEC publications
- no browser automation
- no special-paper or special-answer-sheet pages in the first provider
- no Shuati crawling
