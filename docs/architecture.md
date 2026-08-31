# Architecture

This document describes the implemented system in present tense. Normative identity and field rules live in [exam identity](reference/exam-identity.md) and [contracts](reference/contracts.md); accepted rationale lives in [decisions](decisions/).

## Ownership model

The repository separates official-source ingestion from public-site publication:

```text
official sources
  -> provider discovery, fetch, validation, normalization
  -> data/providers/<provider_id>/ + mirror/providers/<provider_id>/
  -> site selection and bundle construction
  -> data/sites/<site_id>/ + bundles/sites/<site_id>/
  -> release shards + frontend build
```

Providers own discovery, source parsing, mirror keys, normalized records, review queues, manifests, and failures. Sites own provider membership, bundle selection, release-shard assignment, public feeds, and deployment behavior.

## Executable boundaries

| Owner | Responsibility |
| --- | --- |
| `app/providers/registry.py` | runtime provider membership |
| `app/site_registry.py` | site membership and publication policy |
| `catalog/source-inventory.json` | reviewed provider/candidate scope and observed source state |
| `app/cli.py` | orchestration and command surface |
| `app/sync.py`, `app/state.py`, `app/manifest.py` | provider fetch, merge, and discovery state |
| `app/classification.py`, `catalog/`, `schemas/` | deterministic identity and serialized contracts |
| `app/bundler.py`, `app/publisher.py`, `app/release_tags.py` | site bundles, feeds, and deterministic release shards |
| `.github/workflows/` | provider sync, audits, publication, and deploy automation |
| `frontend/` | presentation over generated site data |

## Stored state

Provider-generated state is scoped under `data/providers/<provider_id>/`; mirrored payloads are scoped under `mirror/providers/<provider_id>/`. Reviewed aliases are provider inputs even though they live beside generated state.

Site-generated state is scoped under `data/sites/<site_id>/` and `bundles/sites/<site_id>/`. The default site publishes deterministic release shards before any one release approaches its configured capacity.

Generated files are outputs, not documentation owners. Do not edit them to implement behavior.

## End-to-end flow

1. A provider discovers official availability, optionally updating its source manifest.
2. A sync command fetches source events and validates attachments before retaining them in the provider mirror.
3. Normalization and classification produce shared paper identities; unresolved records enter review state instead of receiving guessed identities.
4. State merging preserves unaffected retained history during targeted and incremental work.
5. Site publication selects eligible provider records, builds pure bundles, and writes site feeds plus release-asset metadata.
6. Release planning assigns every asset to a deterministic site-owned shard.
7. The frontend consumes only site publication data and never raw provider crawl state.

## Enforcement

CI validates Python behavior, workflows, schemas, publication, source scope, catalog identity, history coverage, release planning, and documentation projections. The documentation renderer derives provider facts and the CLI summary from their executable owners; the documentation validator enforces parity, freshness, command validity, archive isolation, and link integrity.

Changes to this architecture require a focused update to the executable owner, its tests, the relevant reference/procedure, and an ADR when the rationale is durable.
