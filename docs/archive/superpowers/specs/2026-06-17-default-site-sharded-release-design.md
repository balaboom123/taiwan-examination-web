# Default Site Sharded Release Design

## Goal

Lock the migration rule for multi-provider expansion of the existing public site.

## Decisions

### 1. Site topology

- The repository will keep one public site: `default`.
- New providers may feed that site without creating a second public frontend.

### 2. Ownership boundary

- Providers own ingestion state only: discovery, manifests, raw records, mirrored source files, normalization inputs, and provider-scoped failures.
- The `default` site owns public publication state: bundles, release assets, LootLabs links, and frontend feed outputs.
- Public GitHub releases are site-owned publication artifacts, not provider-owned ingestion artifacts.

### 3. Release topology

- The `default` site may publish assets through one GitHub release tag or many GitHub release tags.
- The architecture must not assume that one site equals one release tag.
- Asset-to-tag assignment must be deterministic so unchanged assets do not move between tags without reason.
- The operational target is to shard before any single release reaches 900 assets.
- Frontend and LootLabs consumers must read one site publication view and must not need to know which release tag stores a given bundle.

### 4. CEEC GSAT provider

- Provider ID: `ceec_gsat`
- Consuming site: `default`
- Source scope: CEEC `學科能力測驗` archive
- Publication rule: this provider contributes exactly one canonical bundle asset
- Canonical bundle identity:
  - `canonical_id`: `ceec-gsat`
  - `canonical_name`: `學科能力測驗`

### 5. Compatibility rule

- The current single-tag publication flow may remain during migration for compatibility.
- Multi-tag support must be added before the site approaches the GitHub per-release asset limit.
- Release-tag sharding is a site concern and must not leak into provider-owned contracts.

## Rationale

This keeps the architecture aligned with the actual public product boundary.

Users see one site, one catalog, and one monetization layer. They should not need to understand which crawler or release tag produced a given bundle. At the same time, provider-owned ingestion state remains isolated enough for parsing, failure recovery, and future source onboarding.

Site-owned release sharding solves the GitHub release-asset scaling risk without forcing the frontend, LootLabs, or provider contracts to coordinate multiple provider-specific release tags.

## Non-Goals

- no provider-owned public release tags for providers feeding the existing site
- no second public site for CEEC
- no CEEC bundle split into multiple public assets

## Acceptance Criteria

- Developer docs define release-tag sharding as a site-owned rule.
- Bundle and release asset contracts can carry release tag ownership explicitly.
- Registry docs identify `ceec_gsat` as a planned provider for the `default` site.
- Migration docs require multi-tag capability before the GitHub asset cap becomes a risk.
