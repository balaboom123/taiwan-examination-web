# Provider Spec: `cpc_recruit`

## Summary

- `provider_id`: `cpc_recruit`
- status: planned
- target site: `default`
- source family: CPC Corporation, Taiwan company-specific recruitment exam past-exam archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

CPC Corporation, Taiwan (台灣中油公司) conducts its own recruitment for operational-level hired personnel (僱用人員) and doctoral-level researchers, separate from the MOEA joint professional-level exam handled by `moea_recruit`. This provider covers CPC's company-specific exam materials hosted on its official website.

- source domain: `www.cpc.com.tw`
- employment information hub: `https://www.cpc.com.tw/News.aspx?n=32&sms=8969`
- past PhD-level exam papers: `https://www.cpc.com.tw/News_Content.aspx?n=32&s=826`
- past hiring exam outlines (簡章): `https://www.cpc.com.tw/News_Content.aspx?n=32&s=824`
- source access: public web pages plus linked PDF files
- source cadence: yearly exam administrations; archive updated when new materials are published
- authentication: none
- rate-limit posture: conservative scheduled sync

## Content Scope

CPC's official website hosts two categories of exam materials:

| Category                   | Chinese name             | Source URL                                        |
|---------------------------|--------------------------|---------------------------------------------------|
| PhD-level exam papers      | 新進博士級人員甄試試題    | `News_Content.aspx?n=32&s=826`                    |
| Hiring exam outlines       | 新進僱用人員甄試簡章      | `News_Content.aspx?n=32&s=824`                    |

CPC's joint exam page (`News_Content.aspx?n=32&s=844`) redirects to Taipower's download archive — those papers are handled by the `moea_recruit` provider and are not duplicated here.

CPC does not independently host past exam papers for its hiring-level (僱用人員) recruitment on its official website. These papers are administered by contracted exam agencies and published through them rather than on `cpc.com.tw`.

## Discovery Model

The provider crawls CPC's employment information section, extracts PDF links from the PhD-level exam papers page and hiring exam outline pages. Individual announcements follow the URL pattern `News_Content.aspx?n=32&s=[id]`.

Provider-owned outputs live under:

- `data/providers/cpc_recruit/`
- `mirror/providers/cpc_recruit/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-cpc-recruit.yml`

That workflow is provider-only. It refreshes `data/providers/cpc_recruit/` and does not publish the aggregated `default` site on its own.

The primary operator command is:

```bash
python -m app sync-full --provider cpc_recruit --site-id default
```

## Scraping Considerations

- CPC's website uses ASP.NET; pages use standard server-side rendering (no ViewState postback required for read-only listing pages)
- PDF files are served through a download handler at `ws.cpc.com.tw/Download.ashx` with base64-encoded path and filename parameters
- The employment information listing is paginated — the scraper should iterate all pages under `News.aspx?n=32&sms=8969`

## Normalization Rules

- all normalized records carry `provider_id = "cpc_recruit"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `cpc-recruit`
  - `canonical_name`: `中油新進人員甄試`
- records are tagged with exam level: `level = "phd"` for doctoral recruitment, `level = "hire"` for operational-level outlines
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
