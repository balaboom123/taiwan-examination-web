# Provider Spec: `tqc_cert`

## Summary

- `provider_id`: `tqc_cert`
- status: active
- target site: `default`
- source family: TQC official sample papers
- source URL: `https://www.tqc.org.tw/TQCNet/ExamPaper.aspx`

## Source Model

The TQC sample-paper page is a paginated ASP.NET listing. Each row lists certificate subject title, category, publication date, and a direct PDF sample-paper link under `www.tqc.org.tw/user/Example/`.

Only `/user/Example/*.pdf` links are mirrored. Pagination links and administrative downloads are discovery inputs, not bundle files.

TQC+ was evaluated as an adjacent CSF source, but it is not part of `tqc_cert`; add a separate `tqcplus_cert` provider only if TQC+ enters scope.

## Output Model

- one exam per source publication year: `tqc-cert-samples-<year_ad>`
- category: `TQC範例試卷_<source category>`
- file type: `question`
- provider data: `data/providers/tqc_cert/`
- workflow: `.github/workflows/sync-tqc-cert.yml`

## Plan

1. Fetch the TQC sample-paper listing.
2. Discover paginated listing pages from ASP.NET postback anchors or plain page links.
3. Parse direct `/user/Example/*.pdf` links and their adjacent title/category/date cells.
4. Deduplicate by final PDF URL.
5. Normalize subject codes from titles.
6. Mirror PDFs through the standard sync pipeline.
