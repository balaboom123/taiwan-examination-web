# Recovery Guide

Use this guide when sync, publication, release, or deploy behavior fails.

## Recovery Principles

- preserve provider integrity before publication convenience
- prefer the smallest safe repair path first
- do not mask source failures by manually editing generated outputs unless you are performing an explicit temporary recovery step
- after a manual recovery, rerun a generating command so the repo returns to derived state

## Quick Triage

When something fails, answer these questions first:

1. Did the failure happen during provider fetch, site publication, release publication, frontend download gating, or deploy?
2. Did any generated files change before the failure?
3. Is the problem limited to one provider or does it affect the whole `default` site?
4. Is the site release asset set still complete?
5. Are public download links broken, stale, or merely delayed?

## Scenario 1: Targeted Sync Aborts

Symptoms:

- `sync-targeted` exits non-zero
- logs show download or bundle failures for affected exams

Meaning:

- targeted sync is intentionally strict by default because partial writes for probe-identified changed exams are not safe
- when an official page has a mix of valid files and source-side placeholders, the explicit `--allow-partial` mode can retain the valid subset while recording every failed file; it still exits non-zero

Recovery:

1. inspect `.tmp/source-probe.json`
2. inspect the failing entries in logs
3. rerun targeted sync if the failure was transient
4. if the source is persistently partial and the valid subset is useful, rerun with `--allow-partial`, then run `history-audit` and `publish-site` from the generated publish plan
5. if failures persist across multiple exams or categories, run `sync-incremental` or `sync-full` depending on scope

## Scenario 2: Incremental Or Full Sync Completes With Failures

Symptoms:

- command exits non-zero
- `data/providers/<provider_id>/sync-failures.json` contains entries

Meaning:

- some provider failures were recorded
- incremental mode may have preserved prior state for failed exam IDs

Recovery:

1. inspect `data/providers/<provider_id>/sync-failures.json`
2. determine whether failures are transient download issues, source placeholders, or schema drift
3. rerun incremental sync for MOEX if limited to recent years
4. rerun full sync for the affected provider if state trust is broadly reduced
5. if the source format changed, fix code before rerunning

## Scenario 3: A Source Is Officially Blocked or Expired

Symptoms:

- a source page is retained with no papers, or a valid event has one or more exact download failures
- the response is an official 404, empty-result page, expired/closed listing, or reproducible placeholder

Recovery:

1. capture the official URL, status, byte count, SHA-256, parser observation, and capture date
2. add or update `catalog/source-coverage/<provider_id>.json` with the narrowest event/file exception; do not mark a whole event blocked when valid records remain
3. run `python3 -m app history-audit --strict` and inspect `.tmp/history-audit.json`
4. for file-level blockers, run `python3 scripts/validate_publication.py`; the validator accepts only exact current download failures represented by the ledger
5. re-probe after the source changes. A repaired file becomes an orphan exception, and new material creates a conflict; both intentionally fail strict audit until reviewed

Do not delete the raw page, mirror, failure record, or evidence ledger entry merely to make a gate pass.

## Scenario 4: Release Coverage Mismatch

Symptoms:

- release coverage reports missing or unexpected ZIP assets
- scheduled sync chooses bootstrap mode

Meaning:

- release assets no longer match generated `data/sites/default/release-assets.json`

Recovery:

1. ensure `python -m app publish-site --site-id default --repository <owner>/<repo>` completed successfully
2. verify `data/sites/default/release-assets.json`
3. run or rerun `python .github/scripts/release_assets.py ensure`
4. run or rerun `python .github/scripts/release_assets.py upload`
5. run `python .github/scripts/release_assets.py prune`
6. verify each site-owned release tag after upload and prune complete

## Scenario 5: Social-Gated Downloads Look Wrong

Symptoms:

- frontend links do not resolve as expected
- first click opens the wrong LINE channel
- second click still does not open the ZIP

Recovery:

1. verify `data/sites/default/bundles.json` exists and reflects the current bundles
2. verify the frontend category mapping in `frontend/src/lib/social-gate.ts`
3. run the frontend tests and build
4. redeploy after fixing code or generated bundle metadata

Important:

- there is no generated gating manifest
- the social gate is client-side; it cannot verify LINE membership

## Scenario 6: Frontend Deploy Fails

Symptoms:

- `deploy-pages.yml` fails
- frontend build cannot read bundle data

Recovery:

1. verify generated `data/sites/default/bundles.json`
2. run locally:

```bash
cmd /c "cd /d frontend && npm test"
cmd /c "cd /d frontend && npm run build"
```

3. rerun deploy workflow after fixing data or build issues

## Scenario 6: Bundle URLs Or Public Downloads Look Wrong

Symptoms:

- bundle link points to wrong release tag
- bundle link exists but serves stale content

Recovery:

1. verify the assigned `release_tag` in `data/sites/default/bundles.json`
2. verify the generated entries in `data/sites/default/release-assets.json`
3. rerun site publication if provider state is correct:

```bash
python -m app publish-site --site-id default --repository <owner>/<repo>
```

4. republish release assets with `release_assets.py upload`

## Scenario 7: Alias Or Normalization Drift

Symptoms:

- review queue grows unexpectedly
- categories that should merge remain split

Recovery:

1. inspect `data/providers/<provider_id>/review-queue.json`
2. update `data/aliases.json` if a manual alias rule is appropriate
3. rerun bundle or sync generation so the new alias rules are applied

## Scenario 8: CEEC GSAT Sync Or Publication Fails

Symptoms:

- `sync-ceec-gsat.yml` fails
- `python -m app sync-full --provider ceec_gsat --site-id default` exits non-zero
- CEEC records are missing from `data/sites/default/bundles.json`

Recovery:

1. inspect `data/providers/ceec_gsat/sync-failures.json`
2. verify `mirror/providers/ceec_gsat/` contains the expected downloads
3. rerun the CEEC provider sync
4. rerun `python -m app publish-site --site-id default --repository <owner>/<repo>` only after every required provider state and mirror input for `default` is present
5. rerun release publication if the site bundle metadata changed

## Scenario 9: Legacy State Migration Verify Fails

Symptoms:

- `python -m app migrate-legacy-state --provider moex --site-id default --mode verify` exits non-zero
- output reports `Conflict` lines or `Pending promotion` lines

Meaning:

- the final scoped-path cutover is incomplete, or a scoped target already differs from the root legacy source

Recovery:

1. run `python -m app migrate-legacy-state --provider moex --site-id default --mode dry-run`
2. if verify reported only pending promotion, rerun:

```bash
python -m app migrate-legacy-state --provider moex --site-id default --mode move
python -m app migrate-legacy-state --provider moex --site-id default --mode verify
```

3. if verify reported conflicts, inspect both paths before deleting anything
4. do not redownload MOEX mirror or bundle artifacts unless the local data is actually missing or corrupted
5. do not delete the old root files until verify passes

## Scenario 10: New Provider Work Started Without Proper Scoping

Symptoms:

- new code writes more root-level global files
- workflows still assume MOEX-only ownership

Recovery:

1. stop rollout of the new provider
2. check `docs/developer/extension-rules.md`
3. move generated outputs to provider or site scope
4. update operator docs before retrying the rollout

## Post-Incident Actions

After recovery, decide whether the issue requires:

- code fix
- workflow fix
- doc update
- onboarding checklist update

If the incident exposed a missing procedure, update this recovery document and the runbook in the same change.
