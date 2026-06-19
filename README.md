# Taiwan Examination Web

Mirror, normalize, and publish past exam papers into one public `default` site fed by provider-scoped sync pipelines.

## What This Repo Produces

Provider-owned state:

- `data/providers/moex/`: parsed MOEX exams, normalized papers, failures, and manifest state
- `data/providers/ceec_gsat/`: parsed CEEC GSAT exams, normalized papers, failures, and manifest state
- `mirror/providers/<provider_id>/`: mirrored source files per provider

Site-owned publication state:

- `data/sites/default/bundles.json`: canonical bundle metadata for the public site
- `data/sites/default/release-assets.json`: expected GitHub Release assets grouped by site-owned release tag
- `data/sites/default/lootlabs-links.json`: gated public download links for the site
- `bundles/sites/default/*.zip`: human-friendly multi-year bundle archives

Compatibility outputs kept during migration:

- `data/bundles.json`
- `data/release-assets.json`
- `data/lootlabs-links.json`
- `site/index.html`

Manual input:

- `data/aliases.json`

## Commands

```bash
python -m app probe-latest --provider moex --years 2 --manifest data/providers/moex/source-manifest.json --output .tmp/source-probe.json --write-manifest
python -m app sync-targeted --provider moex --probe .tmp/source-probe.json --download-affected-bundles
python -m app sync-incremental --provider moex --years 2 --write-manifest --manifest data/providers/moex/source-manifest.json
python -m app sync-full --provider moex --write-manifest --manifest data/providers/moex/source-manifest.json
python -m app sync-full --provider ceec_gsat --site-id default
python -m app publish-site --site-id default --repository <owner>/<repo>
python -m app sync-lootlabs --site-id default
```

## Workflow Strategy

- Provider sync owns discovery, source parsing, mirrored files, normalized papers, manifests, and sync failures.
- Site publication owns bundle ZIPs, release asset manifests, LootLabs link manifests, and the public site output.
- `probe-latest` checks the newest MOEX years first and updates the provider manifest only when `--write-manifest` is passed.
- `sync-targeted` refreshes only exams reported by the MOEX probe result.
- `sync-incremental` is the compatibility wrapper used by the audit workflow.
- `sync-full` is the recovery and bootstrap path for a selected provider.
- `publish-site` aggregates all providers assigned to the `default` site and assigns deterministic site-owned release tags.
- Mirror validation rejects HTML placeholder downloads and repairs stale `.ashx` siblings when a valid `.pdf` or `.zip` is fetched again.

The scheduled `sync-incremental` GitHub Actions workflow behaves in two modes:

1. If the default site's assigned release tags already have the exact expected zip asset set, it runs probe-first targeted sync.
2. If the assigned releases are empty or incomplete, it falls back to a full sync bootstrap so publication cannot get stuck with only a small subset of bundles.

## Bundle Format

- `mirror/` stays code-based so crawl outputs remain stable and easy to diff.
- Bundle filenames use Chinese display names plus canonical IDs.
- Release assets can include legacy compatibility alias names during migration.
- Archive entry paths stay human-readable while retaining the original source codes.
- Machine-readable metadata stays in `bundle.json` inside each zip.

Example:

- Bundle asset: `護理師__nurse.zip`
- Legacy alias asset: `nurse.zip`
- Archive entry: `115/115030_護理師/101_0101_基礎醫學_試題.pdf`

## Alias Rules

Use `data/aliases.json` to merge cross-year naming variants into the same canonical bucket.

Example:

```json
{
  "rules": [
    {
      "match_type": "exact",
      "raw_pattern": "some raw category",
      "canonical_id": "nurse",
      "canonical_name": "Nurse"
    }
  ]
}
```

## Verification

Python:

```bash
uv run pytest -q
```

Frontend bundle-data tests:

```bash
node --test frontend/build/bundles-data.test.mjs
```
