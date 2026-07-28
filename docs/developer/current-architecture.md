Status: transition snapshot. This page describes the original MOEX-first paths and remains useful for locating legacy files. It is not authoritative for exam identity, bundle purity, or release capacity; use exam-identity-v2.md, contracts.md, and operator/catalog-audit.md for those topics. Do not copy its old single-provider or one-release assumptions into new code.

# Current Architecture

This document describes the repository as it exists today. It is descriptive, not aspirational.

## Scope

The repository has a provider-registry and default-site implementation. Legacy root-level descriptions in this transition document remain for migration context; the current completeness baseline and provider specs are authoritative for scope.

Current major characteristics:

- source/provider: 35 registered providers in the `default` site, with MOEX-specific and provider-specific adapters
- reviewed source scope: `catalog/source-inventory.json`; local drift gate: `scripts/validate_source_inventory.py`
- generated provider data stored under `data/providers/<provider_id>/`
- mirrored files stored under `mirror/providers/<provider_id>/`
- downloadable ZIP bundles stored under `bundles/sites/default/`
- site publication indexes stored under `data/sites/default/`
- modern frontend app stored under `frontend/`
- release assets managed across the default site’s planned `default-bundles-*` shards

## Current Repo Boundaries

| Path | Responsibility |
| --- | --- |
| `app/cli.py` | main command entrypoint and orchestration |
| `app/crawler.py` | MOEX-specific discovery, page fetch, file download |
| `app/sync.py` | mirroring, payload validation, and normalized input preparation |
| `app/state.py` | incremental and targeted merge logic against existing generated state |
| `app/publisher.py` | write generated site-scoped publication JSON files |
| `app/manifest.py` | provider source manifest read/write for probe state |
| `app/probe.py` | probe recent source changes without full download |
| `app/source_inventory.py` | validate reviewed source scope against the provider registry and local state |
| `catalog/source-inventory.json` | reviewed official-source scope/status/evidence input |
| `scripts/validate_source_inventory.py` | CI/operator gate for source-scope and local-state drift |
| `.github/workflows/` | scheduled and manual automation |
| `.github/scripts/release_assets.py` | release asset ensure, coverage, upload, and prune logic |
| `frontend/` | Vite/React frontend consuming generated bundle data |

## Current CLI Surface

These commands are implemented in `python -m app` today:

| Command | Purpose | Typical Output |
| --- | --- | --- |
| `discover` | list available exams for the selected provider grouped by year (MOEX by default) | JSON discovery payload |
| `probe-latest` | cheaply inspect recent source changes | `.tmp/source-probe.json`, optional `data/providers/<provider_id>/source-manifest.json` |
| `sync-targeted` | refresh only exams identified by a probe result | updated generated data and bundles for affected categories |
| `sync-incremental` | refresh a recent year window | updated generated data with safe partial merge |
| `sync-full` | rebuild from the live source | full generated data and bundles |
| `build-bundles` | rebuild ZIP bundles from existing local state only | updated `bundles/sites/default/`, `data/sites/default/bundles.json` |

## Current Generated Data

The current provider/site outputs are scoped as follows:

| Path | Status | Notes |
| --- | --- | --- |
| `data/providers/<provider_id>/exams/YYYY.json` | generated | parsed source exam pages |
| `data/providers/<provider_id>/papers/YYYY.json` | generated | normalized paper records |
| `data/providers/<provider_id>/review-queue.json` | generated | unresolved normalization candidates |
| `data/providers/<provider_id>/sync-failures.json` | generated | download/build failures |
| `data/providers/<provider_id>/source-manifest.json` | generated when a provider supports it | source discovery/probe state; current coverage is incomplete for most providers |
| `data/sites/default/bundles.json` | generated | site publication inventory |
| `data/sites/default/frontend-bundles.json` | generated | frontend feed |
| `data/sites/default/release-assets.json` | generated | expected release asset inventory |
| `catalog/source-inventory.json` | manual reviewed input | official-source scope, status, evidence, and exact local-state observations |
| `data/providers/<provider_id>/aliases.json` | manual provider input | alias rules maintained by developers/operators |

Generated provider and site files must not be manually edited as the implementation mechanism. The reviewed catalog input and aliases are the intentional manual sources of truth.

## Current Publication Surfaces

There is one supported public output surface today:

1. Modern frontend app
   - source code under `frontend/`
   - consumes generated bundle data at build and dev time
   - deploy workflow targets GitHub Pages

## Current End-To-End Flow

1. Provider-specific `discover` or `probe-latest` inspects official availability; the reviewed source inventory records scope and evidence separately.
2. `sync-*` commands fetch exam pages and download files into provider-scoped mirrors.
3. `app/sync.py` validates downloaded payloads and rejects HTML placeholders or wrong binary types.
4. `app/normalizer.py` and alias rules produce normalized paper records.
5. `app/state.py` merges refreshed state with existing generated state for incremental and targeted runs.
6. `app/bundler.py` rebuilds ZIP bundles and canonical bundle metadata.
7. `app/publisher.py` writes generated site-scoped publication JSON outputs.
8. `.github/scripts/release_assets.py` ensures release coverage and publishes bundle ZIP assets.
9. `frontend/` build emits a frontend-friendly `data/bundles.json` feed and deploys the app.
10. Frontend download rows open the configured LINE channel before unlocking ZIP downloads locally.

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
- the frontend feed assumes a single global `data/bundles.json`
- provider behavior is mixed into shared orchestration paths

These limitations are acceptable for the current MOEX system, but they MUST NOT be copied when adding new sources.
