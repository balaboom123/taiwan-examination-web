# Provider Spec: `rcpet_cap`

## Summary

- `provider_id`: `rcpet_cap`
- status: active
- target site: `default`
- source family: Research Center for Psychological and Educational Testing CAP archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

- source domain: `cap.rcpet.edu.tw`
- source URL: `https://cap.rcpet.edu.tw/examination.html`
- source access: public web pages; exam papers hosted as Google Drive links
- source cadence: yearly archive updates after each May examination administration
- authentication: none
- rate-limit posture: conservative scheduled sync; the main page loads per-year content into an iframe via a `<select>` dropdown

## Discovery Model

The main `examination.html` page contains a `<select id="exam">` dropdown whose `<option>` values point to per-year iframe pages at `exam/{roc_year}/{roc_year}exam.html`. The provider parses this dropdown for year discovery, then fetches each year page to extract subject links.

Year range: ROC 102–115 (2013–2026), plus a special `111c` reference test entry.

Years with special status:

- 民國 102 (2013): pilot program (試辦) materials only
- 民國 111 (2022): includes supplementary reference test (參考試題) materials

Subjects per exam year (six total):

| Subject key | Chinese name |
|-------------|-------------|
| `writing`   | 寫作測驗     |
| `chinese`   | 國文         |
| `english`   | 英語         |
| `math`      | 數學         |
| `social`    | 社會         |
| `science`   | 自然         |

Provider-owned outputs live under:

- `data/providers/rcpet_cap/`
- `mirror/providers/rcpet_cap/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-rcpet-cap.yml`

That workflow is provider-only. It refreshes `data/providers/rcpet_cap/` and does not publish the aggregated `default` site on its own.

The primary operator command is:

```bash
python -m app sync-full --provider rcpet_cap --site-id default
```

## Normalization Rules

- all normalized records carry `provider_id = "rcpet_cap"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `rcpet-cap`
  - `canonical_name`: `國中教育會考`
- year values stored as Gregorian integers; the ROC year is derived (Gregorian − 1911)
- the pilot year (2013) is tagged `pilot: true` in metadata

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
