# Provider Spec: `jlpt_cert`

## Summary

- `provider_id`: `jlpt_cert`
- status: active; declared source scope complete, redistribution blocked
- target site: `default`
- source family: JLPT official practice workbook downloads
- source URL: `https://www.jlpt.jp/e/samples/sampleindex.html`

## Source Model

The provider scans the official JLPT practice workbook page. The page exposes direct PDF and MP3 links for workbook sections published in 2018 and 2012.

Files are grouped by the workbook section year on the page. This keeps 2012 workbook audio links that are hosted under `sample2017/` with the 2012 workbook.

The current page exposes exactly 58 files in each section (116 unique URLs total), and retained URL/checksum state agrees. That is complete only for this explicit sample-workbook denominator. The official FAQ says every administered sitting is not published.

The official copyright policy does not grant blanket archive republication. It also identifies separate third-party restrictions for N1/N2 grammar/reading content and all N1–N5 listening audio. Keep release blocked pending an operator/legal decision; exact source/local agreement is not permission.

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

## Safe Next Steps

1. Fetch the official JLPT practice workbook page.
2. Parse direct PDF and MP3 links under each workbook-year section.
3. Classify workbook assets by filename suffix.
4. Obtain and record redistribution authority before any refresh or release.
5. Preserve both per-level and aggregate mirror identity sets until reviewed deduplication.
