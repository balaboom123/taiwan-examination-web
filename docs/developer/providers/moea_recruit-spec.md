# Provider Spec: `moea_recruit`

## Summary

- `provider_id`: `moea_recruit`
- status: planned
- target site: `default`
- source family: Ministry of Economic Affairs Joint Recruitment Examination for State-Owned Enterprises (經濟部所屬事業機構新進職員甄試) past-exam archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

The examination formally titled 經濟部所屬事業機構新進職員甄試 — officially translated as Joint Recruitment Examination for State-Owned Enterprises — is the unified annual hiring exam for professional-level (職員) positions across four state-owned enterprises under the Ministry of Economic Affairs (MOEA). Taiwan Power Company (Taipower) serves as the administrative body and hosts the exam portal and all past-paper downloads on behalf of MOEA.

Participating enterprises:

| Abbr | Chinese name   | English name                        | Provider            |
|------|---------------|-------------------------------------|---------------------|
| 台電 | 台灣電力公司   | Taiwan Power Company (Taipower)     | `taipower_recruit`  |
| 中油 | 台灣中油公司   | CPC Corporation, Taiwan             | `cpc_recruit`       |
| 台水 | 台灣自來水公司 | Taiwan Water Corporation (TWC)      | `twc_recruit`       |
| 台糖 | 台灣糖業公司   | Taiwan Sugar Corporation (Taisugar) | `taisugar_recruit`  |

Each enterprise also operates its own independent recruitment for operational-level positions; those are covered by the respective company providers listed above.

- source domain: `www.taipower.com.tw` (hosted by Taipower on behalf of MOEA)
- exam portal: `https://service.taipower.com.tw/exam/info.aspx`
- past exam papers (歷年試題): `https://www.taipower.com.tw/2289/2544/2554/2556/`
- past exam outlines (歷年簡章): `https://www.taipower.com.tw/2289/2544/2554/2555/`
- source access: public web pages plus linked PDF files
- source cadence: yearly — one examination administration per year, archive updated after each session
- authentication: none
- rate-limit posture: conservative scheduled sync; Taipower pages may use client-side rendering

## Discovery Model

The provider crawls the Taipower-hosted past-exam listing page, identifies per-year entries, and extracts linked PDF assets. Each year's exam typically includes multiple subject papers grouped by test category along with corresponding answer keys.

Provider-owned outputs live under:

- `data/providers/moea_recruit/`
- `mirror/providers/moea_recruit/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-moea-recruit.yml`

That workflow is provider-only. It refreshes `data/providers/moea_recruit/` and does not publish the aggregated `default` site on its own.

The primary operator command is:

```bash
python -m app sync-full --provider moea_recruit --site-id default
```

## Scraping Considerations

- The past-exam page (`/2289/2544/2554/2556/`) appears to use client-side rendering — static HTTP fetch returns empty content; a headless browser approach may be required
- The exam portal at `service.taipower.com.tw` is an ASP.NET application; if interaction beyond the info page is needed, ViewState handling may be required
- The alternate URL form `www.taipower.com.tw/tc/download.aspx?mid=261` exposes the same content through a server-side download listing — this may be a more reliable scraping target
- All exam assets are PDF format

## Normalization Rules

- all normalized records carry `provider_id = "moea_recruit"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `moea-recruit`
  - `canonical_name`: `國營事業聯招（新進職員）`
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
