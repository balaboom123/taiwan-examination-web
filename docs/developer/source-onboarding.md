# Source Onboarding

Use this checklist when adding a new provider to the repository.

## Before You Start

Answer these questions first:

- What is the `provider_id`?
- What is the source domain or source system?
- Is the content public, licensed, rate-limited, or authentication-gated?
- What identifies a stable source exam or paper record?
- What file types are expected?
- How often does the source change?
- Will one site or multiple sites consume this provider?
- Will this provider contribute one canonical bundle or many?
- Will this provider force an existing site to add or rebalance release shards?
- Does the provider need site-specific canonicalization or only provider-local aliasing?

If these answers are unclear, do not start implementation.

## Required Design Outputs

Before coding, the provider design SHOULD define:

- discovery model
- probe model
- raw page schema
- normalized mapping into shared records
- mirror layout
- provider-scoped generated outputs
- test strategy
- operator commands and workflows

## Implementation Checklist

### 1. Establish ownership

- choose `provider_id`
- define provider-owned paths under the target architecture
- define which site or sites will consume the provider

### 2. Implement provider ingestion

- discovery logic
- page fetch logic
- file download logic
- payload validation rules
- provider-specific parsing

### 3. Implement provider state

- provider-scoped source manifest
- provider-scoped review queue
- provider-scoped failure log
- provider-scoped alias or canonicalization inputs if needed

### 4. Implement normalized output contract

- map provider data into shared normalized records
- define category, subject, year, source exam ID, and file metadata behavior
- define how canonical ID migrations are handled, if applicable

### 5. Integrate publication

- decide which site consumes the provider
- define bundle selection rules
- define whether the provider contributes one bundle or many
- define release tag ownership
- define release tag sharding impact on the consuming site
- define gating behavior, if any
- define frontend/public feed implications

### 6. Add automation

- provider sync workflow
- provider audit or discovery workflow if needed
- site publication or deploy workflow updates if publication changes

### 7. Add tests and verification

- parser tests
- manifest tests
- publication or feed tests if outputs change
- documented operator verification commands

### 8. Update docs

- developer architecture docs
- operator runbook
- operator recovery procedures
- this onboarding doc if a new pattern is introduced

## Minimum Definition Of Done

A new provider is not done until:

- the provider has a documented `provider_id`
- provider-owned generated state is scoped
- operator commands and workflows are documented
- recovery steps are documented
- tests exist for source-specific logic
- site consumption rules are documented
- release sharding impact is documented
- no new global root-level generated state was introduced without a transition plan

## Review Questions

Before merge, reviewers SHOULD ask:

- Does this provider force MOEX-specific assumptions into shared code?
- Does it introduce new global state?
- Does it define clear ownership of manifests, failures, and outputs?
- Can an operator run and recover it without reading code?
- Can the provider be consumed by a site without coupling the frontend to raw source logic?
