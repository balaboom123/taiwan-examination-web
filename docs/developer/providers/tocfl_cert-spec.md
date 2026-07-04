# Provider Spec: `tocfl_cert`

## Summary

- `provider_id`: `tocfl_cert`
- status: active
- target site: `default`
- source family: TOCFL 華語文能力測驗 official reference and mock-test downloads
- source URLs:
  - `https://tocfl.edu.tw/tocfl/index.php/exam/download`
  - `https://tocfl.edu.tw/tocfl/index.php/exam/test/page/1?pressBtn=%28%E9%A1%8C%E5%BA%AB%29`

## Source Model

The provider mirrors official reference PDF/ZIP/XLS assets and official mock-test download assets. The mock-test page exposes direct `.rar` and `.xlsx` links for traditional/simplified questions, audio bundles, answers, and listening scripts.

## Output Model

- source exams by filename year or current mock-test year: `tocfl-cert-<year>`
- category: `TOCFL華語文能力測驗官方參考資料`
- file types:
  - `question`: reference documents and mock question archives
  - `listening_audio`: mock audio archives
  - `answer`: mock answer spreadsheets
  - `question_alt`: mock listening-script archives
- provider data: `data/providers/tocfl_cert/`
- workflow: `.github/workflows/sync-tocfl-cert.yml`

## Plan

1. Fetch the official TOCFL reference-download and mock-test pages.
2. Parse direct `.pdf`, `.zip`, `.rar`, `.xls`, and `.xlsx` links.
3. Deduplicate URLs.
4. Mirror validated payloads through the standard sync pipeline.
