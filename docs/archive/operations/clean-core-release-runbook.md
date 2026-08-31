# Clean-core release runbook — 2026-08-02

Status: steps 1-4 executed 2026-08-02; steps 5-6 pending
Owner: release and data operators

This runbook ships the recovered MOEX/WDASEC/TCTE/CEEC catalog while withholding the
providers whose published records are known to be wrong.

Execution state as of 2026-08-02:

- **Steps 1–4 are done.** Shards `default-bundles-v2-009` … `-013` were created and all
  1,327 new assets (7.28 GB) were uploaded; the verification preflight reports zero
  missing assets. One asset was pulled back down and its SHA-256 matched the projection
  byte for byte.
- **Steps 5–6 are pending.** No push, no merge, no deployment, and no prune has run, so
  the live site still serves the previous 2,305-bundle catalog.

Read `release-checklist.md` first; this runbook is the current-cycle supplement, not a
replacement.

## Why the ordering matters

`.github/workflows/deploy-pages.yml` triggers on any push to `main` touching
`frontend/**`, `app/**`, `catalog/**`, `data/providers/**`, or `data/sites/default/**`,
and it **only builds the site**. It never touches GitHub Releases; only `sync-full.yml`
does. The site therefore goes live referencing whatever assets happen to exist at that
moment.

The branch added 1,327 assets that did not exist on any release. Pushing first would have
published a catalog in which **1,327 of 3,593 rows (37%) returned 404 on download**.

> Upload assets first. Push second. Never the reverse.

## Current delta

Measured on `agent/completeness-integration` at the quarantine checkpoint against
`origin/main`'s `data/sites/default/release-assets.json`.

| Quantity | Value |
| --- | --- |
| Live assets (per `origin/main`) | 2,308 |
| Branch projection | 3,593 |
| Assets to upload | 1,327 (7.28 GB) |
| Stale assets to prune | 42 |
| Releases to create | 5 (`default-bundles-v2-009` … `-013`) |
| Frontend rows | 2,305 → 3,593 |

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

Prunes are 40 quarantined assets plus 2 superseded orphans, in tags `-001` (16),
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
   `total expected zips: 3593`.

2. **Create the five missing releases.**

   ```bash
   python3 .github/scripts/release_assets.py ensure
   ```

3. **Upload the 1,327 new assets (7.28 GB).** Batched 50 per `gh` call. This is the
   long step; it is resumable — rerun after any interruption and it continues.

   ```bash
   python3 .github/scripts/release_assets.py upload
   ```

4. **Re-run preflight.** The gate here is **zero `missing from release` lines**, not
   `bootstrap_required: false`.

   ```bash
   python3 .github/scripts/release_assets.py coverage 2>&1 | grep -c '^missing from'
   ```

   `bootstrap_required` is raised by *either* a missing asset or an unexpected one, and
   the 42 stale assets are deliberately still present until step 6. It therefore cannot
   read `false` at this point in the sequence — expect `True` on tags `-001`, `-003`,
   and `-008` with `expected < release`, which is the prune backlog and not an upload
   failure. Only a non-zero `missing` count blocks the push.

5. **Push.** Only now. This triggers `deploy-pages.yml`.

   ```bash
   git push -u origin agent/completeness-integration
   ```

   Open a PR to `main` rather than pushing to `main` directly, so CI runs before the
   deploy. See the Hakka disposition below.

6. **Prune the 42 stale assets** after the deploy is confirmed serving the new catalog.
   Pruning earlier would break the live site for the window between prune and deploy,
   because the current live frontend still links the quarantined bundles.

   ```bash
   python3 .github/scripts/release_assets.py prune
   ```

## Rollback

The projection change is data-only and reversible:

- `git revert` the quarantine checkpoint restores the 39 withheld bundles; their bytes
  were never deleted from `bundles/` or `mirror/`.
- Uploaded assets are additive. Leaving them in place while reverting the site data
  costs storage but breaks nothing.
- Step 6 is the only destructive step, which is why it is last and gated on a confirmed
  deploy.

## Hakka disposition

`ci.yml` runs `history-audit --strict` as a blocking gate. It previously exited 1 on 8
Hakka `normalized_not_published` events (AD 2018–2025 basic/elementary), which are now
withheld with the rest of `hakka_cert`.

State this plainly: quarantining `hakka_cert` is what turns that gate green. It is not a
convenience. The provider was verified against its published data to carry the same
defect classes as the other twelve entries, and the withheld events remain visible as
`withheld_by_quarantine` rather than disappearing:

- both published non-basic bundles use a synthetic ROC 115 identity forced by
  `MATERIALS_YEAR` onto undated material absent from the current exam scope
  (`hakka-cert-advanced-2026`, `hakka-cert-intermediate-high-intermediate-2026`);
- 11 ZIPs are published as `listening_audio` because every ZIP suffix is treated as
  audio, including the 5 advanced writing-test ZIPs;
- the 8 historical events were never a small gap: that group is 140 papers totalling
  **30.02 GB**, with three single source files at 2.09 GB each. Publishing it means a
  ~16-part multipart archive of paired audio.
- the Hakka Affairs Council applies Open Government Data License 1.0 but expressly
  carves out audiovisual works, so audio redistribution is unresolved regardless.

Publishing was therefore the worst of the three options. The defects stay recorded in
the provider spec and source manifest; lifting the quarantine is a revert plus a
republish once identity, ZIP role classification, and audio rights are settled.

## Current strict-audit summary

All six CI gates pass at this checkpoint.

| Status | Count |
| --- | --- |
| `published_complete` | 975 |
| `excluded_by_publication_policy` | 371 |
| `withheld_by_quarantine` | 194 |
| `blocked` | 13 |
| `partially_blocked` | 3 |
| `normalized_not_published` | 0 |
| `parser_gap` | 0 |
