# Operator Workflow Guide

This document explains what the automated GitHub Actions workflows do, when operators should trigger them manually, and what to check afterward.

## Current Workflow Inventory

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `sync-incremental.yml` | scheduled and manual | normal recent-source maintenance |
| `sync-full.yml` | manual | full rebuild and publication |
| `audit-recent.yml` | scheduled and manual | recent-year audit and repair |
| `discover.yml` | manual | discovery artifact generation |
| `deploy-pages.yml` | push to `main` for selected paths and manual | frontend build and deploy |

## Workflow Details

### `sync-incremental.yml`

Use case:

- regular maintenance
- probe-first refresh
- automatic bootstrap when release coverage is incomplete

Operator expectations:

- release coverage is checked before targeted sync
- if release coverage is incomplete, the workflow runs a full bootstrap instead of targeted sync
- if probe sees no source change, only the manifest may be committed

Trigger manually when:

- you want the standard maintenance path outside the schedule
- you want automation to decide between probe-targeted refresh and bootstrap

### `sync-full.yml`

Use case:

- force a full rebuild
- recover from broad state distrust
- bootstrap after structural changes

Trigger manually when:

- targeted or incremental logic is no longer sufficient
- release or bundle metadata needs a clean rebuild

### `audit-recent.yml`

Use case:

- re-audit recent years
- compare current release coverage with expected bundle inventory

Trigger manually when:

- scheduled maintenance passed but you still suspect recent drift
- you want the audit behavior without waiting for the schedule

### `discover.yml`

Use case:

- inspect current discovery output without mutating state

Trigger manually when:

- planning a sync
- validating source inventory changes
- investigating whether the source itself changed

### `deploy-pages.yml`

Use case:

- build and deploy the modern frontend app

Current inputs:

- generated bundles metadata
- current LootLabs manifest when gating is enabled
- frontend app source

Trigger manually when:

- deployment should be rerun without waiting for another push
- you fixed frontend-only deployment issues

## Operator Checks After Workflow Runs

For sync and publication workflows:

1. Check workflow logs for non-zero Python command exits.
2. Check whether `data/` and `site/` commits were pushed.
3. Check release asset coverage and uploaded ZIP names.
4. Check LootLabs refresh step if enabled.

For deploy workflows:

1. Check that the frontend build completed.
2. Check that `data/bundles.json` was emitted into the build artifact.
3. Check the deployed site if bundle links or gating behavior changed.

## Current Workflow Ownership Model

Today the ownership model is still global and MOEX-centric.

As the repo expands, the workflow model MUST become:

- provider-scoped sync or audit workflows
- site-scoped publication workflows
- site-scoped deploy workflows

## When To Prefer Manual Commands Over Workflows

Prefer local/manual commands when:

- you need to inspect intermediate outputs before publishing
- you are debugging parser or bundle behavior
- you want to repair data without immediately pushing release changes
- you are validating a new provider design before adding CI
