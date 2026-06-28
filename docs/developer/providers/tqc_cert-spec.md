# Provider Spec: `tqc_cert`

## Summary

- `provider_id`: `tqc_cert`
- status: active
- target site: `default`
- source family: TQC official sample papers
- source URL: `https://www.tqc.org.tw/TQCNet/ExamPaper.aspx`

## Source Model

The TQC sample-paper page lists certificate subject title, category, publication date, and a direct PDF sample-paper link under `www.tqc.org.tw/user/Example/`.

## Output Model

- one current-year exam: `tqc-cert-samples`
- category: `TQC範例試卷_<source category>`
- file type: `question`
- provider data: `data/providers/tqc_cert/`
- workflow: `.github/workflows/sync-tqc-cert.yml`

## Plan

1. Fetch the TQC sample-paper listing.
2. Parse direct PDF links and their adjacent title/category/date cells.
3. Normalize subject codes from titles.
4. Mirror PDFs through the standard sync pipeline.
