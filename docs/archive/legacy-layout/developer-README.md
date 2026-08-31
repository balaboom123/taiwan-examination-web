# Developer documentation

This section is for engineers changing repository behavior, schemas, publication, release workflows, or provider integrations.

## Start here

- exam-identity-v2.md is the current normative identity/bundle reference.
- contracts.md defines serialized boundaries and compatibility rules.
- ../operator/catalog-audit.md defines whole-catalog audit and migration commands.
- decision-records/ explains why the identity and release decisions were made.
- current-architecture.md explains the pipeline as implemented; target-architecture.md is transition context.
- provider-site-registry.md and source-onboarding.md are required before changing provider/site scope.
- ci-cd-and-release.md is required before changing workflows or release upload logic.
- exam-classification.md documents frontend display taxonomy and its v1 compatibility fallback; it is not the official identity source.

## Normative language

These docs use RFC-style words:

- MUST: mandatory
- MUST NOT: forbidden
- SHOULD: recommended default; deviations require a recorded reason
- MAY: optional

## Ownership boundary

Executable domain truth belongs in catalog/, schemas/, and app/classification.py. Documentation explains and governs that truth; it must not duplicate a second unvalidated regex taxonomy.

## Required companion updates

Any change that adds or materially changes a provider, site, workflow, schema, release process, or operator procedure MUST update:

- the owning catalog/mapping or schema;
- the relevant developer reference and ADR;
- the relevant operator procedure;
- tests and audit fixtures.

## Document map

- exam-identity-v2.md: identity dimensions, bundle purity, review and migration workflow
- contracts.md: concrete provider/site/feed/release contracts
- decision-records/: accepted architecture decisions
- current-architecture.md: current pipeline and data paths
- target-architecture.md: provider/site target model
- data-lifecycle.md: source-to-publication lifecycle
- ci-cd-and-release.md: CI/CD and release rules
- extension-rules.md: expansion governance
- provider-site-registry.md: ownership registry
- source-onboarding.md: new-provider checklist
- source-spec-template.md: source proposal template
- exam-classification.md: UI class/subclass compatibility behavior

When a document is dated or located under docs/superpowers/, treat it as historical unless this README or an ADR explicitly adopts it.
