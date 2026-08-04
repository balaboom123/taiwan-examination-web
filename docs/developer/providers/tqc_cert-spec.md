# Provider Spec: `tqc_cert`

## Summary

- `provider_id`: `tqc_cert`
- status: active; audit-partial
- target site: `default`
- source family: TQC official sample papers
- source URL: `https://www.tqc.org.tw/TQCNet/ExamPaper.aspx`

## Source Model

The TQC sample-paper page is a paginated ASP.NET listing. Each row lists certificate subject title, category, publication date, and a direct PDF sample-paper link under `www.tqc.org.tw/user/Example/`.

Only `/user/Example/*.pdf` links are mirrored. Pagination links and administrative downloads are discovery inputs, not bundle files.

TQC+ was evaluated as an adjacent CSF source, but it is not part of `tqc_cert`; add a separate `tqcplus_cert` provider only if TQC+ enters scope.

The four current listing pages contain 44 PDFs across 11 source publication years. All 44 URLs remain represented, but nine public records point to the wrong bytes. Five title groups reuse generic Linux or input-method labels, and storage keys derived from those labels collapse distinct URLs. Exact live mismatch hashes are preserved in `data/providers/tqc_cert/source-manifest.json`.

The listing describes the PDFs as candidate-reference samples. Broader CSF pages prohibit reposting/excerpting without authorization, and no sample-paper republication grant was established.

## Output Model

- one exam per source publication year: `tqc-cert-samples-<year_ad>`
- category: `TQC範例試卷_<source category>`
- file type: `question`
- provider data: `data/providers/tqc_cert/`
- workflow: `.github/workflows/sync-tqc-cert.yml`

## Safe Next Steps

1. Fetch the TQC sample-paper listing.
2. Discover paginated listing pages from ASP.NET postback anchors or plain page links.
3. Parse direct `/user/Example/*.pdf` links and their adjacent title/category/date cells.
4. Deduplicate by final PDF URL.
5. Normalize subject codes from titles.
6. Migrate the five collision groups to URL-stable storage keys and byte-reconcile all 44 records.
7. Record redistribution/takedown authority before republishing.
