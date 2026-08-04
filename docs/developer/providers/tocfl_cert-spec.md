# Provider Spec: `tocfl_cert`

## Summary

- `provider_id`: `tocfl_cert`
- status: active; audit-partial
- target site: `default`
- source family: TOCFL 華語文能力測驗 official reference and mock-test downloads
- source URLs:
  - `https://tocfl.edu.tw/tocfl/index.php/exam/download`
  - `https://tocfl.edu.tw/tocfl/index.php/exam/test/page/1?pressBtn=%28%E9%A1%8C%E5%BA%AB%29`

## Source Model

The provider mirrors official reference PDF/ZIP/XLS assets and official mock-test download assets. The mock-test page exposes direct `.rar` and `.xlsx` links for traditional/simplified questions, audio bundles, answers, and listening scripts.

The live pages expose 95 unique URLs: three filename-dated reference assets (two from 2022 and one from 2024) and 92 rolling mock-bank assets. The mock page says that its 2,138-question bank was updated in October 2025 and that the rolling model began in 2024. It does not declare an AD 2026 exam or resource year. The adapter's process-date assignment therefore puts all 92 mock assets under unsupported synthetic 2026 identity.

The page limits the copyrighted mock materials to learning/non-commercial use, and the site reserves rights. No blanket GitHub republication permission is recorded.

## Output Model

- retained exams by filename year or process year: `tocfl-cert-<year>`
- required mock identity: a stable rolling-bank identity, not the runtime year
- category: `TOCFL華語文能力測驗官方參考資料`
- file types:
  - `question`: reference documents and mock question archives
  - `listening_audio`: mock audio archives
  - `answer`: mock answer spreadsheets
  - `question_alt`: mock listening-script archives
- provider data: `data/providers/tocfl_cert/`
- workflow: `.github/workflows/sync-tocfl-cert.yml`

## Safe Next Steps

1. Fetch the official TOCFL reference-download and mock-test pages.
2. Parse direct `.pdf`, `.zip`, `.rar`, `.xls`, and `.xlsx` links.
3. Deduplicate URLs.
4. Replace the process-year mock event with a stable reviewed rolling identity.
5. Record redistribution/takedown authority before republishing.
