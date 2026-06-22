# Provider And Site Registry

This document is the human-readable ownership registry for active and planned providers and sites.

Update this file whenever a provider or site is added, renamed, deprecated, or materially re-scoped.

## Registry Rules

- Every provider MUST have one registry entry.
- Every site MUST have one registry entry.
- Provider IDs and site IDs MUST be stable.
- A provider registry entry MUST identify its owning sync workflow.
- A site registry entry MUST identify its owning release and deploy workflows.

## Active Providers

### Provider: `moex`

| Field | Value |
| --- | --- |
| provider_id | `moex` |
| status | active |
| source name | Ministry of Examination exam archive source |
| source type | public web source |
| current implementation scope | single active provider in repo |
| current raw data ownership | root-level `data/exams/`, `data/papers/`, `data/review-queue.json`, `data/sync-failures.json`, `data/source-manifest.json` |
| target scoped ownership | `data/providers/moex/` |
| current mirror ownership | `mirror/` |
| target mirror ownership | `mirror/providers/moex/` |
| current sync workflows | `sync-incremental.yml`, `sync-full.yml`, `audit-recent.yml`, `discover.yml` |
| current CLI entrypoints | `discover`, `probe-latest`, `sync-targeted`, `sync-incremental`, `sync-full` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | current provider used as migration baseline |

## Planned Providers

Add planned providers here before implementation starts.

### Provider: `ceec_gsat`

| Field | Value |
| --- | --- |
| provider_id | `ceec_gsat` |
| status | planned |
| source name | College Entrance Examination Center GSAT archive |
| source type | public web source |
| current implementation scope | planned same-site provider feeding the existing public catalog |
| target scoped ownership | `data/providers/ceec_gsat/` |
| target mirror ownership | `mirror/providers/ceec_gsat/` |
| planned sync workflows | provider-scoped CEEC sync workflow to be added during migration |
| planned CLI entrypoints | provider-aware sync entrypoint targeting `ceec_gsat` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes exactly one canonical bundle asset for `學科能力測驗`; public publication remains site-owned |

Recommended entry format:

### Provider: `<provider_id>`

| Field | Value |
| --- | --- |
| provider_id | `<provider_id>` |
| status | planned |
| source name | |
| source type | |
| current implementation scope | |
| target scoped ownership | `data/providers/<provider_id>/` |
| target mirror ownership | `mirror/providers/<provider_id>/` |
| planned sync workflows | |
| planned CLI entrypoints | |
| operator docs | |
| notes | |

## Active Sites

### Site: `default`

| Field | Value |
| --- | --- |
| site_id | `default` |
| status | active |
| purpose | current public exam bundle catalog |
| current input providers | `moex` |
| target input providers | `moex`, `ceec_gsat` |
| current publication ownership | root-level `data/bundles.json`, `data/release-assets.json`, `data/lootlabs-links.json` |
| target scoped ownership | `data/sites/default/` |
| current bundle storage | `bundles/` |
| target bundle storage | `bundles/sites/default/` |
| current release tag | `moex-bundles` |
| target release strategy | site-owned publication; one or more release tags; shard before 900 assets |
| current deploy workflows | `deploy-pages.yml` |
| current publish ownership | sync workflows plus `.github/scripts/release_assets.py` |
| current frontend surface | `frontend/` |
| legacy output surface | none |
| gating provider | LootLabs, optional by build/deploy path |
| notes | current site still uses MOEX-shaped naming, needs site-scoped cutover, and will eventually absorb one CEEC bundle asset without splitting the public site |

## Planned Sites

Add planned sites here before implementation starts.

Recommended entry format:

### Site: `<site_id>`

| Field | Value |
| --- | --- |
| site_id | `<site_id>` |
| status | planned |
| purpose | |
| input providers | |
| target scoped ownership | `data/sites/<site_id>/` |
| target bundle storage | `bundles/sites/<site_id>/` |
| release tag | |
| deploy workflows | |
| publish ownership | |
| frontend surface | |
| gating provider | |
| notes | |

## Secret And Integration Registry

Current shared integrations:

| Integration | Current owner | Purpose |
| --- | --- | --- |
| GitHub release token via `GH_TOKEN` | site publication workflows | upload/prune bundle assets |
| `LOOTLABS_API_KEY` | current default site | content-locker link generation |

Future rule:

- secrets SHOULD be documented per site or provider owner instead of assumed global whenever different sites/providers have different credentials or integrations

## Change Control Checklist

When updating this registry, also update:

- `docs/developer/contracts.md` if a contract owner changes
- `docs/developer/migration-plan.md` if the cutover sequence changes
- `docs/developer/source-onboarding.md` if onboarding rules change
- operator docs if workflow ownership or trigger paths change
