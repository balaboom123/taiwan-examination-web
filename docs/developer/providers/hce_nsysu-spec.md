# Provider Spec: `hce_nsysu`

## Summary

- `provider_id`: `hce_nsysu`
- status: implemented
- target site: `default`
- source family: National Sun Yat-sen University HCE admission archive
- Shuati bucket: `/exams/hce_nsysu`
- Shuati subjects: 普通生物及生化概論, 物理與化學, 英文, 計算機概論與程式設計
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Rule

The accepted source must be an official National Sun Yat-sen University page or an official admission system named by the university. Public direct downloads are required. Private mirrors and practice sites are rejected.

## Implementation Status

- accepted source: `https://www.nsysu.edu.tw/p/412-1000-94.php?Lang=zh-tw`, which links the official library archive
- accepted paper archive: `https://lis.nsysu.edu.tw/p/412-1001-23442.php?Lang=zh-tw`
- implemented provider: `app/providers/hce_nsysu/`
- parser/shared client: `app/providers/hce_archive.py`
- current synced coverage: ROC 111-115 / AD 2022-2026, 5 combined PDFs, 0 failures
- public bundle: `hce-nsysu` at `https://github.com/balaboom123/taiwan-examination-web/releases/download/default-bundles-001/hce-nsysu.zip`

## Discovery Model

If accepted, the provider mirrors official paper assets by year and subject into:

- `data/providers/hce_nsysu/`
- `mirror/providers/hce_nsysu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_nsysu --site-id default
```

## Normalization Rules

- `provider_id`: `hce_nsysu`
- `canonical_id`: `hce-nsysu`
- `canonical_name`: `國立中山大學 HCE 入學考試`

## Non-Goals

- no third-party mirrors
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
