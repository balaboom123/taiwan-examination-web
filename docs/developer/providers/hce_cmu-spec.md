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

The accepted source must be an official China Medical University page or an official admission system named by the university. Public direct downloads are required. Private mirrors and practice sites are rejected.

## Implementation Status

- accepted source: `https://spbcm.cmu.edu.tw/page/384`, which links `考古題下載` to `https://adm21.cmu.edu.tw/?q=news_spbcm`
- implemented provider: `app/providers/hce_cmu/`
- parser/shared client: `app/providers/hce_archive.py`
- current synced coverage: ROC 115 / AD 2026, 8 files, 0 failures
- public bundle: `hce-cmu` at `https://github.com/balaboom123/taiwan-examination-web/releases/download/default-bundles-001/hce-cmu.zip`

## Discovery Model

If accepted, the provider mirrors official paper assets by year and subject into:

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
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
