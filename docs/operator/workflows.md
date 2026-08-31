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
| `sync-<provider>.yml` | scheduled and manual | one provider's source refresh |
| `workflow-health.yml` | completion of any scheduled workflow, daily, and manual | file and resolve health issues |

## Workflow Details

### `sync-incremental.yml`

Use case:

- regular maintenance
- probe-first refresh
- fail-fast protection when release coverage is incomplete

Operator expectations:

- release coverage is checked before targeted sync
- if release coverage is incomplete, the workflow stops and requires manual recovery on a machine with persistent MOEX state
- if probe sees no source change, only the manifest may be committed

Trigger manually when:

- you want the standard maintenance path outside the schedule
- you want automation to decide whether probe-targeted refresh is safe

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

### `sync-<provider>.yml`

Use case:

- refresh one provider's source coverage on its own schedule

Operator expectations:

- a run that could not fetch every file still commits the papers it did fetch
  and records the rest in `data/providers/<provider>/sync-failures.json`; the
  run is still reported as failed so it is visible
- `commit-and-push.sh` gates every such commit on the reviewed source floor, so
  a partial result can never publish a truncated catalog
- clear a recorded failure with
  `python -m app repair-failures --provider <provider>`, which re-fetches only
  the affected source exams
- `sync-taisugar-recruit.yml` is manual-only until its reviewed multi-year
  migration can rebuild the default-site metadata and publish the matching
  release asset in the same operator-controlled change. Do not dispatch it as
  a routine provider refresh.

### `workflow-health.yml`

Use case:

- notice that a scheduled workflow has stopped succeeding

Operator expectations:

- one open issue per unhealthy workflow, labelled `workflow-health`, closed
  automatically as soon as that workflow succeeds again
- the daily run additionally reports any scheduled workflow that has missed two
  consecutive runs, which is what a workflow that stops firing altogether looks
  like. The window follows each workflow's own cron cadence, with a floor of 14
  days: 14 for the weekly syncs, 62 for monthly `audit-recent`. Only a
  `schedule` run clears it, because a manual dispatch proves nothing about
  whether the schedule still fires.

### `deploy-pages.yml`

Use case:

- build and deploy the modern frontend app

Current inputs:

- generated bundles metadata
- frontend app source

Trigger manually when:

- deployment should be rerun without waiting for another push
- you fixed frontend-only deployment issues

## Operator Checks After Workflow Runs

For sync and publication workflows:

1. Check workflow logs for non-zero Python command exits.
2. Check whether `data/` commits were pushed.
3. Check release asset coverage and uploaded ZIP names.
4. Check open issues labelled `workflow-health`; each one names a workflow that
   is failing or has stopped succeeding on its schedule.

For deploy workflows:

1. Check that the frontend build completed.
2. Check that the emitted frontend `data/bundles.json` came from `data/sites/default/bundles.json`.
3. Check the deployed site if bundle links or social-gate behavior changed.

## Current Workflow Ownership Model

The current ownership model is provider-scoped for sync and site-scoped for publication/deploy.

As the repo expands, keep this boundary:

- provider-scoped sync or audit workflows
- site-scoped publication workflows
- site-scoped deploy workflows

## When To Prefer Manual Commands Over Workflows

Prefer local/manual commands when:

- you need to inspect intermediate outputs before publishing
- you are debugging parser or bundle behavior
- you want to repair data without immediately pushing release changes
- you are validating a new provider design before adding CI
