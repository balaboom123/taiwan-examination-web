# Contracts

This document defines the concrete data and interface contracts that future providers and sites MUST follow.

The goal is to prevent the multi-source expansion from drifting into ad hoc JSON shapes, implicit compatibility assumptions, or frontend/backend coupling.

## Contract Principles

- Every persisted schema MUST have an explicit owner.
- Provider-owned contracts and site-owned contracts MUST remain separate.
- Public-facing contracts MUST be versioned.
- Additive changes are preferred over destructive changes.
- Breaking contract changes MUST ship with a migration plan.

## Contract Ownership

| Contract | Owner | Current location | Target ownership |
| --- | --- | --- | --- |
| source manifest | provider | `data/source-manifest.json` | `data/providers/<provider_id>/source-manifest.json` |
| raw exam pages | provider | `data/exams/*.json` | `data/providers/<provider_id>/exams/*.json` |
| normalized papers | provider | `data/papers/*.json` | `data/providers/<provider_id>/papers/*.json` |
| review queue | provider | `data/review-queue.json` | `data/providers/<provider_id>/review-queue.json` |
| sync failures | provider | `data/sync-failures.json` | `data/providers/<provider_id>/sync-failures.json` |
| alias rules | provider unless documented otherwise | `data/aliases.json` | `data/providers/<provider_id>/aliases.json` |
| bundle metadata | site | `data/bundles.json` | `data/sites/<site_id>/bundles.json` |
| release asset inventory | site | `data/release-assets.json` | `data/sites/<site_id>/release-assets.json` |
| gating manifest | site | `data/lootlabs-links.json` | `data/sites/<site_id>/lootlabs-links.json` |
| frontend bundle feed | site | emitted during frontend build | `data/sites/<site_id>/frontend-bundles.json` or build artifact equivalent |

## Versioning Rules

- Persisted JSON contracts SHOULD include `schema_version` once they become multi-provider or multi-site scoped.
- Schema versions MUST be integers.
- A breaking change MUST increment `schema_version`.
- A non-breaking additive change MAY keep the current version if all consumers safely ignore unknown fields.
- Consumers MUST fail loudly on unsupported `schema_version` values for critical contracts.

## Provider Contract: Source Manifest

Current behavior:

- `app/manifest.py` defines `SourceManifest`
- current schema version is `1`
- sections include `probe_policy`, `years`, `exams`, and `files`

Required target shape:

```json
{
  "schema_version": 1,
  "provider_id": "moex",
  "probe_policy": {},
  "years": {},
  "exams": {},
  "files": {}
}
```

Required fields:

- `schema_version`: integer
- `provider_id`: stable provider identifier
- `probe_policy`: provider-specific probe settings
- `years`: year-level probe state
- `exams`: source exam-level probe state
- `files`: optional file-level probe state if the provider needs it

Rules:

- A manifest MUST belong to exactly one provider.
- A manifest MUST NOT describe release or site state.
- Probe consumers MUST reject manifests that do not match the expected provider.

## Provider Contract: Raw Exam Page Record

Current shape is derived from `SourceExamPage`, `ExamAttachment`, and `ParsedPaper`.

Required fields:

- `source_exam_id`
- `year_ad`
- `year_roc`
- `exam_name_raw`
- `attachments`
- `papers`

Attachment fields:

- `title`
- `file_type`
- `download_url_source`
- `storage_key`
- `asset_name`
- `checksum`
- `download_url_mirror`

Paper fields:

- `category_raw`
- `category_code`
- `subject_code`
- `subject_name_raw`
- `files`
- `mirror_files`

Rules:

- Raw exam page records are provider-owned and MUST preserve enough source detail to rebuild normalized records.
- Raw records MUST NOT depend on site publication choices.

## Provider Contract: Normalized Paper Record

Current shape is derived from `NormalizedPaper`.

Required fields:

- `canonical_id`
- `canonical_name`
- `year_roc`
- `exam_name_raw`
- `category_raw`
- `subject_name_raw`
- `paper_code`
- `file_type`
- `download_url_source`

Current optional-but-supported fields:

- `category_code`
- `source_exam_id`
- `subject_code`
- `download_url_mirror`
- `download_url_bundle`
- `storage_key`
- `checksum`

Rules:

- `canonical_id` is the stable grouping key for bundle generation.
- `source_exam_id` is the stable provider traceability key.
- `download_url_bundle` is publication-derived and MUST remain optional at provider-normalization time.
- Provider-specific parser fields MUST NOT leak into this contract without an explicit schema update.

Recommended future wrapped shape:

```json
{
  "schema_version": 1,
  "provider_id": "moex",
  "records": []
}
```

## Provider Contract: Review Queue

Required fields for each record:

- `raw_category`
- `normalized_candidate`
- `source_exam_id`
- `year_roc`

Rules:

- Review queue entries MUST only represent unresolved normalization work.
- Review queue records MUST be provider-scoped unless a site explicitly owns cross-provider canonicalization.

## Provider Contract: Sync Failure Record

Current shape is derived from `SyncFailure`.

Required fields:

- `stage`
- `source_exam_id`
- `year_roc`
- `paper_code`
- `file_type`
- `url`
- `message`

Rules:

- Failure records MUST be machine-readable enough for triage and operator recovery.
- New providers MUST reuse these semantics unless there is a documented reason to extend them.

## Site Contract: Bundle Metadata

Current frontend publication depends on fields derived from `BundleAsset`.

Required fields:

- `canonical_id`
- `canonical_name`
- `years`
- `file_count`
- `storage_key`
- `asset_name`
- `release_tag`
- `download_url`
- `checksum`
- `legacy_asset_names`

Rules:

- Bundle metadata is site-owned publication state.
- Bundle metadata MUST identify the GitHub release tag that owns the final asset.
- `download_url` MUST point to the ungated final artifact target.
- `legacy_asset_names` MAY be used for compatibility but MUST remain site-owned, not provider-owned.
- Consumers MUST NOT assume that all bundles for a site live under one release tag.

Recommended future wrapped shape:

```json
{
  "schema_version": 1,
  "site_id": "default",
  "bundles": []
}
```

## Site Contract: Release Asset Inventory

Required fields:

- `release_tag`
- `storage_key`
- `asset_name`
- `checksum`
- `legacy_asset_names`

Rules:

- The release asset inventory is the source of truth for what ZIP assets a site expects on its release.
- Release publication logic MUST derive upload and prune behavior from this contract.
- Release asset inventory entries MUST be site-owned even when multiple providers contribute bundle content.
- Release tag assignment MUST be deterministic.
- Site publication MUST support multiple release tags.
- The default operational ceiling is to shard before any one release exceeds 900 assets.

## Site Contract: Gating Manifest

Current LootLabs entries include:

- `canonical_id`
- `asset_name`
- `loot_url`
- `target_download_url`
- `target_checksum`
- `updated_at`

Required target wrapped shape:

```json
{
  "schema_version": 1,
  "site_id": "default",
  "provider": "lootlabs",
  "settings": {},
  "bundles": {}
}
```

Rules:

- Gating manifests MUST belong to exactly one site.
- Gating records MUST validate target URL and checksum drift.
- Gating consumers MUST be able to rebuild the manifest from site bundle metadata.

## Site Contract: Frontend Bundle Feed

Current frontend feed shape:

```json
[
  {
    "id": "nurse",
    "name": "Nurse",
    "years": [115, 114],
    "fileCount": 42,
    "url": "https://..."
  }
]
```

Required future wrapped shape:

```json
{
  "schema_version": 1,
  "site_id": "default",
  "gated": true,
  "bundles": [
    {
      "id": "nurse",
      "name": "Nurse",
      "years": [115, 114],
      "fileCount": 42,
      "url": "https://..."
    }
  ]
}
```

Rules:

- The frontend feed MUST be site-owned.
- The frontend feed MUST NOT expose raw provider-specific crawl fields.
- The frontend feed MUST be derivable entirely from site publication outputs.
- Frontend consumers MUST NOT need to know which release tag stores a given asset.

## Compatibility Policy

- Current root-level files are legacy compatibility outputs.
- New providers and sites MUST define scoped versions of their contracts first.
- Legacy root-level compatibility files MAY continue to exist during migration, but they MUST NOT be the only persisted form of a new provider or site contract.

## Required Contract Changes For Source #2

Before adding the second provider, the repo SHOULD implement:

1. `provider_id` support on provider-owned persisted contracts.
2. `site_id` support on site-owned persisted contracts.
3. Site-scoped frontend feed generation.
4. Explicit schema wrappers for bundle metadata and gating manifests.
5. Site-owned `release_tag` assignment on published bundle and release asset contracts.
6. A deterministic multi-tag publication policy that avoids the GitHub per-release asset cap.
