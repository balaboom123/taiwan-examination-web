# Developer Documentation

This section is for engineers changing repository behavior, architecture, schemas, release workflows, or onboarding new sources.

The repository is in a transition state:

- `current-architecture.md` describes the MOEX-first implementation that exists today.
- `target-architecture.md` defines the multi-source structure the repo MUST move toward.

## How To Use These Docs

- Read `current-architecture.md` if you need to understand the repo as it exists now.
- Read `target-architecture.md` before introducing any new provider, site, or workflow.
- Read `contracts.md` before changing schemas, feeds, or persisted publication state.
- Read `migration-plan.md` before moving paths or changing ownership boundaries.
- Read `extension-rules.md` before approving structural changes.
- Read `provider-site-registry.md` before adding or renaming any provider or site.
- Read `source-onboarding.md` when adding a new source.
- Read `source-spec-template.md` before drafting source #2 or later.
- Read `ci-cd-and-release.md` before touching GitHub Actions, release logic, or deploy paths.

## Normative Language

These docs use RFC-style words:

- `MUST`: mandatory rule
- `MUST NOT`: forbidden
- `SHOULD`: recommended default; deviations require clear justification
- `MAY`: optional

## Required Companion Updates

Any change that adds or materially changes a provider, site, workflow, schema, release process, or operator procedure MUST update:

- the relevant developer doc in this directory
- the relevant operator doc in `../operator/`
- tests or validation steps affected by the change

## Document Map

- `current-architecture.md`: current repo boundaries, outputs, and single-source assumptions
- `target-architecture.md`: future provider/site model and migration phases
- `contracts.md`: normative contract definitions for provider and site data
- `migration-plan.md`: exact migration sequence from root-level global state to scoped ownership
- `data-lifecycle.md`: flow from source discovery to public download link
- `ci-cd-and-release.md`: current workflows and future scoping rules
- `extension-rules.md`: expansion governance
- `provider-site-registry.md`: current and planned provider/site ownership registry
- `source-onboarding.md`: required steps and definition of done for new sources
- `source-spec-template.md`: copy-paste template for approving new provider designs
