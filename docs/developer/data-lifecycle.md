# Data Lifecycle

This document defines the source-to-publication lifecycle, the integrity checks at each stage, and the write behavior of current commands.

## Lifecycle Overview

The current and future lifecycle is:

1. discover source inventory
2. probe for recent changes
3. fetch pages and download files
4. validate and mirror payloads
5. normalize provider data into shared catalog records
6. merge refreshed state with existing published state
7. build bundles and release metadata
8. upload/prune release assets
9. publish frontend outputs
10. apply frontend social-gated download behavior

## Stage Details

### 1. Discovery

Current behavior:

- `discover` asks MOEX for available years and exam codes.
- discovery is read-only and produces JSON output for inspection.

Future rule:

- each provider MUST have a provider-scoped discovery entrypoint
- discovery MUST NOT mutate publication state

### 2. Probe

Current behavior:

- `probe-latest` uses `data/source-manifest.json`
- it compares current year or exam HEAD responses to prior manifest entries
- it fetches full exam pages only when a HEAD comparison indicates change

Integrity properties:

- cheap change detection
- minimized download volume
- explicit `should_sync` decision in `.tmp/source-probe.json`

Future rule:

- each provider MUST own its own source manifest
- probe manifests MUST be provider-scoped, not global

### 3. Fetch and mirror

Current behavior:

- `sync-*` commands download source files into `mirror/`
- mirror paths are built from year, exam ID, category, subject, and file type
- existing mirrored files are reused when valid

Integrity properties:

- mirror files receive SHA-256 checksums
- invalid payloads are redownloaded
- stale sibling files with wrong extensions are removed after successful refresh

Future rule:

- mirror roots MUST be provider-scoped
- source download logic MUST remain separate from site publication logic

### 4. Payload validation

Current behavior:

- PDF files are validated by signature
- ZIP files are validated by signature
- HTML placeholders are rejected
- wrong binary type for a known file type is treated as failure

Why this matters:

- source systems sometimes return an HTML page or placeholder instead of the file
- bundle generation MUST NOT consume invalid mirrored content

## Reviewed Source-Coverage Exceptions

Manual source evidence belongs in `catalog/source-coverage/<provider_id>.json`, not in generated provider state. An entry may be event-scoped (`blocked` or `intentionally_out_of_scope`) or file-scoped (`blocked`). Each entry records the official URL, capture date, response fingerprint, observation, and reason.

`history-audit` matches event entries to the current raw event and file entries to the exact current download failure: provider, exam ID, AD year, paper code, file type, download URL, and `download` stage must all agree. An event exception conflicts if the current raw page has papers or attachments, normalized records exist, or any failure is recorded. An unmatched exception is an orphan. Both conditions fail strict audit. The publication validator ignores only exact file exceptions; all other provider failures remain blocking.

A reviewed exception is therefore an evidence-backed denominator decision, not a generated-manifest shortcut. When the source changes or a file becomes available, the old entry becomes an orphan or conflict and must be removed or re-probed.

### 5. Normalize

Current behavior:

- provider raw pages become `NormalizedPaper` records
- `data/aliases.json` is applied during normalization
- unresolved naming cases are emitted to `data/review-queue.json`

Future rule:

- alias rules SHOULD be provider-scoped unless a site explicitly owns cross-provider canonicalization
- normalized schema MUST remain source-agnostic

### 6. Merge refreshed state

Current behavior:

- full sync writes a complete regenerated state
- incremental sync merges refreshed state into existing generated state
- targeted sync merges only probe-identified exams
- canonical ID migrations are derived when refreshed records rename a prior category family

Why this matters:

- unaffected bundles should stay stable
- recent refreshes should not force full rebuilds
- canonical renames should not orphan prior records

### 7. Build bundles

Current behavior:

- bundle generation reads normalized papers and mirrored files
- generated bundle metadata is written to `data/bundles.json`
- release asset inventory is written to `data/release-assets.json`
- legacy alias asset names may be preserved for compatibility

Future rule:

- bundle outputs MUST be site-scoped
- release asset inventory MUST belong to the site that publishes those bundles

### 8. Release synchronization

Current behavior:

- `.github/scripts/release_assets.py` ensures the GitHub release exists
- coverage compares expected ZIP names to release ZIP names
- upload publishes local bundles
- prune removes stale ZIP assets not present in the current expected set

Integrity properties:

- release state is derived from generated metadata, not manual memory
- compatibility alias assets remain published when listed in generated metadata

### 9. Public output

Current behavior:

- `app.publisher.publish_site` writes site-scoped publication metadata under `data/sites/<site_id>/`
- the frontend build emits a frontend-specific `data/bundles.json` feed from publication data

Future rule:

- public outputs MUST be site-scoped
- frontend feed generation MUST consume publication outputs, never raw provider state

### 10. Frontend social gate

Current behavior:

- generated bundle feeds keep direct ZIP URLs
- the frontend download row opens a category-specific LINE channel before unlocking ZIP downloads locally

Future rule:

- provider and publication commands MUST NOT depend on frontend download gating to complete ingestion or release publication

## Current Write Behavior By Command

| Command | Writes generated data? | Partial writes allowed? | Failure semantics |
| --- | --- | --- | --- |
| `discover` | no | n/a | read-only |
| `probe-latest` | yes, only output file and optional manifest | yes | returns a probe result even when no sync is needed |
| `sync-targeted` | yes, if successful; `--allow-partial` may commit the valid subset | no by default; explicit partial mode is opt-in | default aborts on any failure; partial mode retains successful records and failure rows, returns non-zero, and requires follow-up audit/publication |
| `sync-incremental` | yes | yes, safe subset only | preserves existing state for failed exam IDs and returns non-zero if failures remain |
| `sync-full` | yes | yes | writes full regenerated outputs and returns non-zero if failures remain |
| `build-bundles` | yes | no | local rebuild path; returns non-zero if failures exist |

## Generated Versus Manual Inputs

Manual inputs today:

- `data/aliases.json`
- `catalog/source-coverage/<provider_id>.json` reviewed evidence for blocked or intentionally excluded official sources

Generated outputs today:

- `data/exams/**`
- `data/papers/**`
- `data/bundles.json`
- `data/review-queue.json`
- `data/sync-failures.json`
- `data/source-manifest.json`
- `data/release-assets.json`
- `data/sites/<site_id>/*` publication indexes

Operators and developers MUST treat generated outputs as derived state. Manual edits to generated files are temporary recovery actions only and MUST be followed by a rebuilding command or code fix.

## Expansion Rules

- New providers MUST own their own manifests, review queues, failure logs, and source-coverage evidence where an official source is blocked or intentionally excluded.
- New sites MUST own their own bundle metadata and release asset inventory.
- Shared schemas MAY evolve, but provider-specific fields MUST NOT leak into site-facing bundle feeds without an explicit contract update.
