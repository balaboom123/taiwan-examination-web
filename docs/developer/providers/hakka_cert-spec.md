# Provider Spec: `hakka_cert`

## Summary

- `provider_id`: `hakka_cert`
- status: active
- target site: `default`
- source family: 客語能力認證 official教材及試題 downloads
- source URL: `https://elearning.hakka.gov.tw/hakka/download-files`

## Source Model

The provider scans the official Hakka download pages for level categories `c=2`, `c=3`, and `c=5`, following pagination links on the same source surface.

Direct `.pdf` files are mirrored as `question`. Direct `.zip` files and labels containing `音檔` are mirrored as `listening_audio`.

## Output Model

- source exams: `hakka-cert-<level>-<year>`
- canonical bundles:
  - `hakka-cert-basic-elementary`
  - `hakka-cert-intermediate-high-intermediate`
  - `hakka-cert-advanced`
- file types: `question`, `listening_audio`
- provider data: `data/providers/hakka_cert/`
- workflow: `.github/workflows/sync-hakka-cert.yml`

## Plan

1. Fetch each official level-category download page.
2. Follow same-source pagination.
3. Parse direct PDF and ZIP download links.
4. Mirror validated PDF and ZIP payloads through the standard sync pipeline.
