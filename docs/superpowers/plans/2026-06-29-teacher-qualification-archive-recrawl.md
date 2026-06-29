# Teacher Qualification Archive Recrawl Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the full official 教師資格考試 archive from the national source instead of only the latest year.

**Architecture:** Reuse the existing `teacher_qual` provider and patch only its source-specific parser. The existing sync, mirror, bundler, and default-site publication pipeline handles data output and public JSON.

**Tech Stack:** Python stdlib `HTMLParser` / `urllib`, existing sync CLI, pytest, GitHub Pages data feed.

---

### Task 1: National Source Parser

**Files:**
- Modify: `app/providers/teacher_qual/client.py`
- Modify: `tests/test_teacher_qual.py`

- [x] **Step 1: Add failing parser tests**

Add tests for `099年試題及參考答案`, `107年僅有範例題`, and the `ddlOrder` first/second exam selector.

- [x] **Step 2: Run the focused test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_qual.py -q`

Expected before implementation: fail because order parsing and historical heading handling are missing.

- [x] **Step 3: Patch the provider**

Add `parse_order_options()`, accept zero-padded/sample-only year headings, and route `teacher-qual-108-1` / `teacher-qual-108-2` through the official `ddlOrder` postback.

- [x] **Step 4: Run the focused test again**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_qual.py -q`

Expected: `9 passed`.

### Task 2: Recrawl And Publish Data

**Files:**
- Generated: `data/providers/teacher_qual/**`
- Generated: `data/sites/default/{bundles.json,frontend-bundles.json,release-assets.json}`
- Generated: `bundles/sites/default/teacher-qual.zip`

- [x] **Step 1: Verify live source behavior**

Run a live probe for AD 2019, 2018, 2010, and 2005.

Expected: AD 2019 returns `teacher-qual-108-1` and `teacher-qual-108-2`; AD 2018, 2010, and 2005 each return one downloadable paper.

- [x] **Step 2: Run full provider sync**

Run: `.venv\Scripts\python.exe -m app sync-full --provider teacher_qual --site-id default`

Expected: AD 2005-2026 sync with 0 failures.

- [x] **Step 3: Publish default site**

Run: `.venv\Scripts\python.exe -m app publish-site --site-id default --repository balaboom123/taiwan-examination-web`

Expected: `teacher-qual` in `data/sites/default/bundles.json` has ROC years 115-94 and 23 files.

- [x] **Step 4: Upload refreshed release asset**

Run the release asset upload for `teacher-qual.zip` and compare the downloaded release ZIP checksum with `data/sites/default/bundles.json`.

Expected: the remote `teacher-qual.zip` SHA-256 matches the updated public metadata checksum.
