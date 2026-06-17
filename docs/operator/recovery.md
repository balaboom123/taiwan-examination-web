# Recovery Guide

Use this guide when sync, publication, release, or deploy behavior fails.

## Recovery Principles

- preserve provider integrity before publication convenience
- prefer the smallest safe repair path first
- do not mask source failures by manually editing generated outputs unless you are performing an explicit temporary recovery step
- after a manual recovery, rerun a generating command so the repo returns to derived state

## Quick Triage

When something fails, answer these questions first:

1. Did the failure happen during source fetch, bundle build, release publication, gating, or deploy?
2. Did any generated files change before the failure?
3. Is the problem limited to recent exams or does it affect the whole dataset?
4. Is the release asset set still complete?
5. Are public download links broken, stale, or merely delayed?

## Scenario 1: Targeted Sync Aborts

Symptoms:

- `sync-targeted` exits non-zero
- logs show download or bundle failures for affected exams

Meaning:

- targeted sync is intentionally strict because partial writes for probe-identified changed exams are not safe

Recovery:

1. inspect `.tmp/source-probe.json`
2. inspect the failing entries in logs
3. rerun targeted sync if the failure was transient
4. if failures persist across multiple exams or categories, run `sync-incremental` or `sync-full` depending on scope

## Scenario 2: Incremental Or Full Sync Completes With Failures

Symptoms:

- command exits non-zero
- `data/sync-failures.json` contains entries

Meaning:

- some provider failures were recorded
- incremental mode may have preserved prior state for failed exam IDs

Recovery:

1. inspect `data/sync-failures.json`
2. determine whether failures are transient download issues, source placeholders, or schema drift
3. rerun incremental sync if limited to recent years
4. rerun full sync if state trust is broadly reduced
5. if the source format changed, fix code before rerunning

## Scenario 3: Release Coverage Mismatch

Symptoms:

- release coverage reports missing or unexpected ZIP assets
- scheduled sync chooses bootstrap mode

Meaning:

- release assets no longer match generated `data/release-assets.json`

Recovery:

1. ensure bundles were built locally or by workflow
2. run or rerun release asset publication
3. if using automation, prefer `sync-full.yml` for a clean rebuild
4. verify the release after upload and prune complete

## Scenario 4: LootLabs Links Are Missing Or Stale

Symptoms:

- frontend links do not resolve as expected
- `sync-lootlabs` fails
- LootLabs manifest entries do not match current bundle URL or checksum

Recovery:

1. verify `LOOTLABS_API_KEY`
2. verify `data/bundles.json` exists and reflects the current bundles
3. rerun:

```bash
python -m app sync-lootlabs
```

4. if link creation still fails, inspect provider response behavior and check whether the upstream API changed

Important:

- do not edit `data/lootlabs-links.json` by hand as a permanent fix
- refresh from generated bundle metadata instead

## Scenario 5: Frontend Deploy Fails

Symptoms:

- `deploy-pages.yml` fails
- frontend build cannot read bundle data or LootLabs manifest

Recovery:

1. verify generated `data/bundles.json`
2. verify `data/lootlabs-links.json` if gating is enabled
3. run locally:

```bash
cd frontend
npm test
npm run build
```

4. rerun deploy workflow after fixing data or build issues

## Scenario 6: Bundle URLs Or Public Downloads Look Wrong

Symptoms:

- bundle link points to wrong release tag
- bundle link exists but serves stale content

Recovery:

1. verify the `--bundle-base-url` used for the last generation
2. verify `data/bundles.json`
3. rebuild bundles if normalized data is correct:

```bash
python -m app build-bundles --bundle-base-url "https://github.com/<owner>/<repo>/releases/download/moex-bundles"
```

4. republish release assets
5. rerun `sync-lootlabs` if gating is enabled

## Scenario 7: Alias Or Normalization Drift

Symptoms:

- review queue grows unexpectedly
- categories that should merge remain split

Recovery:

1. inspect `data/review-queue.json`
2. update `data/aliases.json` if a manual alias rule is appropriate
3. rerun bundle or sync generation so the new alias rules are applied

## Scenario 8: New Provider Work Started Without Proper Scoping

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
