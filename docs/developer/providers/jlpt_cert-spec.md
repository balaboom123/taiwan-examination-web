# Provider Spec: `jlpt_cert`

## Summary

- `provider_id`: `jlpt_cert`
- status: active
- target site: `default`
- source family: JLPT official practice workbook downloads
- source URL: `https://www.jlpt.jp/e/samples/sampleindex.html`

## Source Model

The provider scans the official JLPT practice workbook page. The page exposes direct PDF and MP3 links for workbook sections published in 2018 and 2012.

Files are grouped by the workbook section year on the page. This keeps 2012 workbook audio links that are hosted under `sample2017/` with the 2012 workbook.

## Output Model

- source exams: `jlpt-cert-practice-2018`, `jlpt-cert-practice-2012`
- canonical bundle: `jlpt-cert`
- file types:
  - `question`: vocabulary, grammar, reading, and listening PDFs
  - `listening_audio`: MP3 listening files
  - `answer_sheet`: sample answer-sheet PDFs
  - `answer`: answer PDFs
  - `question_alt`: listening-script PDFs
- provider data: `data/providers/jlpt_cert/`
- workflow: `.github/workflows/sync-jlpt-cert.yml`

## Plan

1. Fetch the official JLPT practice workbook page.
2. Parse direct PDF and MP3 links under each workbook-year section.
3. Classify workbook assets by filename suffix.
4. Mirror validated PDF and MP3 payloads through the standard sync pipeline.
