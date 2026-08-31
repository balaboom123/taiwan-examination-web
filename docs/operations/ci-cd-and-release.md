# CI/CD and release

CI validates checked-in behavior; provider workflows refresh retained source state; site workflows publish site-owned bundles and release shards; deploy workflows build the frontend from site feeds.

## CI gates

The Python job runs the complete test suite plus focused workflow contracts, strict catalog and history audits, publication/schema validation, source-inventory validation, release planning, documentation validation, shell syntax checks, and whitespace checks. The frontend job installs locked dependencies, tests, lints, and builds.

The workflow file is the owner of exact CI commands. This document explains why the gates exist and does not duplicate an exhaustive command list.

## Release ownership

- Providers own retained source state, not public release tags.
- Sites own bundle selection, asset naming, and deterministic release-shard assignment.
- `data/sites/<site_id>/release-assets.json` describes the expected public asset set.
- The release plan assigns assets to bounded site-owned tags without relying on one global release.
- Upload and prune operations must compare external state with generated expectations before mutation.

Changing shard policy, compatibility aliases, or release ownership requires tests, an updated operator procedure, and an ADR when the rationale is durable.

## Documentation enforcement

CI runs `scripts/validate_docs.py --check`. Changes to provider scope, CLI commands, or the maintained document set must be rendered before push so generated provider facts, the provider index, command reference, and single document index stay current.
