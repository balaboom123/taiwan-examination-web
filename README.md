# Taiwan Examination Web

Mirror, normalize, and publish past exam papers from the MOEX exam search site.

## What This Repo Produces

- `data/exams.raw.json`: parsed source exam pages
- `data/papers.json`: normalized paper records
- `data/bundles.json`: canonical bundle metadata
- `data/review-queue.json`: category names that still need alias review
- `data/sync-failures.json`: download or bundle failures
- `data/aliases.json`: manual alias rules for cross-year name normalization
- `data/release-assets.json`: expected GitHub Release bundle assets
- `data/source-manifest.json`: probe fingerprints for cheap incremental checks
- `site/index.html`: minimal searchable static site
- `bundles/*.zip`: human-friendly multi-year bundle archives

## Commands

```bash
python -m app discover
python -m app probe-latest --years 2 --output .tmp/source-probe.json --write-manifest
python -m app sync-targeted --probe .tmp/source-probe.json
python -m app sync-incremental --years 1
python -m app sync-full --write-manifest
python -m app build-site
```

## Workflow Strategy

- `probe-latest` checks the newest years first and updates `data/source-manifest.json` only when `--write-manifest` is passed.
- `sync-targeted` refreshes only exams reported by the probe result.
- `sync-incremental` is the compatibility wrapper used by the audit workflow.
- `sync-full` is the recovery and bootstrap path that rebuilds the full dataset.
- Mirror validation rejects HTML placeholder downloads and repairs stale `.ashx` siblings when a valid `.pdf` or `.zip` is fetched again.

The scheduled `sync-incremental` GitHub Actions workflow behaves in two modes:

1. If the release already has the exact expected zip asset set, it runs probe-first targeted sync.
2. If the release is empty or incomplete, it falls back to a full sync bootstrap so the release cannot get stuck with only a small subset of bundles.

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

The full test suite runs with:

```bash
uv run python -m unittest discover -s tests -q
```
