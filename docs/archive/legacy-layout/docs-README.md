# Project documentation

The repository has two documentation audiences:

- docs/developer/: contracts, architecture, taxonomy, decisions, and contributor workflows.
- docs/operator/: repeatable audit, publication, release, and recovery procedures.

Generated state under data/, bundles/, mirror/, and frontend build output is never a documentation source of truth.

## Authority and precedence

Use the smallest authoritative source for the question:

1. catalog/ and schemas/ for executable taxonomy and data contracts;
2. developer/exam-identity-v2.md for the current identity and bundle policy;
3. developer/contracts.md for provider/site interface details;
4. developer/decision-records/ for accepted architectural choices;
5. operator/ for commands, release preflight, and recovery;
6. developer/current-architecture.md and target-architecture.md for transition context;
7. dated plans/specs under docs/superpowers/ for historical, non-normative context.

If an older document conflicts with the catalog, schema, identity reference, or ADR, the older document is stale and must be corrected or marked historical.

## Recommended reading order

1. developer/README.md
2. developer/exam-identity-v2.md
3. developer/contracts.md
4. developer/current-architecture.md
5. operator/catalog-audit.md
6. relevant provider/source and ADR documents

## Project map

~~~
catalog/                         reviewed taxonomy and provider mappings
schemas/                         versioned JSON contracts
app/classification.py            deterministic identity resolver
app/normalizer.py                provider normalization and v2 enrichment
app/bundler.py                   pure bundle grouping and ZIP manifests
app/publisher.py                 site projection and frontend facets
app/release_tags.py              physical-asset shard assignment
app/audit.py                     whole-catalog audit
data/providers/<provider>/       generated provider-owned state
data/sites/<site>/               generated site publication state
bundles/sites/<site>/            generated ZIP assets
frontend/                        presentation and compatibility feed code
docs/developer/                  reference, decisions, architecture, onboarding
docs/operator/                   runbooks, audits, release, recovery
docs/superpowers/                historical plans/specifications
PLAN.md                          temporary untracked execution brief
~~~

## Document map

- developer/exam-identity-v2.md: normative identity dimensions, purity, versioning, and change workflow.
- developer/contracts.md: provider, normalized paper, bundle, release, and frontend contracts.
- developer/decision-records/: short ADRs for durable architectural decisions.
- developer/current-architecture.md: current pipeline and transition assumptions.
- developer/target-architecture.md: longer-term provider/site architecture.
- developer/data-lifecycle.md: source-to-publication lifecycle.
- developer/ci-cd-and-release.md: workflow and release integration.
- developer/extension-rules.md: expansion governance.
- developer/provider-site-registry.md: provider/site ownership.
- developer/source-onboarding.md: provider onboarding checklist.
- operator/catalog-audit.md: full-catalog identity audit, migration, release preflight, and recovery.
- operator/runbook.md, workflows.md, recovery.md: established operational procedures.
- superpowers/: historical proposals; not normative after implementation.

## Maintenance rule

Every change to a catalog concept, mapping, schema, release policy, provider, or site must update the owning reference, relevant ADR/procedure, and automated tests. Add Status, Owner, and applicable version to maintained docs. Completed plans move to an archive or receive a clear historical banner; they do not remain competing specifications.
