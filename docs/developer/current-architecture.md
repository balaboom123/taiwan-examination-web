# Current Architecture

This document describes the repository as it exists today. It is descriptive, not aspirational.

## Scope

The current implementation is a single-provider, mostly single-site system centered on MOEX exam content.

Current major characteristics:

- source/provider: MOEX
- generated data stored under root-level `data/`
- mirrored files stored under `mirror/`
- downloadable ZIP bundles stored under `bundles/`
- modern frontend app stored under `frontend/`
- release assets managed on one GitHub release tag, currently `moex-bundles`

## Current Repo Boundaries

| Path | Responsibility |
| --- | --- |
| `app/cli.py` | main command entrypoint and orchestration |
| `app/crawler.py` | MOEX-specific discovery, page fetch, file download |
| `app/sync.py` | mirroring, payload validation, and normalized input preparation |
| `app/state.py` | incremental and targeted merge logic against existing generated state |
| `app/publisher.py` | write generated site-scoped publication JSON files |
| `app/lootlabs.py` | create and refresh LootLabs content-locker links |
| `app/manifest.py` | source manifest read/write for probe state |
| `app/probe.py` | probe recent source changes without full download |
| `.github/workflows/` | scheduled and manual automation |
| `.github/scripts/release_assets.py` | release asset ensure, coverage, upload, and prune logic |
| `frontend/` | Vite/React frontend consuming generated bundle data |

## Current CLI Surface

These commands are implemented in `python -m app` today:

| Command | Purpose | Typical Output |
| --- | --- | --- |
| `discover` | list available MOEX exams grouped by year | JSON discovery payload |
| `probe-latest` | cheaply inspect recent source changes | `.tmp/source-probe.json`, optional `data/source-manifest.json` |
| `sync-targeted` | refresh only exams identified by a probe result | updated generated data and bundles for affected categories |
| `sync-incremental` | refresh a recent year window | updated generated data with safe partial merge |
| `sync-full` | rebuild from the live source | full generated data and bundles |
| `build-bundles` | rebuild ZIP bundles from existing local state only | updated `bundles/`, `data/bundles.json` |
| `sync-lootlabs` | create or refresh LootLabs links for bundle downloads | `data/lootlabs-links.json` |

## Current Generated Data

The repo currently writes these root-level artifacts:

| Path | Status | Notes |
| --- | --- | --- |
| `data/exams/YYYY.json` | generated | parsed source exam pages |
| `data/papers/YYYY.json` | generated | normalized paper records |
| `data/bundles.json` | generated | canonical bundle metadata used by publication layers |
| `data/review-queue.json` | generated | unresolved normalization candidates |
| `data/sync-failures.json` | generated | download/build failures |
| `data/source-manifest.json` | generated | probe state for cheap incremental checks |
| `data/release-assets.json` | generated | expected release asset inventory |
| `data/lootlabs-links.json` | generated | current LootLabs link manifest |
| `data/aliases.json` | manual input | alias rules maintained by developers/operators |

`data/aliases.json` is the only intended manual normalization input in the current `data/` tree. Everything else is generated.

## Current Publication Surfaces

There is one supported public output surface today:

1. Modern frontend app
   - source code under `frontend/`
   - consumes generated bundle data at build and dev time
   - deploy workflow targets GitHub Pages

## Current End-To-End Flow

1. `discover` or `probe-latest` inspects MOEX availability.
2. `sync-*` commands fetch exam pages and download files into `mirror/`.
3. `app/sync.py` validates downloaded payloads and rejects HTML placeholders or wrong binary types.
4. `app/normalizer.py` and alias rules produce normalized paper records.
5. `app/state.py` merges refreshed state with existing generated state for incremental and targeted runs.
6. `app/bundler.py` rebuilds ZIP bundles and canonical bundle metadata.
7. `app/publisher.py` writes generated site-scoped publication JSON outputs.
8. `.github/scripts/release_assets.py` ensures release coverage and publishes bundle ZIP assets.
9. `sync-lootlabs` wraps bundle URLs with current LootLabs links.
10. `frontend/` build emits a frontend-friendly `data/bundles.json` feed and deploys the app.

## Current Automation

Current workflows:

- `sync-incremental.yml`: scheduled incremental sync with probe-first behavior and release bootstrap fallback
- `sync-full.yml`: manual full rebuild
- `audit-recent.yml`: scheduled audit of recent years
- `discover.yml`: manual discovery artifact generation
- `deploy-pages.yml`: build and deploy the frontend app to GitHub Pages

## Current Single-Source Assumptions

These are the main structural limitations that MUST be removed over time:

- most generated state is unscoped root-level state in `data/`
- workflow names and environment variables are MOEX-specific
- one release tag owns all published bundles
- one LootLabs manifest is assumed for the full publication set
- the frontend feed assumes a single global `data/bundles.json`
- provider behavior is mixed into shared orchestration paths

These limitations are acceptable for the current MOEX system, but they MUST NOT be copied when adding new sources.
