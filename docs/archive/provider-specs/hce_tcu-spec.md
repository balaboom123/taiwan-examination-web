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

- accepted category archive: `https://admissions.tcu.edu.tw/?cat=23`
- official program/provenance page: `https://admissions.tcu.edu.tw/?page_id=62`
- accepted paper page: `https://admissions.tcu.edu.tw/?p=26534`
- implemented provider: `app/providers/hce_tcu/`
- parser/shared client: `app/providers/hce_archive.py`
- current synced coverage: ROC 115 / AD 2026, 1 event, 8 files, 0 failures
- current local bundle identity: `hce-tcu-post-baccalaureate-medical-not-applicable-hce-tcu`; remote release-asset existence was not verified by this audit

## Discovery Model

Discovery uses the official `後中醫招生訊息` category rather than the
program page's five-item latest-post widget. On 2026-07-30 the category and its
public WordPress API exposed nine HCE posts and exactly one paper event: ROC 115
/ AD 2026. The event publishes separate question and reference-answer PDFs for
Chinese, chemistry, English, and biology.

The provider mirrors official paper assets by year and subject into:

- `data/providers/hce_tcu/`
- `mirror/providers/hce_tcu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_tcu --site-id default
```

All eight current files were downloaded through the normal provider path on
2026-07-30. Their 3,963,069 bytes match the retained SHA-256 checksums, and all
eight `HEAD` requests return HTTP 200.

This is not a historical-completeness claim. Three known official ROC 114 / AD
2025 question/clarification URLs now return HTTP 302 to the TCU homepage, and
neither the current category nor its API exposes a 2025 paper event. The
manifest retains the exact URLs, redirect target, response size, and response
hash as source-removal evidence. Private or third-party copies are not accepted
as replacements.

## Normalization Rules

- `provider_id`: `hce_tcu`
- `canonical_id`: `hce-tcu`
- `canonical_name`: `慈濟大學學士後中醫學系`

## Source Restrictions

- `/robots.txt` returns the WordPress homepage as `text/html`, so the site
  publishes no machine-readable robots directives.
- Default TLS verification succeeds.
- No explicit redistribution license or copyright terms were linked from the
  archive pages. Mirroring/publication remains subject to the repository-wide
  legal and takedown decision.

## Non-Goals

- no third-party mirrors
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
