# Provider Spec: `ceec_gsat`

## Summary

- `provider_id`: `ceec_gsat`
- status: active
- target site: `default`
- source family: College Entrance Examination Center GSAT archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

- source domain: `www.ceec.edu.tw`
- source page: `https://www.ceec.edu.tw/xmfile?xsmsid=0J052424829869345634`
- source access: public web pages plus linked PDF, DOC, and ZIP files
- source cadence: yearly archive updates with occasional late-file corrections
- authentication: none
- rate-limit posture: keep scheduled sync conservative and prefer the weekly workflow unless a repair run is needed

## Discovery Model

The provider crawls the GSAT archive listing, groups entries by Gregorian year, and turns each archive row into one source exam page.

The 2026-07-29 official snapshot contains 179 event rows across AD 1994–2026. All 179 events are represented locally as 648 normalized records with zero sync failures and zero normalization-review records. The parser accepts both two- and three-digit ROC years because the oldest rows use titles such as `86學年度`.

Listing rows do not expose stable detail-page URLs, so year and event evidence in `data/providers/ceec_gsat/source-manifest.json` points to the official paginated listing. This manifest is a reproducible discovery snapshot, not independent proof that CEEC exposes every historical administration.

One AD 2003 mathematics scoring-principle asset is an official legacy OLE Word document. The shared downloader accepts it only after the `.doc` role and OLE signature both validate; HTML placeholders remain rejected.

Provider-owned outputs live under:

- `data/providers/ceec_gsat/`
- `mirror/providers/ceec_gsat/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-ceec-gsat.yml`

That workflow is provider-only. It refreshes `data/providers/ceec_gsat/` and does not publish the aggregated `default` site on its own.

The primary operator command is:

```bash
python -m app sync-full --provider ceec_gsat --site-id default
```

## Normalization Rules

- all normalized records carry `provider_id = "ceec_gsat"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `ceec-gsat`
  - `canonical_name`: `學科能力測驗`

The provider does not own a public release tag. Release tags are assigned later by site publication.

## Publication Integration

After provider sync completes, publish the `default` site separately when every required provider state and mirror input for that site is available:

```bash
python -m app publish-site --site-id default --repository <owner>/<repo>
```

Canonical site-owned outputs then live under:

- `data/sites/default/bundles.json`
- `data/sites/default/release-assets.json`
- `bundles/sites/default/`

For compatibility during the migration, the `default` site may also refresh legacy root-level outputs such as `data/bundles.json`.
