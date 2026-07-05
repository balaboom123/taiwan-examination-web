# Provider Spec: `hce_tcu`

## Summary

- `provider_id`: `hce_tcu`
- status: implemented
- target site: `default`
- source family: Tzu Chi University HCE admission archive
- Shuati bucket: `/exams/hce_tcu`
- Shuati subjects: 化學, 國文, 生物學, 英文
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Rule

The accepted source must be an official Tzu Chi University page or an official admission system named by the university. Public direct downloads are required. Private mirrors and practice sites are rejected.

## Implementation Status

- accepted source: `https://admissions.tcu.edu.tw/?page_id=62`
- accepted paper page: `https://admissions.tcu.edu.tw/?p=26534`
- implemented provider: `app/providers/hce_tcu/`
- parser/shared client: `app/providers/hce_archive.py`
- current synced coverage: ROC 115 / AD 2026, 8 files, 0 failures
- public bundle: `hce-tcu` at `https://github.com/balaboom123/taiwan-examination-web/releases/download/default-bundles-001/hce-tcu.zip`

## Discovery Model

If accepted, the provider mirrors official paper assets by year and subject into:

- `data/providers/hce_tcu/`
- `mirror/providers/hce_tcu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_tcu --site-id default
```

## Normalization Rules

- `provider_id`: `hce_tcu`
- `canonical_id`: `hce-tcu`
- `canonical_name`: `慈濟大學 HCE 入學考試`

## Non-Goals

- no third-party mirrors
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
