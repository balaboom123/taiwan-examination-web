# Operator Runbook

This runbook covers manual operation of the repository in its current state and notes the rules that must remain true as the project expands.

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

Current generated operational paths:

- `mirror/`: mirrored downloaded files
- `bundles/`: locally built ZIP bundles
- `data/`: generated metadata and manifests
- `site/`: generated legacy static output

Manual input:

- `data/aliases.json`

## Common Commands

Run from the repo root.

| Command | Use it when | Main outputs |
| --- | --- | --- |
| `python -m app discover` | you want to inspect current source inventory | stdout JSON |
| `python -m app probe-latest --years 2 --output .tmp/source-probe.json --write-manifest` | you want to check if a recent sync is needed | `.tmp/source-probe.json`, manifest update |
| `python -m app sync-targeted --probe .tmp/source-probe.json --download-affected-bundles --release-tag moex-bundles --bundle-base-url "<url>"` | the probe found changes and you want the minimal refresh path | updated affected bundles and generated data |
| `python -m app sync-incremental --years 2 --write-manifest --bundle-base-url "<url>"` | you want a recent-year refresh without starting from scratch | updated generated state |
| `python -m app sync-full --write-manifest --bundle-base-url "<url>"` | you need a full rebuild or bootstrap | fully regenerated state |
| `python -m app build-bundles --bundle-base-url "<url>"` | raw data is already present and you only need bundle rebuild | rebuilt bundles and release metadata |
| `python -m app build-site` | you only need the legacy site rebuilt | `site/` |
| `python -m app sync-lootlabs` | bundle URLs or bundle checksums changed | `data/lootlabs-links.json` |

Replace `<url>` with the release download base, for example:

```text
https://github.com/<owner>/<repo>/releases/download/moex-bundles
```

## Standard Operating Procedures

### 1. Inspect source inventory

Use:

```bash
python -m app discover
```

Use this before large maintenance changes or when validating source availability.

### 2. Probe recent changes

Use:

```bash
python -m app probe-latest --years 2 --output .tmp/source-probe.json --write-manifest
```

Then inspect `.tmp/source-probe.json`:

- if `should_sync` is `false`, no targeted sync is needed
- if `should_sync` is `true`, continue to targeted sync

### 3. Run targeted sync after a positive probe

Use:

```bash
python -m app sync-targeted ^
  --probe .tmp/source-probe.json ^
  --download-affected-bundles ^
  --release-tag moex-bundles ^
  --bundle-base-url "https://github.com/<owner>/<repo>/releases/download/moex-bundles"
```

Use this when only a known set of exam IDs changed.

### 4. Run incremental maintenance

Use:

```bash
python -m app sync-incremental --years 2 --write-manifest ^
  --bundle-base-url "https://github.com/<owner>/<repo>/releases/download/moex-bundles"
```

Use this for a broader recent-year refresh when you do not already have a probe result or when you want the audit path manually.

### 5. Run a full rebuild

Use:

```bash
python -m app sync-full --write-manifest ^
  --bundle-base-url "https://github.com/<owner>/<repo>/releases/download/moex-bundles"
```

Use this for bootstrap, large repair work, or when incremental state is no longer trusted.

### 6. Rebuild bundles only

Use:

```bash
python -m app build-bundles ^
  --bundle-base-url "https://github.com/<owner>/<repo>/releases/download/moex-bundles"
```

Use this when normalized data is correct but bundle ZIPs or release metadata must be rebuilt.

### 7. Rebuild legacy site only

Use:

```bash
python -m app build-site
```

### 8. Refresh LootLabs links

Use:

```bash
python -m app sync-lootlabs
```

Run this after bundle URLs or bundle checksums change.

## Manual Verification Checklist

After a sync or publication run, check:

1. `data/sync-failures.json`
2. `data/review-queue.json`
3. `data/release-assets.json`
4. `data/lootlabs-links.json` if gating is enabled
5. GitHub release asset coverage if you published bundles
6. `site/` output if legacy site consumers matter
7. frontend build if public deployment behavior changed

Recommended verification commands:

```bash
uv run python -m unittest discover -s tests -q
```

```bash
cd frontend
npm test
npm run build
```

## Expansion Guidance For Operators

As the repo expands:

- provider sync commands SHOULD become provider-scoped
- site publication commands SHOULD become site-scoped
- runbooks MUST explain which provider or site each command owns

Do not rely on MOEX-only names when documenting a new provider or site.
