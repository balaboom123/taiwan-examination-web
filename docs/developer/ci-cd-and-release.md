# CI/CD And Release

This document defines the current workflow behavior and the rules future automation MUST follow.

## Principles

- provider sync and site publication are separate concerns
- workflows MUST be idempotent
- release state MUST be derived from generated metadata
- deploy workflows MUST consume publication outputs, not raw provider state
- new workflows MUST be scoped to a provider or site instead of mutating global state by default

## Current Workflows

### `sync-incremental.yml`

Purpose:

- scheduled maintenance path for recent-source refresh
- bootstrap the release with a full sync if release coverage is incomplete

Current behavior:

- ensures the release exists
- checks release coverage
- runs `probe-latest` when bootstrap is not required
- commits refreshed source manifest when probe finds no changes
- runs `sync-targeted` when probe reports changes
- uploads and prunes release assets
- refreshes LootLabs links
- commits regenerated `data/` and `site/`

### `sync-full.yml`

Purpose:

- manual full rebuild and publication path

Current behavior:

- runs `sync-full`
- ensures the release exists
- uploads and prunes release assets
- refreshes LootLabs links
- commits regenerated `data/` and `site/`

### `audit-recent.yml`

Purpose:

- scheduled recent-year audit

Current behavior:

- ensures the release exists
- checks release coverage
- downloads current release bundles when possible
- runs either bootstrap full sync or recent-year incremental sync
- uploads and prunes release assets
- refreshes LootLabs links
- commits audited `data/` and `site/`

### `discover.yml`

Purpose:

- manual discovery artifact generation

Current behavior:

- runs `discover`
- uploads `discover.json` as an artifact

### `deploy-pages.yml`

Purpose:

- build and deploy the modern frontend app

Current behavior:

- checks out repo
- refreshes LootLabs links before build
- builds `frontend/`
- emits frontend `data/bundles.json` during the build
- deploys `frontend/dist` to GitHub Pages

## Current Release Script

`.github/scripts/release_assets.py` is the current release authority for ZIP assets.

It provides four operations:

- `ensure`: create the release if it does not exist
- `coverage`: compare expected and actual ZIP assets
- `upload`: publish local ZIPs to the release
- `prune`: delete stale ZIP assets from the release

Current assumptions:

- one release tag
- one generated `data/release-assets.json`
- one bundle namespace

These assumptions MUST be removed before multiple sites publish independent bundle sets.

## Current Secrets And External Dependencies

Current workflows rely on:

- `GH_TOKEN` or `github.token`
- `LOOTLABS_API_KEY`
- `gh` CLI for release asset management
- Python 3.12
- Node for `frontend/`

## Target Workflow Model

Future workflows SHOULD fall into these categories:

### Provider sync workflows

Responsibilities:

- discovery
- probe
- provider-scoped sync
- provider-scoped manifest maintenance

Naming pattern:

- `sync-<provider_id>.yml`
- `audit-<provider_id>.yml`
- `discover-<provider_id>.yml`

### Site publication workflows

Responsibilities:

- build bundles for a site
- publish release assets for a site
- refresh optional gating manifests for a site
- commit or store site publication outputs

Naming pattern:

- `publish-<site_id>.yml`

### Site deploy workflows

Responsibilities:

- build frontend or static site for one site
- deploy to GitHub Pages, Netlify, or another target

Naming pattern:

- `deploy-<site_id>.yml`

## Required Rules For New Automation

- A workflow MUST declare which provider or site it owns.
- A workflow MUST NOT mutate another provider's manifest, mirror, bundle, or release state.
- New workflows MUST prefer generic environment variable names or site/provider-scoped names over hard-coded MOEX names.
- Release tags MUST be site-scoped in the target architecture.
- Gating refresh MUST happen after bundle metadata is finalized, never before.
- Deploy workflows MUST use site-owned publication data as input.

## Migration Guidance

Before adding a second provider or site, the repo SHOULD first:

1. separate provider-owned and site-owned generated paths
2. parameterize release tag ownership
3. make frontend build inputs site-scoped
4. update operator docs for new workflow names and trigger points

## Workflow Definition Of Done

A new or modified workflow is not done until:

- ownership scope is documented
- required secrets are documented
- operator trigger rules are documented
- failure and recovery paths are documented
- tests or validation commands are updated
