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

Compatibility outputs still refreshed for the `default` site:

- `data/bundles.json`
- `data/release-assets.json`
- `data/lootlabs-links.json`
- `site/`

Manual input:

- `data/aliases.json`

## Common Commands

Run from the repo root.

| Command | Use it when | Main outputs |
| --- | --- | --- |
| `python -m app discover --provider moex` | you want to inspect MOEX source inventory | stdout JSON |
| `python -m app probe-latest --provider moex --years 2 --manifest data/providers/moex/source-manifest.json --output .tmp/source-probe.json --write-manifest` | you want to check if recent MOEX data changed | `.tmp/source-probe.json`, `data/providers/moex/source-manifest.json` |
| `python -m app sync-targeted --provider moex --probe .tmp/source-probe.json --download-affected-bundles` | the MOEX probe found changes and you want the smallest repair path | refreshed MOEX provider state plus compatibility outputs |
| `python -m app sync-incremental --provider moex --years 2 --write-manifest --manifest data/providers/moex/source-manifest.json` | you want a broader recent-year MOEX refresh | refreshed MOEX provider state plus compatibility outputs |
| `python -m app sync-full --provider moex --write-manifest --manifest data/providers/moex/source-manifest.json` | you need a full MOEX rebuild | full MOEX provider refresh plus compatibility outputs |
| `python -m app sync-full --provider ceec_gsat --site-id default` | you want the CEEC GSAT provider refreshed | refreshed CEEC provider state only |
| `python -m app publish-site --site-id default --repository <owner>/<repo>` | provider state is ready and you need site bundles, release metadata, and site output rebuilt | `data/sites/default/*`, `bundles/sites/default/`, compatibility site outputs |
| `python -m app sync-lootlabs --site-id default` | site bundle URLs or checksums changed | `data/sites/default/lootlabs-links.json` plus compatibility copy |
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
  --download-affected-bundles
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

### 5. Sync LootLabs links

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
5. GitHub release asset coverage if you published bundles
6. `site/` output if legacy site consumers matter
7. frontend build if public deployment behavior changed

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
