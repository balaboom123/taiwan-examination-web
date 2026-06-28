# Provider Spec: `taisugar_recruit`

## Summary

- `provider_id`: `taisugar_recruit`
- status: planned
- target site: `default`
- source family: Taiwan Sugar Corporation (Taisugar) company-specific recruitment exam (新進工員甄試) past-exam archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

Taiwan Sugar Corporation (台灣糖業公司, Taisugar) conducts its own annual recruitment exam for new operational-level workers (新進工員), including a work-study cooperative track (產學合作). This is separate from the MOEA joint professional-level exam handled by `moea_recruit`. This provider covers Taisugar's company-specific exam papers hosted on its official website.

- source domain: `www.taisugar.com.tw`
- recruitment section (人才招募): `https://www.taisugar.com.tw/chinese/News_Index.aspx?p=3&n=10080`
- source access: public web pages plus linked ZIP archives containing PDF files
- source cadence: yearly exam administrations; individual announcement pages published when new materials are available
- authentication: none
- rate-limit posture: conservative scheduled sync

## Discovery Model

The provider crawls Taisugar's recruitment news listing page, identifies exam-paper announcements, and follows each to its detail page to extract ZIP download links.

Listing URL pattern: `News_Index.aspx?p=3&n=10080&page=[N]`
Detail page URL pattern: `News_detail.aspx?p=3&n=10080&s=[id]`

Each detail page typically provides ZIP downloads for:

- 新進工員甄試試題及解答 (new worker exam papers and answers)
- 產學合作甄試試題及解答 (work-study cooperative exam papers and answers)

Known example: ROC 111 (2022) detail page at `s=11543` provides two ZIP files (~12M and ~7M respectively).

The recruitment listing contains 36+ announcements across multiple pages, mixing exam papers with other recruitment notices (result announcements, assignment notifications, exam outlines). The provider must filter for exam-paper announcements specifically.

Provider-owned outputs live under:

- `data/providers/taisugar_recruit/`
- `mirror/providers/taisugar_recruit/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-taisugar-recruit.yml`

That workflow is provider-only. It refreshes `data/providers/taisugar_recruit/` and does not publish the aggregated `default` site on its own.

The primary operator command is:

```bash
python -m app sync-full --provider taisugar_recruit --site-id default
```

## Scraping Considerations

- The recruitment listing is paginated; the scraper must iterate all pages
- Detail pages mix exam-paper downloads with other recruitment content (簡章, 錄取名冊, 分發通知) — the provider should identify exam-paper entries by title pattern (e.g. containing `甄試試題`)
- ZIP files are served from `www.taisugar.com.tw/upload/UserFiles/News/[id]/[filename].zip`
- ZIP archives contain individual PDF files per subject — the provider must unpack ZIPs during mirror phase to normalize individual papers

## Normalization Rules

- all normalized records carry `provider_id = "taisugar_recruit"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `taisugar-recruit`
  - `canonical_name`: `台糖新進工員甄試`
- records are tagged with exam track: `track = "worker"` for standard recruitment, `track = "coop"` for work-study cooperative (產學合作)
- year values stored as Gregorian integers; the ROC year is derived (Gregorian − 1911)

The provider does not own a public release tag. Release tags are assigned later by site publication.

## Publication Integration

After provider sync completes, publish the `default` site separately when every required provider state and mirror input for that site is available:

```bash
python -m app publish-site --site-id default --repository <owner>/<repo>
```

Canonical site-owned outputs then live under:

- `data/sites/default/bundles.json`
- `data/sites/default/release-assets.json`
- `data/sites/default/lootlabs-links.json`
- `bundles/sites/default/`

For compatibility during the migration, the `default` site may also refresh legacy root-level outputs such as `data/bundles.json` and `data/lootlabs-links.json`.
