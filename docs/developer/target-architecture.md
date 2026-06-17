# Target Architecture

This document defines the intended multi-source architecture for the repository. It is normative for future expansion.

## Goals

The target architecture MUST allow the repo to support:

- multiple independent source providers
- one or more public sites backed by shared provider data
- site-specific release assets and monetization rules
- provider-scoped sync and recovery workflows
- migration from the current MOEX-first layout without breaking current publication

## Core Concepts

- `provider`: source-specific ingestion implementation such as MOEX
- `site`: public-facing deployment with its own branding, frontend config, release tag, and download behavior
- `normalized catalog`: provider data converted into a shared paper schema
- `publication`: transformation from normalized data to bundles, release assets, gating links, and frontend outputs
- `operator profile`: secrets, workflow permissions, and manual procedures required to run a provider or site

Providers and sites are intentionally separate concepts. A single provider MAY feed multiple sites. A site MAY aggregate multiple providers if the UX and business rules require it.

## Target Directory Layout

The repository SHOULD evolve toward a structure like this:

```text
app/
  core/
  providers/
    moex/
    <provider_id>/
  publication/
  monetization/

data/
  providers/
    moex/
      exams/
      papers/
      review-queue.json
      source-manifest.json
      sync-failures.json
      aliases.json
    <provider_id>/
      ...
  sites/
    default/
      bundles.json
      release-assets.json
      lootlabs-links.json
      frontend-bundles.json
    <site_id>/
      ...

mirror/
  providers/
    moex/
    <provider_id>/

bundles/
  sites/
    default/
    <site_id>/

frontend/
  site-configs/
    default.ts
    <site_id>.ts
```

The exact filenames may change, but the ownership boundary MUST remain the same:

- provider-owned state stays under provider-scoped paths
- site-owned publication state stays under site-scoped paths

## Ownership Boundaries

### Provider-owned responsibilities

Providers MUST own:

- discovery of available years and exams
- source probing and manifest updates
- page fetch and raw record parsing
- file download and validation
- normalization into shared catalog shape
- provider-scoped review queue and failure tracking

### Shared-core responsibilities

Shared core modules SHOULD own:

- generic manifest and state helpers
- checksum and integrity utilities
- shared normalized data models
- bundle generation interfaces
- release publication interfaces

### Site-owned responsibilities

Sites MUST own:

- bundle selection rules
- release tag and asset naming policy
- gating or monetization wrapper selection
- frontend feed contract
- branding and deployment target

## Target Contracts

### Provider contract

Every provider MUST define:

- `provider_id`
- discovery entrypoint
- probe strategy and manifest schema
- normalized output schema mapping
- storage and mirror key rules
- failure semantics
- tests for parser, manifest, and download validation

### Site contract

Every site MUST define:

- `site_id`
- input provider set
- bundle-building rules
- release tag and compatibility alias policy
- frontend/public feed schema
- monetization behavior, if any
- deployment target and workflow owner

### Monetization contract

Monetization layers such as LootLabs MUST wrap publication outputs, not provider downloads. They MUST validate that the wrapped target URL and checksum still match the current bundle asset.

## Transition Phases

The migration SHOULD happen in phases:

### Phase 0: Current single-provider state

- MOEX-only
- root-level generated `data/`
- one release tag
- one LootLabs manifest

### Phase 1: Provider-aware code structure

- introduce provider-specific modules and IDs
- keep current root-level outputs for compatibility
- do not yet change public paths

### Phase 2: Dual-write transition

- write both legacy root-level outputs and provider/site-scoped outputs
- validate parity
- migrate workflows and operator runbooks

### Phase 3: Scoped-only steady state

- provider data owned under `data/providers/<provider_id>/`
- site publication data owned under `data/sites/<site_id>/`
- workflows parameterized by provider or site

## Compatibility Rules During Transition

- Current MOEX behavior MUST keep working until operator docs and workflows are updated.
- New providers MUST NOT introduce new global root-level state.
- If compatibility outputs are needed, they MUST be marked as legacy and have a removal plan.
- The frontend SHOULD move to site-scoped feed generation before multiple sites are deployed.

## Non-Goals

The target architecture does not require:

- immediate replacement of every current MOEX path
- microservices or multi-repo decomposition
- a database
- per-provider frontend codebases by default

The default strategy is still one repo with clear internal boundaries.
