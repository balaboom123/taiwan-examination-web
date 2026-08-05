# Provider Spec: `hce_cmu`

## Summary

- `provider_id`: `hce_cmu`
- status: implemented
- target site: `default`
- source family: China Medical University HCE admission archive
- Shuati bucket: `/exams/hce_cmu`
- Shuati subjects: 化學, 國文, 生物學, 英文
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Rule

The accepted provenance page is the official China Medical University program page at `https://spbcm.cmu.edu.tw/page/384`; its `考古題下載` link names the official archive at `https://adm21.cmu.edu.tw/?q=zh-hant/news_spbcm`. Public exam-file links are required. Private mirrors and practice sites are rejected.

The archive's `robots.txt` specifies `Crawl-delay: 10`, which the shared client honors. Default CA verification for `adm21.cmu.edu.tw` fails in this environment; the existing shared client uses an unverified TLS context only for `adm21.cmu.edu.tw`. That is a documented transport-authenticity limitation requiring remediation or explicit risk acceptance. No explicit redistribution license or copyright terms were linked from the archive pages.

## Implementation Status

- accepted source: official CMU provenance page plus the linked `adm21.cmu.edu.tw` archive
- implemented provider: `app/providers/hce_cmu/`
- parser/shared client: `app/providers/hce_archive.py`
- source manifest: 6/6 official events for ROC 110–115 / AD 2021–2026, captured 2026-07-30
- asset reconciliation: all 30 live question/answer URLs match local state; all six events are published-complete
- public bundle: `hce-cmu` at `https://github.com/balaboom123/taiwan-examination-web/releases/download/default-bundles-v2-001/hce-cmu-post-baccalaureate-medical-not-applicable-hce-cmu--ab6c4df6cc4d.zip`

## Discovery Model

The provider follows all four bounded archive pages, deduplicates fragment-only pagination variants, and mirrors official paper assets by year and subject into:

- `data/providers/hce_cmu/`
- `mirror/providers/hce_cmu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_cmu --site-id default
```

## Normalization Rules

- `provider_id`: `hce_cmu`
- `canonical_id`: `hce-cmu`
- `canonical_name`: `中國醫藥大學 HCE 入學考試`

## Non-Goals

- no third-party mirrors
- no pages outside the dedicated four-page archive
- no certificate-verification bypass beyond the documented `adm21.cmu.edu.tw` exception without explicit review
- no provider that would publish zero files
- no Shuati crawling
