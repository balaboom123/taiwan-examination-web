# Provider Spec: `tocfl_cert`

## Summary

- `provider_id`: `tocfl_cert`
- status: active
- target site: `default`
- source family: TOCFL 華語文能力測驗 official reference downloads
- source URL: `https://tocfl.edu.tw/tocfl/index.php/exam/download`

## Source Model

The TOCFL site has interactive mock-test pages, but the stable public direct downloads are on the reference-download page. The provider mirrors official PDF/ZIP assets exposed there.

## Output Model

- one current-year exam: `tocfl-cert-materials`
- category: `TOCFL華語文能力測驗官方參考資料`
- file type: `question`
- provider data: `data/providers/tocfl_cert/`
- workflow: `.github/workflows/sync-tocfl-cert.yml`

## Plan

1. Fetch the official TOCFL reference-download page.
2. Parse direct `.pdf` and `.zip` links.
3. Deduplicate URLs.
4. Mirror validated payloads through the standard sync pipeline.
