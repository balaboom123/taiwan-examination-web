# Provider Spec: `taipower_recruit`

## Summary

- `provider_id`: `taipower_recruit`
- status: planned
- target site: `default`
- source family: Taiwan Power Company (Taipower) company-specific recruitment exam (新進僱用人員甄試) past-exam archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

Taiwan Power Company (台灣電力公司, Taipower) conducts its own annual recruitment exam for operational-level hired personnel (僱用人員/養成班), separate from the MOEA joint professional-level exam handled by `moea_recruit`. This provider covers Taipower's company-specific hiring exam papers only.

- source domain: `www.taipower.com.tw`
- source URL (past papers): `https://www.taipower.com.tw/2289/2544/2554/2557/simpleList`
- alternate URL: `https://www.taipower.com.tw/tc/download.aspx?mid=262`
- source access: public web pages plus linked PDF files
- source cadence: yearly — typically one exam administration per year, archive updated after each session
- authentication: none
- rate-limit posture: conservative scheduled sync; pages may use client-side rendering

## Discovery Model

The provider crawls the Taipower hiring-exam archive listing, identifies per-year entries, and extracts linked PDF assets. Available years span from ROC 90 (2001) through recent administrations, including multiple sessions in some years (e.g. 107年5月, 107年12月).

Each year's entry typically includes subject-specific exam papers and answer keys in PDF format.

Provider-owned outputs live under:

- `data/providers/taipower_recruit/`
- `mirror/providers/taipower_recruit/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-taipower-recruit.yml`

That workflow is provider-only. It refreshes `data/providers/taipower_recruit/` and does not publish the aggregated `default` site on its own.

The primary operator command is:

```bash
python -m app sync-full --provider taipower_recruit --site-id default
```

## Scraping Considerations

- The primary listing page (`/2289/2544/2554/2557/simpleList`) may use client-side rendering — the alternate server-side URL (`/tc/download.aspx?mid=262`) is a more reliable scraping target
- Individual year entries follow the pattern `/2289/2544/2554/2557/[id]/` with download links to PDF files
- All exam assets are PDF format

## Normalization Rules

- all normalized records carry `provider_id = "taipower_recruit"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `taipower-recruit`
  - `canonical_name`: `台電新進僱用人員甄試`
- year values stored as Gregorian integers; the ROC year is derived (Gregorian − 1911)
- years with multiple exam sessions are disambiguated by session date (e.g. `2018-05`, `2018-12`)

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
