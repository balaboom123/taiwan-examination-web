# Migration Plan

This document turns the target architecture into an executable migration sequence.

It answers four questions:

1. Which current files move first?
2. Which paths dual-write during transition?
3. What are the acceptance criteria for each phase?
4. When is a legacy path allowed to disappear?

## Migration Objectives

- preserve current MOEX publication behavior
- create provider-scoped and site-scoped ownership boundaries
- make source #2 possible without introducing more root-level global state
- make workflows parameterizable by provider or site

## Current-To-Target Path Mapping

| Current path | Target owner | Target path |
| --- | --- | --- |
| `data/exams/*.json` | provider | `data/providers/<provider_id>/exams/*.json` |
| `data/papers/*.json` | provider | `data/providers/<provider_id>/papers/*.json` |
| `data/review-queue.json` | provider | `data/providers/<provider_id>/review-queue.json` |
| `data/sync-failures.json` | provider | `data/providers/<provider_id>/sync-failures.json` |
| `data/source-manifest.json` | provider | `data/providers/<provider_id>/source-manifest.json` |
| `data/aliases.json` | provider | `data/providers/<provider_id>/aliases.json` |
| `mirror/**` | provider | `mirror/providers/<provider_id>/**` |
| `data/bundles.json` | site | `data/sites/<site_id>/bundles.json` |
| `data/release-assets.json` | site | `data/sites/<site_id>/release-assets.json` |
| `data/lootlabs-links.json` | site | `data/sites/<site_id>/lootlabs-links.json` |
| `bundles/**` | site | `bundles/sites/<site_id>/**` |
| frontend build feed | site | `data/sites/<site_id>/frontend-bundles.json` or equivalent build asset |

## Migration Phases

### Phase 1: Introduce scoped ownership in code

Goal:

- make provider and site ownership explicit in code and docs without changing current public behavior

Required work:

- add `provider_id` and `site_id` concepts to command orchestration
- introduce provider-aware and site-aware path builders
- create registry docs for current MOEX/default site ownership

Deliverables:

- current root-level outputs still work
- internal code can resolve scoped target paths
- new docs exist for contracts, migration, registry, and source spec template

Acceptance criteria:

- no current workflow breaks
- no new feature work introduces additional root-level global state

### Phase 2: Dual-write provider state

Goal:

- write provider-owned outputs to both legacy root-level paths and provider-scoped paths

Required work:

- dual-write raw exam pages
- dual-write normalized papers
- dual-write review queue
- dual-write sync failures
- dual-write source manifest
- dual-write alias ownership location if migrated

Acceptance criteria:

- scoped provider outputs match legacy outputs for MOEX
- operator docs explain both locations during transition
- verification proves parity for at least one full sync and one incremental sync

### Phase 3: Dual-write site publication state

Goal:

- write site-owned outputs to both legacy root-level paths and site-scoped paths

Required work:

- dual-write bundle metadata
- dual-write release asset inventory
- dual-write gating manifest
- dual-write frontend bundle feed
- move local ZIP storage into site-aware paths or add a compatibility shim

Acceptance criteria:

- release publication can run using site-scoped metadata
- frontend build can consume site-scoped feed inputs
- current public downloads remain unchanged

### Phase 4: Parameterize workflows

Goal:

- decouple automation from MOEX-only names and global paths

Required work:

- define provider-scoped sync workflows
- define site-scoped publish workflows
- define site-scoped deploy workflows
- move environment variable names toward provider/site scoping

Acceptance criteria:

- at least one workflow can be reasoned about by ownership without reading code
- workflow docs describe provider or site ownership explicitly

### Phase 5: Cut over consumers to scoped paths

Goal:

- make code and workflows read scoped paths as primary inputs

Required work:

- frontend reads site-owned publication outputs
- release asset script reads site-owned release inventory
- gating refresh reads site-owned bundle metadata
- operator runbook uses provider/site terminology by default

Acceptance criteria:

- no primary consumer depends on root-level legacy paths
- scoped paths are the documented default

### Phase 6: Remove legacy compatibility outputs

Goal:

- eliminate root-level global outputs once they are no longer authoritative

Prerequisites:

- provider and site scoped paths have been primary for at least one stable release cycle
- operator docs no longer rely on legacy paths
- recovery steps work with scoped paths only

Acceptance criteria:

- legacy removal has no user-facing regression
- migration cleanup is documented in release notes or repo docs

## First Implementation Order

To get ready for source #2, this is the recommended order:

1. add contract docs and registry
2. implement provider-aware path helpers
3. dual-write provider outputs for MOEX
4. dual-write site outputs for the current site
5. switch frontend build to site-scoped feed input
6. parameterize workflows by provider/site
7. onboard source #2

## Dual-Write Rules

- Dual-write periods MUST be temporary.
- During dual-write, one path MUST be documented as authoritative.
- Parity verification MUST be explicit, not assumed.
- New providers MUST write scoped outputs even if legacy compatibility outputs are still emitted for MOEX.

## Cutover Criteria

A path can stop being primary only when:

- all consuming code reads the scoped replacement
- all workflows use the scoped replacement
- operator docs use the scoped replacement
- verification and recovery procedures have been updated

A legacy path can be removed only when:

- it is no longer the primary or fallback input for any workflow, tool, or operator runbook
- a full sync and deploy cycle succeeded without it

## Risks To Watch

- accidentally keeping root-level outputs authoritative forever
- frontend still depending on global `data/bundles.json`
- release script still assuming one release tag
- gating logic remaining global instead of site-owned
- source #2 reusing MOEX paths "just temporarily" and making migration harder
