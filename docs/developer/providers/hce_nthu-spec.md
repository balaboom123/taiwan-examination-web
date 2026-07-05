# Provider Spec: `hce_nthu`

## Summary

- `provider_id`: `hce_nthu`
- status: implemented
- target site: `default`
- source family: National Tsing Hua University HCE admission archive
- Shuati bucket: `/exams/hce_nthu`
- Shuati subjects: 化學與物理, 生物與生化, 英文, 資訊科學, 進階物理與線性代數
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Rule

The accepted source must be an official National Tsing Hua University page or an official admission system named by the university. Public direct downloads are required. Private mirrors and practice sites are rejected.

## Implementation Status

- accepted source: `https://adms.site.nthu.edu.tw/p/403-1207-6125-1.php?Lang=zh-tw`
- accepted paper page: `https://adms.site.nthu.edu.tw/p/406-1207-305076,r6125.php?Lang=zh-tw`
- implemented provider: `app/providers/hce_nthu/`
- parser/shared client: `app/providers/hce_archive.py`
- current synced coverage: ROC 115 / AD 2026, 4 files, 0 failures
- public bundle: `hce-nthu` at `https://github.com/balaboom123/taiwan-examination-web/releases/download/default-bundles-001/hce-nthu.zip`

## Discovery Model

If accepted, the provider mirrors official paper assets by year and subject into:

- `data/providers/hce_nthu/`
- `mirror/providers/hce_nthu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_nthu --site-id default
```

## Normalization Rules

- `provider_id`: `hce_nthu`
- `canonical_id`: `hce-nthu`
- `canonical_name`: `國立清華大學 HCE 入學考試`

## Non-Goals

- no third-party mirrors
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
