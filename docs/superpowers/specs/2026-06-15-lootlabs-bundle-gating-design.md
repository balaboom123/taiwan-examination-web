# LootLabs Bundle Gating Design

## Summary

This design adds build-time LootLabs gating for the React homepage bundle downloads in `taiwan_examination_web`.

All homepage bundle ZIP downloads will route through one pre-created LootLabs `loot_url` per bundle. Links are created or refreshed during the data/build pipeline, persisted in a repo-tracked manifest, and merged into the frontend output at build time. The raw bundle ZIP URLs remain available to the internal data pipeline but must not appear in the frontend-served `data/bundles.json`.

## Goals

- Gate every React homepage bundle ZIP download through LootLabs.
- Reuse the same LootLabs link for the same bundle across deploys until the target changes.
- Create or refresh LootLabs links during deploy/build, not on user click.
- Fail closed when LootLabs link creation or lookup fails.
- Keep the React frontend simple: it should continue rendering normal anchor tags.

## Non-Goals

- Gating the Python-generated `site/index.html` paper and per-year download links.
- Adding login, credits, sessions, or a user wallet.
- Adding runtime Netlify Functions or another server redirect layer for the first version.
- Supporting partial rollout. This version gates all homepage bundles.

## Confirmed Product Decisions

- Scope is limited to the React homepage bundle ZIP buttons.
- Every bundle uses LootLabs.
- A given bundle reuses one LootLabs link until its target metadata changes.
- If LootLabs integration fails, downloads do not fall back to the raw ZIP URL.
- LootLabs links are pre-created during deploy/build.
- A bundle link is recreated when:
  - no stored `loot_url` exists
  - the bundle `download_url` changes
  - the bundle `checksum` changes
  - the applied LootLabs settings change

## Current Project Context

The current project has three relevant layers:

1. Python pipeline
   - `app/cli.py` drives sync/build commands.
   - `app/publisher.py` writes root `data/bundles.json`.
   - `BundleAsset.download_url` in `app/models.py` currently holds the raw bundle ZIP URL.

2. Frontend build adapter
   - `frontend/vite.config.ts` serves and emits `data/bundles.json` for the React app.
   - `frontend/build/bundles-data.mjs` converts generated bundle records into the frontend schema.

3. React frontend
   - `frontend/src/hooks/use-bundles.ts` fetches `data/bundles.json`.
   - `frontend/src/components/bundle-row.tsx` renders `<a href={bundle.url}>`.

This existing separation is useful. The Python pipeline can continue owning raw bundle metadata, while the frontend build adapter can emit a gated version for public use.

## Chosen Architecture

The implementation will use a build-time manifest-driven approach.

### Internal Raw Bundle Data

Root `data/bundles.json` remains the internal generated source of truth and keeps the raw bundle ZIP `download_url`.

This file is used by:

- Python workflows
- local bundle generation
- LootLabs sync input
- the existing static `site/` build path

It is not the final public contract for the React site.

### LootLabs Manifest

A new repo-tracked manifest stores the persistent bundle-to-LootLabs mapping:

- Path: `data/lootlabs-links.json`
- Ownership: Python pipeline
- Purpose: remember which `loot_url` belongs to each bundle and when it must be rebuilt

Proposed schema:

```json
{
  "version": 1,
  "provider": "lootlabs",
  "settings": {
    "tier_id": 1,
    "number_of_tasks": 1,
    "theme": 1
  },
  "bundles": {
    "nurse": {
      "canonical_id": "nurse",
      "asset_name": "nurse_bundle.zip",
      "loot_url": "https://loot-link.example/abc",
      "target_download_url": "https://github.com/example/repo/releases/download/moex-bundles/nurse_bundle.zip",
      "target_checksum": "abc123",
      "updated_at": "2026-06-15T12:34:56+08:00"
    }
  }
}
```

Schema rules:

- `bundles` is an object keyed by `canonical_id`.
- `settings` captures the effective LootLabs configuration used to create the stored links.
- Each stored bundle record must be self-sufficient for rebuild decisions.

## LootLabs Sync Step

A new Python command will maintain `data/lootlabs-links.json`.

### Proposed Command

`python -m app sync-lootlabs`

### Inputs

- root `data/bundles.json`
- existing `data/lootlabs-links.json` if present
- environment variables:
  - `LOOTLABS_API_KEY`
  - `LOOTLABS_TIER_ID`
  - `LOOTLABS_NUMBER_OF_TASKS`
  - `LOOTLABS_THEME`

### Output

- updated `data/lootlabs-links.json`

### Behavior

For each bundle in root `data/bundles.json`:

1. Read the current raw `download_url`, `checksum`, `canonical_id`, and `asset_name`.
2. Read the existing manifest entry if present.
3. Reuse the existing `loot_url` only when all of the following are true:
   - entry exists
   - stored `target_download_url` matches the current raw `download_url`
   - stored `target_checksum` matches the current `checksum`
   - stored manifest `settings` match the current configured LootLabs settings
4. Otherwise call the LootLabs content locker API to create a new link.
5. Persist the resulting `loot_url` and current target metadata back into the manifest.

### API Contract Assumptions

The sync step will call the LootLabs content locker API using:

- endpoint: `POST https://creators.lootlabs.gg/api/public/content_locker`
- bearer auth via `Authorization: Bearer <token>`
- request fields:
  - `title`
  - `url`
  - `tier_id`
  - `number_of_tasks`
  - `theme`

The title should be derived from bundle metadata and truncated to the provider limit.

### Manifest Write Strategy

Manifest updates must be atomic:

1. build the full in-memory result
2. write to a temporary file
3. replace the target manifest only after the full sync succeeds

This prevents partial or corrupted writes when the process fails mid-run.

## Frontend Build Integration

The React app should keep its current runtime behavior and receive already-gated URLs from the build adapter.

### Merge Point

The gating merge happens in `frontend/build/bundles-data.mjs`, because that file already converts root `data/bundles.json` into the frontend schema used by `frontend/vite.config.ts`.

### Merge Rules

When producing frontend bundle records:

- read the raw generated bundle list
- read `data/lootlabs-links.json`
- require a manifest entry for every bundle
- replace frontend `url` with the corresponding `loot_url`

Result:

- root `data/bundles.json` keeps raw ZIP URLs for internal tooling
- frontend-emitted `data/bundles.json` contains only LootLabs URLs

### Public Data Guarantee

The frontend-served bundle data must not expose raw bundle ZIP URLs for gated bundles.

That applies to:

- dev server output from `frontend/vite.config.ts`
- production output under `frontend/dist/data/bundles.json`

## Failure Handling

This feature fails closed.

### Sync Failures

The LootLabs sync command fails when:

- the API key is missing
- the LootLabs API request fails
- the LootLabs API response is malformed
- the response does not contain a usable `loot_url`

If any required bundle fails to get a valid `loot_url`, the command exits non-zero and does not commit a partially updated manifest.

### Frontend Build Failures

The frontend build fails when:

- `data/lootlabs-links.json` is missing while gating is enabled
- any bundle from root `data/bundles.json` has no corresponding valid manifest entry
- a manifest entry is structurally invalid

There is no fallback to the raw ZIP URL in production mode.

### User-Facing Result

Because links are pre-created, end users should never wait for on-click LootLabs link creation. If the integration is broken, the build/deploy fails before release instead of leaking raw downloads.

## Build and Deploy Flow

The first-version workflow is:

1. run the existing sync/build command that regenerates root `data/bundles.json`
2. run `python -m app sync-lootlabs`
3. run the frontend build
4. deploy the frontend output

Expected command families:

- `python -m app sync-full`
- `python -m app sync-incremental`
- `python -m app build-bundles`
- `python -m app sync-lootlabs`
- `npm run build` in `frontend/`

This design does not require Netlify Functions for the first version.

## Testing Strategy

Testing is split across Python sync logic, frontend build integration, and workflow coverage.

### Python Unit Tests

Add tests for:

- manifest read/write behavior
- rebuild decision logic
- settings-change full rebuild behavior
- API success parsing
- API failure handling
- atomic manifest replacement

The LootLabs API must be mocked in tests.

### CLI Tests

Add tests for:

- parser registration of `sync-lootlabs`
- required environment/config handling
- non-zero exit behavior on provider failures

### Frontend Build Tests

Expand `frontend/build/bundles-data.test.mjs` to verify:

- raw generated bundle data merges with the LootLabs manifest
- frontend output replaces `url` with `loot_url`
- missing manifest entries fail loudly
- malformed manifest data fails loudly

### Workflow Tests

Update workflow tests to assert that build/deploy automation runs the LootLabs sync step before the frontend build or release publication that depends on gated links.

### Manual Smoke Tests

Before rollout:

1. regenerate bundles
2. run LootLabs sync
3. build the frontend
4. inspect built `dist/data/bundles.json`
5. confirm built bundle URLs are LootLabs URLs
6. click several bundle links in a deployed environment and confirm they route through LootLabs

## Rollout Plan

Version 1 rollout is all-or-nothing for React homepage bundles.

Release checklist:

1. configure LootLabs environment variables in the deploy environment
2. generate raw bundle data
3. sync LootLabs manifest
4. build frontend output
5. verify no raw bundle ZIP URLs remain in the React-served bundle data
6. deploy

## Risks and Mitigations

### Risk: Raw ZIP URLs leak through public frontend data

Mitigation:

- keep raw URLs only in root generated data
- enforce LootLabs replacement in the frontend build adapter
- fail the frontend build if any mapping is missing

### Risk: Repeated unnecessary LootLabs link creation

Mitigation:

- store `target_download_url`, `target_checksum`, and effective settings in the manifest
- rebuild only when those fields change

### Risk: Provider outage blocks deployment

Mitigation:

- accept fail-closed behavior for version 1
- keep the sync step explicit in CI so failures are visible before release

## Future Extensions

Out of scope for this version, but compatible with this design:

- selective gating instead of gating every bundle
- postback verification
- anti-bypass download tokens
- gating for the Python-generated static `site/` pages
- richer provider abstraction if LootLabs is replaced later

## Design Approval State

This spec reflects the approved direction as of 2026-06-15:

- React homepage bundles only
- all bundles gated
- one reusable LootLabs link per bundle
- build-time pre-creation
- no fallback to raw ZIP URLs
- rebuild on target URL, checksum, or settings changes
