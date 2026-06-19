# Operator Runbook

This runbook covers the provider-scoped sync flow and the site-scoped publication flow used by the current branch.

## Prerequisites

Recommended local tools:

- Python 3.12
- `uv` for running the Python test suite
- Node and npm for `frontend/`
- GitHub CLI `gh` for release operations

Required credentials for release and gating operations:

- `GH_TOKEN`
- `LOOTLABS_API_KEY`

## Generated State You Should Know

Provider-owned generated paths:

- `data/providers/moex/`
- `data/providers/ceec_gsat/`
- `mirror/providers/moex/`
- `mirror/providers/ceec_gsat/`

Site-owned generated paths:

- `data/sites/default/bundles.json`
- `data/sites/default/release-assets.json`
- `data/sites/default/lootlabs-links.json`
- `bundles/sites/default/`

Public site output:

- `site/`

Manual input:

- `data/aliases.json`

## Common Commands

Run from the repo root.

| Command | Use it when | Main outputs |
| --- | --- | --- |
| `python -m app discover --provider moex` | you want to inspect MOEX source inventory | stdout JSON |
| `python -m app probe-latest --provider moex --years 2 --manifest data/providers/moex/source-manifest.json --output .tmp/source-probe.json --write-manifest` | you want to check if recent MOEX data changed | `.tmp/source-probe.json`, `data/providers/moex/source-manifest.json` |
| `python -m app sync-targeted --provider moex --probe .tmp/source-probe.json --manifest data/providers/moex/source-manifest.json` | the MOEX probe found changes and you want the smallest repair path | refreshed MOEX provider state |
| `python -m app sync-incremental --provider moex --years 2 --write-manifest --manifest data/providers/moex/source-manifest.json` | you want a broader recent-year MOEX refresh | refreshed MOEX provider state |
| `python -m app sync-full --provider moex --write-manifest --manifest data/providers/moex/source-manifest.json` | you need a full MOEX rebuild | full MOEX provider refresh |
| `python -m app sync-full --provider ceec_gsat --site-id default` | you want the CEEC GSAT provider refreshed | refreshed CEEC provider state only |
| `python -m app migrate-legacy-state --provider moex --site-id default --mode dry-run` | you are preparing the final root-to-scoped cutover and want a non-mutating inventory first | stdout migration plan only |
| `python -m app migrate-legacy-state --provider moex --site-id default --mode move` | reader and workflow cutover is ready and you want to promote existing root state in place without re-downloading | `data/providers/moex/*`, `data/sites/default/*`, `mirror/providers/moex/*`, `bundles/sites/default/*` |
| `python -m app migrate-legacy-state --provider moex --site-id default --mode verify` | you already promoted legacy state and need a pass/fail safety check before deleting the old root files | stdout verification report |
| `python -m app publish-site --site-id default --repository <owner>/<repo>` | provider state is ready and you need site bundles, release metadata, and site output rebuilt | `data/sites/default/*`, `bundles/sites/default/`, `site/` |
| `python -m app sync-lootlabs --site-id default` | site bundle URLs or checksums changed | `data/sites/default/lootlabs-links.json` |
| `python .github/scripts/release_assets.py ensure` | site publication wrote new release metadata and tags may need bootstrapping | GitHub Releases only |
| `python .github/scripts/release_assets.py upload` | local bundle ZIPs need to be uploaded to their assigned release tags | GitHub Releases only |
| `python .github/scripts/release_assets.py prune` | stale ZIP assets may remain on one or more release tags | GitHub Releases only |

## Standard Operating Procedures

### 1. Probe recent MOEX changes

Use:

```bash
python -m app probe-latest --provider moex --years 2 ^
  --manifest data/providers/moex/source-manifest.json ^
  --output .tmp/source-probe.json ^
  --write-manifest
```

Then inspect `.tmp/source-probe.json`:

- if `should_sync` is `false`, stop
- if `should_sync` is `true`, continue to targeted sync

### 2. Run targeted MOEX sync after a positive probe

Use:

```bash
python -m app sync-targeted ^
  --provider moex ^
  --probe .tmp/source-probe.json ^
  --manifest data/providers/moex/source-manifest.json
```

Use this when only a known MOEX subset changed.

### 3. Refresh CEEC GSAT provider data

Use:

```bash
python -m app sync-full --provider ceec_gsat --site-id default
```

This command does not publish the aggregated `default` site or update release assets by itself.

Expected provider outputs:

- `data/providers/ceec_gsat/exams/*.json`
- `data/providers/ceec_gsat/papers/*.json`
- `data/providers/ceec_gsat/review-queue.json`
- `mirror/providers/ceec_gsat/**`

### 4. Publish the default site

Use:

```bash
python -m app publish-site --site-id default --repository <owner>/<repo>
```

Expected site outputs:

- `data/sites/default/bundles.json`
- `data/sites/default/release-assets.json`
- `data/sites/default/lootlabs-links.json` after a LootLabs sync
- `bundles/sites/default/*.zip`

### 5. Promote legacy root state during the final cutover

Use this only for the scoped-path migration window. It is not part of the normal daily sync pipeline.

Run in this order:

```bash
python -m app migrate-legacy-state --provider moex --site-id default --mode dry-run
python -m app migrate-legacy-state --provider moex --site-id default --mode move
python -m app migrate-legacy-state --provider moex --site-id default --mode verify
```

Interpretation:

- `dry-run` is non-mutating and lists every legacy file that would move or copy
- `move` promotes existing root state into provider/site scope without redownloading mirror or bundle artifacts
- `verify` must pass before deleting the old root files

Important:

- `data/aliases.json` is copied into provider scope in this phase because it is still treated as manual input
- the command rewrites site bundle metadata from `bundles/<asset>` to `bundles/sites/default/<asset>`
- the reader and workflow cutover is already complete on this branch, so `move` is now the last preparation step before root-file cleanup

### 6. Sync LootLabs links

Use:

```bash
python -m app sync-lootlabs --site-id default
```

Run this after `publish-site` when site bundle URLs or checksums changed.

## Manual Verification Checklist

After a sync or publication run, check:

1. `data/providers/<provider_id>/sync-failures.json`
2. `data/providers/<provider_id>/review-queue.json`
3. `data/sites/default/release-assets.json`
4. `data/sites/default/lootlabs-links.json` if gating is enabled
5. `python -m app migrate-legacy-state --provider moex --site-id default --mode verify` during the final cutover window
6. GitHub release asset coverage if you published bundles
7. `site/` output if legacy site consumers matter
8. frontend build if public deployment behavior changed

Recommended verification commands:

```bash
uv run pytest -q
```

```bash
node --test frontend/build/bundles-data.test.mjs
```

```bash
cmd /c "cd /d frontend && npm run build"
```
