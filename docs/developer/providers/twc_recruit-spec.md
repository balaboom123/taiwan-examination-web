# Provider Spec: `twc_recruit`

## Summary

- `provider_id`: `twc_recruit`
- status: planned
- target site: `default`
- source family: Taiwan Water Corporation (TWC) company-specific recruitment exam (評價職位人員甄試) past-exam archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

Taiwan Water Corporation (台灣自來水公司, TWC) conducts its own annual recruitment exam for evaluation-position personnel (評價職位人員), separate from the MOEA joint professional-level exam handled by `moea_recruit`. This provider covers TWC's company-specific exam papers hosted on its official website.

- source domain: `www.water.gov.tw`
- source URL: `https://www.water.gov.tw/ch/Subject/Detail/59619?nodeId=715`
- employment information section: `https://www.water.gov.tw/ch/Subject?nodeId=715`
- source access: public web pages plus linked ZIP archives containing PDF files
- source cadence: yearly exam administrations; archive page updated when new materials are published
- authentication: none
- rate-limit posture: conservative scheduled sync

## Discovery Model

The provider crawls TWC's employment information detail page, which lists per-year ZIP downloads of exam papers with answer keys. Each year's entry is a single ZIP bundle.

Available archive spans ROC years 103–114 (2014–2025) as of the last survey. Each ZIP bundle contains:

| Year (ROC) | Year (Gregorian) | File name pattern            | Size   |
|------------|-------------------|------------------------------|--------|
| 103        | 2014              | `103年試題(解答).zip`         | ~7.0M  |
| 104        | 2015              | `104年試題(解答).zip`         | ~9.3M  |
| 105        | 2016              | `105年試題(解答).zip`         | ~6.1M  |
| 106        | 2017              | `106年試題(解答).zip`         | ~8.3M  |
| 107        | 2018              | `107年試題(解答).zip`         | ~6.4M  |
| 108        | 2019              | `108年試題(解答).zip`         | ~6.3M  |
| 110        | 2021              | `110年試題(解答).zip`         | ~7.8M  |
| 111        | 2022              | `111年試題(解答).zip`         | ~11.8M |
| 112        | 2023              | `112年試題(解答).zip`         | ~5.7M  |
| 114        | 2025              | `114年試題(解答).zip`         | ~4.8M  |

Provider-owned outputs live under:

- `data/providers/twc_recruit/`
- `mirror/providers/twc_recruit/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-twc-recruit.yml`

That workflow is provider-only. It refreshes `data/providers/twc_recruit/` and does not publish the aggregated `default` site on its own.

The primary operator command is:

```bash
python -m app sync-full --provider twc_recruit --site-id default
```

## Scraping Considerations

- The archive page uses a CMS-style URL structure (`/ch/Subject/Detail/[id]?nodeId=715`)
- File downloads use a server file handler with UUID-based paths: `/ch/ServerFile/Get/[uuid]?nodeId=715`
- Each download entry includes a SHA256 verification link
- ZIP archives contain individual PDF files per subject and per answer key — the provider must unpack ZIPs during mirror phase to normalize individual papers
- Some years are absent from the listing (e.g. 109, 113); the provider should not treat gaps as errors

## Normalization Rules

- all normalized records carry `provider_id = "twc_recruit"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `twc-recruit`
  - `canonical_name`: `台水評價職位人員甄試`
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
