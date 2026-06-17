# Project Documentation

This directory defines how the repository works today and how it MUST evolve as it expands beyond the current MOEX-only implementation.

There are two primary audiences:

- `developer/`: engineers changing architecture, schemas, workflows, code structure, or onboarding new sources.
- `operator/`: repo operators running syncs, releases, audits, deployments, and recovery procedures. These are the "user" docs for maintainers rather than end visitors of the website.

## Document Precedence

When documents conflict, use this order:

1. `developer/extension-rules.md`
2. `developer/target-architecture.md`
3. `developer/ci-cd-and-release.md`
4. `operator/recovery.md`
5. `operator/runbook.md`
6. `developer/current-architecture.md`
7. Historical design notes such as `DESIGN.md` and `PRODUCT.md`

`developer/extension-rules.md` is the normative governance document for future expansion.

## Reading Order

If you are new to the repo:

1. Read `developer/current-architecture.md`
2. Read `developer/target-architecture.md`
3. Read `developer/contracts.md`
4. Read `developer/migration-plan.md`
5. Read `developer/extension-rules.md`
6. Read `operator/runbook.md`

## Documentation Map

- `developer/README.md`: overview of the developer docs
- `developer/current-architecture.md`: how the repo works today
- `developer/target-architecture.md`: the intended multi-source architecture
- `developer/contracts.md`: concrete data and interface contracts for providers and sites
- `developer/migration-plan.md`: exact current-to-target cutover sequence
- `developer/data-lifecycle.md`: source-to-publication lifecycle and integrity model
- `developer/ci-cd-and-release.md`: workflow, release, and deploy rules
- `developer/extension-rules.md`: mandatory expansion rules
- `developer/provider-site-registry.md`: ownership registry for active and planned providers/sites
- `developer/source-onboarding.md`: checklist for adding a new source
- `developer/source-spec-template.md`: fixed template for proposing a new source before implementation
- `operator/README.md`: overview of operator docs
- `operator/runbook.md`: manual operating procedures
- `operator/workflows.md`: automated workflow behavior and expectations
- `operator/recovery.md`: failure handling and recovery steps

## Glossary

- `provider`: source-specific ingestion implementation such as MOEX
- `site`: public-facing deployment with its own branding, bundle feed, release assets, and deploy target
- `normalized paper`: source content after category normalization and metadata cleanup
- `bundle`: ZIP archive grouping multiple years or files for download
- `publication`: the process of turning normalized data into bundle metadata, release assets, gating links, and frontend-consumable outputs
- `operator`: maintainer who runs syncs, investigates failures, or triggers workflows
- `generated data`: files produced by commands or workflows and not intended for manual editing

## Current Status

The current repository is still single-provider and mostly single-site:

- provider: MOEX
- legacy static output: `site/`
- modern frontend app: `frontend/`
- generated data mostly stored in root-level `data/`

The target model is multi-provider and site-scoped. The docs in this directory define the migration path and the guardrails for getting there.
