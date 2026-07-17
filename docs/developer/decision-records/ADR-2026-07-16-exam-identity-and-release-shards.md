# ADR-2026-07-16: versioned identity, pure bundles, and release shards

- Status: accepted
- Owners: data-model, publication, and operations maintainers
- Scope: all providers in the default site

## Context

The catalog grouped normalized papers by a display-name-derived canonical ID. A track such as 「一般行政」 appears in several official programs and levels, so one ZIP could contain different programs. The same failure is possible for every provider. Separating identities increases logical bundles, while compatibility aliases consume GitHub Release asset slots.

## Decisions

### 1. Official identity is distinct from legacy URL identity

V2 identity is the tuple of provider, domain, family, series, level, track, content-changing variants, and stage. bundle_id is derived from that tuple and the versioned bundle policy.

Old canonical_id values and asset names remain for lookup and compatibility. They are not the v2 grouping key.

### 2. Classification is catalog-wide and evidence-backed

Every registered provider and retained historical record is audited. Provider rules may differ; every result exposes its identity signature, confidence, and reason. A missing or ambiguous marker becomes an isolated review item and must not be merged into a confident fallback.

The executable resolver is app/classification.py. Reviewed vocabulary and mappings live under catalog/. Frontend regexes are presentation compatibility only.

### 3. Bundle purity is an invariant

A primary v2 bundle may vary by year/event, but not by series, level, track, stage, or content-affecting variant. Equivalent grades across different programs remain distinct.

### 4. Shard at 900 and enforce 1,000

Release planning counts physical ZIP names: primary assets plus compatibility aliases. New assignments target at most 900 per tag, leaving margin below GitHub hard cap of 1,000. Publication and upload/preflight share the same capacity calculation.

### 5. Migration is additive and reversible

The first migration rewrites local state and emits v2 outputs without deleting v1 bundles or remote release assets. A new v2 release namespace may be used. Remote upload, alias retirement, and v1 deletion require separate explicit authorization.

## Consequences

Positive: same-track programs and levels are structurally separate; all providers use one auditable contract without pretending their hierarchies are identical; release growth is predictable; decisions can be reviewed outside crawler code.

Costs: more bundles/shards/metadata; historical records without reliable markers require source review; mapping changes require full reclassification; aliases consume capacity.

## Rejected alternatives

- More aliases: aliases preserve lookup but cannot distinguish source identities.
- Frontend-only classification: it cannot repair bundle membership after ZIPs are built.
- One giant archive: it hides level errors and weakens selective download/search.
- Silently dropping ambiguous records: it hides data loss.
- Deleting old assets during migration: it removes rollback and breaks links.

Before publication, run the whole-catalog audit, migration, purity checks, and capacity preflight. If a public record remains review, strict audit should fail until authoritative mapping or explicit exclusion is recorded.

