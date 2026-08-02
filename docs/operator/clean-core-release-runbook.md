# Clean-core release runbook — 2026-08-02

Status: prepared, **not executed**
Owner: release and data operators

This runbook ships the recovered MOEX/WDASEC/TCTE/CEEC catalog while withholding the
providers whose published records are known to be wrong. Nothing in it has been run
against the remote: no push, no release creation, no upload, no prune, no deployment.

Read `release-checklist.md` first; this runbook is the current-cycle supplement, not a
replacement.

## Why the ordering matters

`.github/workflows/deploy-pages.yml` triggers on any push to `main` touching
`frontend/**`, `app/**`, `catalog/**`, `data/providers/**`, or `data/sites/default/**`,
and it **only builds the site**. It never touches GitHub Releases; only `sync-full.yml`
does. The site therefore goes live referencing whatever assets happen to exist at that
moment.

The branch adds 1,327 assets that do not exist on any release yet. Pushing first would
publish a catalog in which **1,327 of 3,596 rows (37%) return 404 on download**.

> Upload assets first. Push second. Never the reverse.

## Current delta

Measured on `agent/completeness-integration` at the quarantine checkpoint against
`origin/main`'s `data/sites/default/release-assets.json`.

| Quantity | Value |
| --- | --- |
| Live assets (per `origin/main`) | 2,308 |
| Branch projection | 3,598 |
| Assets to upload | 1,327 (7.28 GB) |
| Stale assets to prune | 37 |
| Releases to create | 5 (`default-bundles-v2-009` … `-013`) |
| Frontend rows | 2,305 → 3,596 |

Uploads by shard tag:

| Tag | New assets | Release exists |
| --- | --- | --- |
| `default-bundles-v2-002` | 1 | yes |
| `default-bundles-v2-003` | 2 | yes |
| `default-bundles-v2-008` | 107 | yes |
| `default-bundles-v2-009` | 304 | **no — created by `ensure`** |
| `default-bundles-v2-010` | 300 | **no — created by `ensure`** |
| `default-bundles-v2-011` | 306 | **no — created by `ensure`** |
| `default-bundles-v2-012` | 303 | **no — created by `ensure`** |
| `default-bundles-v2-013` | 4 | **no — created by `ensure`** |

Prunes are 35 quarantined assets plus 2 superseded orphans, in tags `-001` (11),
`-003` (2), and `-008` (24).

Preconditions verified locally at this checkpoint:

- every `storage_key` in `release-assets.json` exists on disk (0 missing);
- no asset reaches GitHub's 2 GiB per-asset limit (largest is 1.64 GB);
- no shard exceeds the 900-asset safety target or the 1,000-asset hard limit;
- surviving assets are byte-identical to the pre-quarantine projection — the
  republish was purely subtractive, so no already-uploaded asset needs replacing.

## Procedure

`release_assets.py` reads each asset's own `release_tag`, so one invocation covers all
13 shards. `RELEASE_TAG` is only a fallback and must stay unset here. All three commands
are idempotent: `upload` skips assets already present remotely.

```bash
export GH_TOKEN=...          # needs contents:write on balaboom123/taiwan-examination-web
export SITE_ID=default
unset RELEASE_TAG MOEX_RELEASE_TAG
```

1. **Preflight, read-only.** Confirm the delta before touching anything.

   ```bash
   python3 .github/scripts/release_assets.py coverage
   ```

   Expect `bootstrap_required: true` for the eight tags above and
   `total expected zips: 3598`.

2. **Create the five missing releases.**

   ```bash
   python3 .github/scripts/release_assets.py ensure
   ```

3. **Upload the 1,327 new assets (7.28 GB).** Batched 50 per `gh` call. This is the
   long step; it is resumable — rerun after any interruption and it continues.

   ```bash
   python3 .github/scripts/release_assets.py upload
   ```

4. **Re-run preflight.** Do not proceed unless `bootstrap_required: false`.

   ```bash
   python3 .github/scripts/release_assets.py coverage
   ```

5. **Push.** Only now. This triggers `deploy-pages.yml`.

   ```bash
   git push -u origin agent/completeness-integration
   ```

   Open a PR to `main` rather than pushing to `main` directly, so CI runs before the
   deploy. See the CI blocker below.

6. **Prune the 37 stale assets** after the deploy is confirmed serving the new catalog.
   Pruning earlier would break the live site for the window between prune and deploy,
   because the current live frontend still links the quarantined bundles.

   ```bash
   python3 .github/scripts/release_assets.py prune
   ```

## Rollback

The projection change is data-only and reversible:

- `git revert` the quarantine checkpoint restores the 34 withheld bundles; their bytes
  were never deleted from `bundles/` or `mirror/`.
- Uploaded assets are additive. Leaving them in place while reverting the site data
  costs storage but breaks nothing.
- Step 6 is the only destructive step, which is why it is last and gated on a confirmed
  deploy.

## Known blocker before merge

`ci.yml` runs `python -m app history-audit --strict` as a blocking gate with no
`continue-on-error`. On this branch that gate **exits 1**, reporting 8 Hakka
`normalized_not_published` events.

This predates the quarantine work — it is the finding recorded by `e55261d`
(`audit: expose Hakka source and publication gaps`) — and the quarantine change is
exit-code neutral: the withheld providers are reported under the separate
`withheld_by_quarantine` status (183 events) precisely so that a deliberate withholding
can never be mistaken for, or silently absorb, an unexplained publication gap.

The 8 Hakka events must be dispositioned before this branch can merge through CI. They
are normalized but unpublished, so the options are to publish them, record them as
publication-policy exclusions, or quarantine `hakka_cert` as well. That is an open
decision, not something this runbook resolves.

## Current strict-audit summary

| Status | Count |
| --- | --- |
| `published_complete` | 978 |
| `excluded_by_publication_policy` | 371 |
| `withheld_by_quarantine` | 183 |
| `blocked` | 13 |
| `normalized_not_published` | 8 |
| `partially_blocked` | 3 |
| `parser_gap` | 0 |
