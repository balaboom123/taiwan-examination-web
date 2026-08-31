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
- current-notice index: `https://www.ceec.edu.tw/xmdoc?xsmsid=0I363338985390931117`
- source access: public web pages plus linked PDF files
- source cadence: yearly archive updates with occasional late-file corrections
- authentication: none
- rate-limit posture: conservative scheduled sync; fetch static pages and direct downloads only

CEEC lists 分科測驗 under "分科測驗(110前指考)" and exposes "歷年試題及答題卷" with general, special, and special-answer-sheet pages. This provider mirrors the general-paper archive plus current official confirmed-answer and scoring-principle notices.

## Discovery Model

The provider crawls the general-paper listing, groups rows by academic year and subject, and mirrors linked PDF assets for question papers, answer sheets, answers, and scoring principles.

The shared listing selector includes predecessor 指定科目考試 years, but AST began in AD 2022. Discovery therefore reports only years with actual AST rows or notices. The 2026-07-29 snapshot contains 31 event identities across AD 2022–2026: 29 subject rows plus the AD 2026 confirmed-materials and scoring-principles pages.

CEEC listing links for current notices are normalized to their canonical `/xmdoc/cont` detail routes before parsing. The two AD 2026 pages use distinct event identities so confirmed files cannot silently reuse preliminary-answer mirror paths. Their per-subject records normalize into the same established subject bundles as AD 2022–2025.

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
- local synced coverage: 111–115學年度 / AD 2022–2026, 31 events and 177 files
- discovery evidence: `data/providers/ceec_ast/source-manifest.json`, 31/31 local event representation
- current reconciliation: zero sync failures, zero normalization-review records, and 31/31 events published-complete

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
- no predecessor 指定科目考試 archive in the AST provider
- no Shuati crawling
