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

The accepted provenance page is the official National Sun Yat-sen University admissions page at `https://www.nsysu.edu.tw/p/412-1000-94.php?Lang=zh-tw`; it links the official library archive at `https://lis.nsysu.edu.tw/p/412-1001-23442.php?Lang=zh-tw`. Public direct downloads are required. Private mirrors and practice sites are rejected.

The archive's `robots.txt` allows all paths and default TLS verification succeeds. No explicit redistribution license or copyright terms were linked from the archive pages.

## Implementation Status

- accepted source: `https://www.nsysu.edu.tw/p/412-1000-94.php?Lang=zh-tw`, which links the official library archive
- accepted paper archive: `https://lis.nsysu.edu.tw/p/412-1001-23442.php?Lang=zh-tw`
- implemented provider: `app/providers/hce_nsysu/`
- parser/shared client: `app/providers/hce_archive.py`
- source manifest: 5/5 official events for ROC 111–115 / AD 2022–2026, captured 2026-07-30
- asset reconciliation: all five live combined PDFs match retained SHA-256 checksums byte for byte (35,509,877 bytes total)
- all five events are published-complete with zero failures
- public bundle: `hce-nsysu` at `https://github.com/balaboom123/taiwan-examination-web/releases/download/default-bundles-v2-001/hce-nsysu-post-baccalaureate-medical-not-applicable-hce-nsysu--1a601723a824.zip`

## Discovery Model

The provider reads the bounded library listing and mirrors its one official combined question-and-answer PDF per year into:

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
- no attempt to split official combined PDFs into inferred subject files
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
