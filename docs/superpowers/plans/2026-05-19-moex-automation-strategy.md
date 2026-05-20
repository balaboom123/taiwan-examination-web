# MOEX Automation Strategy And Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce unnecessary MOEX crawling, shorten scheduled sync runtime, and keep repository updates limited to real source changes.

**Architecture:** Add a probe-first pipeline that stores cheap remote fingerprints in `data/source-manifest.json`, then runs targeted sync only for changed exams. Keep the current `sync-full` behavior available for manual rebuilds and audits, but make weekly automation default to low-cost checks, targeted downloads, and affected-bundle rebuilds only.

**Tech Stack:** Python 3.12 standard library, existing `app.crawler.MoexClient`, existing JSON data files in `data/`, GitHub Actions, GitHub Releases for canonical bundle assets.

---

## 1. Purpose

This plan extends the current strategy document into an implementation-ready design. It is based on the existing code in `app/cli.py`, `app/crawler.py`, `app/sync.py`, `app/state.py`, `app/bundler.py`, and the current workflows under `.github/workflows/`.

The main objective is not to make the crawler more aggressive. The objective is to make it decide earlier when no expensive work is needed.

## 2. Current System Summary

### Existing Commands

- `python -m app discover`
  - Discovers years and exam options from the live MOEX search page.
  - Writes only stdout unless a workflow uploads it as an artifact.
- `python -m app sync-full`
  - Discovers target years.
  - Fetches each exam result page.
  - Downloads attachments and paper files into `mirror/`.
  - Normalizes data and rebuilds all bundles.
- `python -m app sync-incremental --years 1`
  - Discovers the latest `1` year.
  - Fetches all exams in that latest year.
  - Downloads files if they are missing from local `mirror/`.
  - Merges refreshed exams into existing `data/*.json`.
  - Rebuilds only affected canonical bundles.
- `python -m app build-site`
  - Rebuilds the static site from existing `data/papers.json` and `data/bundles.json`.

### Existing Workflow Behavior

- `discover.yml`
  - Manual only.
  - Uploads `discover.json` as an artifact.
  - Does not update repo state.
- `sync-full.yml`
  - Manual only.
  - Rebuilds the full data set and release bundles.
- `sync-incremental.yml`
  - Weekly Monday `03:15 UTC`, `11:15 Asia/Taipei`.
  - Downloads all existing release bundle zips before knowing which canonical IDs are affected.
  - Runs `sync-incremental --years 1`.
  - Commits `data` and `site` if changed.

### Key Existing Strengths

- `sync_exam_pages()` already reuses local `mirror/` files.
- `merge_incremental_state()` already preserves older state and identifies `affected_canonical_ids`.
- `build_bundles()` already rebuilds only the catalog passed into it and can reuse entries from existing bundle zips.

### Key Existing Gaps

- There is no persistent remote-source manifest.
- There is no cheap no-change exit before file download work.
- GitHub Actions fresh runners do not have `mirror/`, so local mirror reuse is mostly ineffective there.
- Attachments are downloaded but not surfaced in `papers.json`, bundles, or `site/index.html`.
- Existing bundles are downloaded all at once instead of only for affected canonical IDs.

## 3. Live-Site Findings

The following observations were measured against MOEX on `2026-05-19` using the project CA bundle.

### MOEX Shape

- Available years discovered from the search page: `35`
- Latest year: `2026`
- `2026` exam count: `4`
- `2026` exam page sizes by parsed content:
  - `115040`: `287` papers, `2` attachments, `447` paper file links
  - `115030`: `16` papers, `2` attachments, `35` paper file links
  - `115020`: `42` papers, `1` attachment, `110` paper file links
  - `115010`: `64` papers, `2` attachments, `128` paper file links
- Latest-year total: `720` paper file links plus `7` attachments

### HTTP Signal Quality

`HEAD` works, but the site does not provide strong validators:

- `Last-Modified`: not present
- `ETag`: not present
- `Cache-Control`: `private`
- `Content-Length`: present
- File `Content-Disposition`: present

This means the strategy must treat `Content-Length` as a weak fingerprint. It is useful for skipping expensive work most weeks, but it cannot be the only correctness mechanism.

## 4. Strategy

### Recommended Strategy

Use a layered pipeline:

1. **Probe first:** Run cheap `HEAD` and small `GET` checks to determine candidate changes.
2. **Sync targets only:** Run deep parsing and file downloads only for changed exams.
3. **Download bundles on demand:** Fetch only existing bundle zips needed to rebuild affected canonical IDs.
4. **Audit periodically:** Use monthly deep sync for recent years to catch silent replacements that weak fingerprints can miss.
5. **Keep full sync manual:** Preserve `sync-full` as an explicit recovery and full rebuild command.
6. **Do not commit volatile probe metadata:** Request counts and run timestamps belong in workflow summaries or temporary probe output, not in committed source state.

### Non-Goals

- Do not make every file request concurrent by default.
- Do not rely on `ETag` or `Last-Modified`.
- Do not make `discover` artifacts the main source of state.
- Do not remove `sync-full`.
- Do not make weekly automation download all `mirror/` content unless measurement proves it is cheaper than targeted requests.

## 5. Data Model

### New File: `data/source-manifest.json`

This file records remote-source fingerprints, not downloaded file contents.

Recommended schema:

```json
{
  "schema_version": 1,
  "probe_policy": {
    "year_window": 2,
    "fingerprint_version": 1,
    "download_attachments_by_default": false
  },
  "years": {
    "2026": {
      "year_ad": 2026,
      "year_roc": 115,
      "search_url": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y=2026",
      "head_content_length": 800964,
      "exam_codes": ["115040", "115030", "115020", "115010"],
      "exam_codes_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
      "last_changed_at": "2026-05-20T00:00:00+08:00",
      "last_deep_sync_at": "2026-05-19T00:00:00+08:00"
    }
  },
  "exams": {
    "115040": {
      "source_exam_id": "115040",
      "year_ad": 2026,
      "year_roc": 115,
      "result_url": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?e=115040&y=2026",
      "head_content_length": 538982,
      "exam_name_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
      "paper_count": 287,
      "attachment_count": 2,
      "file_link_count": 447,
      "paper_url_hash": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
      "last_changed_at": "2026-05-20T00:00:00+08:00",
      "last_deep_sync_at": "2026-05-19T00:00:00+08:00"
    }
  },
  "files": {
    "115040/101/0101/question": {
      "source_exam_id": "115040",
      "category_code": "101",
      "subject_code": "0101",
      "file_type": "question",
      "download_url_source": "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?t=Q&code=115040&c=101&s=0101&q=1",
      "head_content_length": 214173,
      "content_disposition": "filename=\"115040_10110(1101).pdf\"",
      "last_changed_at": "2026-05-20T00:00:00+08:00"
    }
  }
}
```

### Manifest Rules

- `schema_version` must be required.
- Hashes must be deterministic and stable across dictionary ordering.
- `paper_url_hash` should include `category_code`, `subject_code`, `subject_name_raw`, `file_type`, and `download_url_source`.
- File-level entries should be optional in Phase 1 and populated only when file `HEAD` probing is enabled.
- Manifest writes must be sorted and stable to avoid meaningless commits.
- Committed manifest data must not include routine run timestamps. A no-change probe must produce no file diff in `data/source-manifest.json`.
- `last_changed_at` changes only when the corresponding fingerprint changes. `last_deep_sync_at` changes only after a targeted sync or audit changes durable source state; no-change probes do not touch it.

## 6. Command Design

### New Command: `probe-latest`

Purpose: detect changed years and exams with minimal network cost.

Recommended CLI:

```bash
python -m app probe-latest --years 2 --manifest data/source-manifest.json --output .tmp/source-probe.json
```

Behavior:

- Load existing `data/source-manifest.json` if present.
- Discover available years.
- Probe the latest `N` years.
- Use `HEAD` on each target year search URL.
- If year `Content-Length` differs or the year is missing from manifest, fetch that year search page and compare exam codes.
- Use `HEAD` on known exam result pages.
- If exam `Content-Length` differs, fetch and parse the exam result page to compute `paper_url_hash`.
- Write `.tmp/source-probe.json` with changed exam IDs, request counts, and run timestamp.
- Update `data/source-manifest.json` only when asked with `--write-manifest` and only when durable fingerprints changed.
- Keep `.tmp/source-probe.json` out of committed state.

Output shape:

```json
{
  "schema_version": 1,
  "generated_at": "2026-05-20T00:00:00+08:00",
  "changed_years": [2026],
  "changed_exam_codes": ["115040"],
  "removed_exam_codes": [],
  "unchanged_exam_codes": ["115030", "115020", "115010"],
  "should_sync": true,
  "request_counts": {
    "head": 5,
    "get": 2,
    "download": 0
  }
}
```

### New Command: `sync-targeted`

Purpose: deep-sync only changed exams and rebuild affected bundles.

Recommended CLI:

```bash
python -m app sync-targeted --probe .tmp/source-probe.json --bundle-base-url "https://github.com/${GITHUB_REPOSITORY}/releases/download/moex-bundles"
```

Behavior:

- Read `.tmp/source-probe.json`.
- If `should_sync` is `false`, exit `0` without changing `data`, `site`, or bundles.
- Fetch only `changed_exam_codes`.
- Default to not downloading exam-level attachments.
- Merge refreshed exams into existing state.
- Compute `affected_canonical_ids`.
- Rebuild only affected bundles.
- Update `data/source-manifest.json` after a successful sync only when durable fingerprints changed or refreshed source state changed.

### Existing Command Changes

- Add `--download-attachments` to `sync-full`, `sync-incremental`, and `sync-targeted`.
- Default `--download-attachments`:
  - `sync-full`: `true`
  - `sync-incremental`: `false`
  - `sync-targeted`: `false`
- Keep `sync-incremental --years N` as a compatibility wrapper until `sync-targeted` is stable.

## 7. Crawler And Sync Design

### New Module: `app/probe.py`

Responsibilities:

- Build probe URLs.
- Run `HEAD` requests through the same SSL context and user agent as `MoexClient`.
- Represent probe results as dataclasses.
- Compute deterministic hashes.
- Compare current probe results against `source-manifest.json`.

### New Module: `app/manifest.py`

Responsibilities:

- Load missing manifest as an empty manifest.
- Validate `schema_version`.
- Convert manifest JSON into dataclasses.
- Serialize stable JSON with sorted keys.
- Merge new probe and sync results into existing manifest.

### Changes To `app/crawler.py`

Add these methods:

```python
def head(self, url: str) -> ResponseMetadata:
    """Return response headers without reading the response body."""

def fetch_search_page(self, year_ad: int | None = None) -> SearchPageData:
    """Fetch and parse the MOEX search page for all years or one year."""
```

`ResponseMetadata` should include:

- `url`
- `status`
- `content_length`
- `content_type`
- `content_disposition`
- `cache_control`

### Changes To `app/sync.py`

Add an option:

```python
download_attachments: bool = True
```

When `download_attachments` is `false`:

- Keep parsed attachment metadata in `SourceExamPage.attachments`.
- Do not call `download_file()` for attachments.
- Leave attachment `storage_key`, `asset_name`, `checksum`, and `download_url_mirror` empty.
- Do not record a failure for skipped attachments.

### Changes To `app/state.py`

Add a helper that supports targeted sync by exam code:

```python
def merge_targeted_state(
    existing_raw_pages: list[SourceExamPage],
    existing_catalog: NormalizedCatalog,
    existing_bundles: list[BundleAsset],
    refreshed_raw_pages: list[SourceExamPage],
    refreshed_catalog: NormalizedCatalog,
    removed_exam_ids: set[str],
) -> tuple[list[SourceExamPage], NormalizedCatalog, list[BundleAsset], set[str]]:
    """Merge refreshed and removed exams, preserving unaffected state."""
```

The existing `merge_incremental_state()` can be reused if targeted sync passes only refreshed pages, but a named targeted helper will make the behavior easier to test and reason about.

## 8. Workflow Design

### New Workflow: `.github/workflows/probe-latest.yml`

Schedule:

- Weekly at first. Increase frequency only after workflow summaries show no-change runs stay under `20` total requests.
- Suggested cron: `15 3 * * 1`, same as current incremental schedule.

Behavior:

- Checkout repository.
- Setup Python.
- Run `mkdir -p .tmp && python -m app probe-latest --years 2 --write-manifest --output .tmp/source-probe.json`.
- If `.tmp/source-probe.json` says `should_sync=false`, exit before `git add` unless `data/source-manifest.json` has a durable fingerprint diff.
- If `should_sync=true`, call `sync-targeted` in the same job. Upload `source-probe.json` as a debugging artifact only.

Recommended first implementation: keep probe and targeted sync in the same workflow job. That avoids artifact plumbing and keeps behavior easier to debug.

### Replace `sync-incremental.yml` Behavior

Target shape:

1. Ensure release exists.
2. Run `probe-latest`.
3. Stop early when `should_sync=false`.
4. Resolve affected bundle asset names after targeted merge.
5. Download only affected existing bundle zips.
6. Run targeted bundle rebuild.
7. Upload changed bundles.
8. Commit changed `data`, `site`, and `data/source-manifest.json`.

### Keep `sync-full.yml`

`sync-full.yml` remains manual. It should eventually run:

```bash
python -m app sync-full --download-attachments
```

This preserves a conservative full-rebuild path.

### New Workflow: `.github/workflows/audit-recent.yml`

Schedule:

- Monthly.
- Suggested cron: `45 3 1 * *`, which is `11:45 Asia/Taipei` on the first day of each month.

Behavior:

- Run a deeper sync against latest `1` or `2` years.
- Allow attachment download only if product requirements say attachments matter.
- Update `source-manifest.json`.
- Commit only if data, site, bundle metadata, or durable manifest fingerprints changed.

## 9. Bundle Release Strategy

### Problem In Current Workflow

`sync-incremental.yml` downloads all `*.zip` release assets before the code knows which canonical IDs changed.

### Target Behavior

- Keep `data/bundles.json` as the full bundle index.
- After targeted merge, compute `affected_canonical_ids`.
- Map `affected_canonical_ids` to asset names from existing `data/bundles.json`.
- Download only those zip assets into `bundles/`.
- Rebuild only affected bundles.
- Preserve unaffected `BundleAsset` records from existing state.

### Stale Asset Deletion

Do not delete release assets inside the first targeted-sync implementation unless a full desired release index is available. Stale deletion should run only when `data/release-assets.json` represents the complete desired set, not just changed bundles.

## 10. Rate Limits And Failure Policy

### Request Policy

- Default to serial requests.
- Add optional low concurrency only after measurement.
- Use the current user agent.
- Add jitter between requests:
  - `HEAD`: `0.2s` to `0.5s`
  - page `GET`: `0.5s` to `1.5s`
  - file download: `1.0s` to `2.0s`
- Use exponential backoff for `429`, `500`, `502`, `503`, and `504`.

### Failure Behavior

- Probe failure should fail the workflow, not silently run a full sync.
- Targeted sync file failures should keep existing partial-success behavior and write `sync-failures.json`.
- Manifest should update only after a successful probe or sync phase.
- If a probe detects a removed exam code, targeted sync must remove that exam from merged state and mark its previous canonical IDs as affected.

## 11. Measurement Plan

Add request counting to probe and sync output.

Metrics to record in `.tmp/source-probe.json` or workflow summary:

- `year_head_count`
- `year_get_count`
- `exam_head_count`
- `exam_get_count`
- `file_head_count`
- `file_download_count`
- `changed_exam_count`
- `affected_canonical_count`
- `elapsed_seconds`

Target outcomes:

- No-change weekly run:
  - `file_download_count = 0`
  - `changed_exam_count = 0`
  - no bundle upload
  - no `site` rebuild commit
- Single-exam change:
  - only one exam result page deep-parsed
  - only new or missing file links downloaded
  - only affected canonical bundles uploaded

## 12. Implementation Tasks

### Task 1: Attachment Download Flag

**Files:**

- Modify: `app/sync.py`
- Modify: `app/cli.py`
- Modify: `tests/test_sync.py`
- Modify: `tests/test_cli.py`

- [ ] Add `download_attachments: bool = True` to `sync_exam_pages()`.
- [ ] Skip attachment downloads when `download_attachments=False`.
- [ ] Keep parsed attachments in raw pages even when skipped.
- [ ] Add CLI flag `--download-attachments`.
- [ ] Set defaults: full sync true, incremental false.
- [ ] Add tests proving incremental skips attachment downloads and full sync can still opt in.
- [ ] Run `python -m pytest tests/test_sync.py tests/test_cli.py -q`.

### Task 2: Manifest Model

**Files:**

- Create: `app/manifest.py`
- Create: `tests/test_manifest.py`

- [ ] Define manifest dataclasses or typed dict helpers.
- [ ] Implement `load_source_manifest(path)`.
- [ ] Implement `write_source_manifest(path, manifest)`.
- [ ] Ensure missing file loads as schema version `1` with empty sections.
- [ ] Ensure JSON output is deterministic.
- [ ] Add tests for missing file, invalid schema, and stable serialization.
- [ ] Run `python -m pytest tests/test_manifest.py -q`.

### Task 3: Probe Client

**Files:**

- Modify: `app/crawler.py`
- Create: `app/probe.py`
- Create: `tests/test_probe.py`

- [ ] Add `ResponseMetadata`.
- [ ] Add `MoexClient.head(url)`.
- [ ] Add deterministic hash helpers for exam codes and paper URLs.
- [ ] Implement probe comparison against manifest.
- [ ] Add fake-client tests for unchanged year, changed year, changed exam, and new exam.
- [ ] Run `python -m pytest tests/test_probe.py tests/test_crawler.py -q`.

### Task 4: `probe-latest` CLI

**Files:**

- Modify: `app/cli.py`
- Modify: `tests/test_cli.py`

- [ ] Add parser for `probe-latest`.
- [ ] Support `--years`, `--manifest`, `--output`, and `--write-manifest`.
- [ ] Print or write probe summary JSON.
- [ ] Exit `0` for both changed and unchanged probes.
- [ ] Add `.tmp/` to `.gitignore` so local probe outputs are not accidentally committed.
- [ ] Add CLI parser tests and command tests using a fake probe service injected through a small helper function.
- [ ] Run `python -m pytest tests/test_cli.py tests/test_probe.py -q`.

### Task 5: Targeted Sync

**Files:**

- Modify: `app/cli.py`
- Modify: `app/state.py`
- Modify: `app/sync.py`
- Modify: `tests/test_incremental.py`
- Modify: `tests/test_cli.py`

- [ ] Add `sync-targeted` parser.
- [ ] Read changed exam codes from `source-probe.json`.
- [ ] Exit without writes when `should_sync=false`.
- [ ] Fetch only changed exam codes.
- [ ] Remove deleted exam codes from merged state.
- [ ] Compute affected canonical IDs from removed and refreshed exams.
- [ ] Rebuild only affected bundles.
- [ ] Add tests for no-change, one changed exam, and removed exam.
- [ ] Run `python -m pytest tests/test_incremental.py tests/test_cli.py tests/test_sync.py -q`.

### Task 6: Targeted Bundle Download Workflow

**Files:**

- Modify: `.github/workflows/sync-incremental.yml`
- Modify: `tests/test_workflows.py`

- [ ] Replace full release bundle download with affected-bundle download.
- [ ] Keep release creation.
- [ ] Ensure stale asset deletion only runs with a complete release asset list.
- [ ] Add tests asserting the workflow does not download all `*.zip` before probe.
- [ ] Add tests asserting the workflow can exit early on no-change.
- [ ] Run `python -m pytest tests/test_workflows.py -q`.

### Task 7: Monthly Audit Workflow

**Files:**

- Create: `.github/workflows/audit-recent.yml`
- Modify: `tests/test_workflows.py`
- Modify: `README.md`

- [ ] Add monthly workflow.
- [ ] Use low-frequency deep sync against latest `1` or `2` years.
- [ ] Document audit purpose and schedule.
- [ ] Add workflow tests for cron and command.
- [ ] Run `python -m pytest tests/test_workflows.py -q`.

### Task 8: Documentation And Final Verification

**Files:**

- Modify: `README.md`
- Modify: `.gitignore`

- [ ] Document command roles.
- [ ] Document attachment policy.
- [ ] Document no-change behavior.
- [ ] Document full sync recovery path.
- [ ] Ensure `.tmp/` is ignored.
- [ ] Run full test suite: `python -m pytest -q`.

## 13. Rollout Plan

### Phase 0: Low-Risk Download Reduction

Implement Task 1 first.

Acceptance criteria:

- Weekly incremental no longer downloads attachments by default.
- Full sync can still download attachments explicitly or by default.
- Existing paper file behavior is unchanged.

### Phase 1: Probe Without Behavior Change

Implement Tasks 2 to 4.

Acceptance criteria:

- `probe-latest` can run manually.
- It writes `source-probe.json`.
- It can update `source-manifest.json`.
- Existing `sync-incremental` workflow still works.

### Phase 2: Targeted Sync Behind Manual Trigger

Implement Task 5.

Acceptance criteria:

- `sync-targeted` can be run manually with a saved probe file.
- No-change probe exits without data or site changes.
- One changed exam refreshes only that exam.

### Phase 3: Replace Weekly Incremental

Implement Task 6.

Acceptance criteria:

- Weekly workflow runs probe first.
- No-change run exits before PDF downloads and bundle uploads.
- Changed run uploads only affected bundles.

### Phase 4: Add Audit

Implement Task 7.

Acceptance criteria:

- Monthly audit exists.
- It provides a correctness backstop for weak fingerprints.
- Manual `sync-full` remains available for full recovery.

## 14. Risks And Mitigations

### Risk: `Content-Length` misses silent file replacement

Mitigation:

- Treat it as a weak signal only.
- Use `paper_url_hash` after parsing changed result pages.
- Run monthly audit for recent years.
- Keep manual full sync.

### Risk: Removed exams leave stale data

Mitigation:

- Track `removed_exam_codes` in `source-probe.json`.
- Remove matching raw pages and normalized papers during targeted merge.
- Mark previous canonical IDs as affected.

### Risk: Stale release assets are deleted incorrectly

Mitigation:

- Do not run stale deletion unless `release-assets.json` is a complete desired asset list.
- Keep existing full-sync stale cleanup path separate from targeted upload logic.

### Risk: Probe mutates manifest even when sync fails

Mitigation:

- Probe may write `source-probe.json`.
- Manifest `last_deep_sync_at` should update only after successful targeted sync changes durable source state.
- Workflow should not commit a manifest that claims a deep sync succeeded when it did not.

### Risk: Request count increases from too many file `HEAD`s

Mitigation:

- Phase 1 and 2 should avoid file-level `HEAD` by default.
- Add file-level `HEAD` only for changed exams, manual audits, or specific repair flows.

## 15. Completion Definition

The strategy is complete when:

- A no-change weekly run performs no file downloads.
- A no-change weekly run performs no bundle uploads.
- A changed weekly run touches only changed exams and affected canonical bundles.
- `sync-full` still works as a manual recovery command.
- Attachments are not downloaded by weekly automation unless explicitly enabled.
- Tests cover parser behavior, manifest behavior, probe decisions, targeted merge behavior, and workflow guardrails.

## 16. Recommended Next Action

Start with Task 1, then Task 2. Task 1 gives immediate request reduction with small blast radius. Task 2 creates the durable state needed for every later optimization.
