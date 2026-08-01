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
- current synced coverage: ROC 111–115 / AD 2022–2026, 5 events, 24 files, 0 failures
- current local bundle identity: `hce-nthu-post-baccalaureate-medical-not-applicable-hce-nthu`; remote release-asset existence was not verified by this audit

## Discovery Model

The official listing exposes four archive pages through embedded `urlPrefix` and
`totalPage` metadata. Discovery follows those pages, currently finding exactly
five annual event pages for ROC 111–115 / AD 2022–2026. It rejects pagination
growth beyond the configured eight-page safety bound instead of silently
truncating the source.

The provider mirrors official paper assets by year and subject into:

- `data/providers/hce_nthu/`
- `mirror/providers/hce_nthu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_nthu --site-id default
```

The source currently exposes:

- 2022–2024: English, biology/biochemistry, chemistry/physics, computer science, and one combined answer file;
- 2025: English, biology/biochemistry, chemistry/physics, advanced physics/linear algebra, and one combined answer file;
- 2026: English, biology/biochemistry, chemistry/physics, and one combined answer file.

All 24 live URLs were downloaded with the normal provider `GET` path on
2026-07-30. Their 76,022,336 bytes match the retained SHA-256 checksums. The
server returns HTTP 403 to `HEAD` for these same URLs, so `HEAD` alone must not
be treated as proof that the assets are blocked. The source manifest records
the four listing-page fingerprints, five event-page fingerprints, URL
inventory hashes, and per-file live checksums.

## Normalization Rules

- `provider_id`: `hce_nthu`
- `canonical_id`: `hce-nthu`
- `canonical_name`: `國立清華大學學士後醫學系`

## Source Restrictions

- `robots.txt` declares `User-agent: *` and `Allow: /`.
- Default TLS verification succeeds.
- No explicit redistribution license or copyright terms were linked from the
  archive pages. Mirroring/publication therefore remains subject to the
  repository-wide legal and takedown decision.

## Non-Goals

- no third-party mirrors
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
