# Taipei Elementary Teacher Recruitment Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the official 臺北市國小教師甄試 source as a current-year scoped 教甄 provider and crawl its public PDF files.

**Architecture:** Implement one source-specific provider, not a generic 教甄 crawler. The provider maps reviewed official article URLs to exam years, decodes `Download.ashx` filenames, mirrors `含答案` PDFs as `question_answer`, and publishes through the existing `default` site.

**Tech Stack:** Python provider/client pattern, existing sync pipeline, unittest/pytest tests, GitHub Actions provider-only workflow.

---

### Task 1: Provider Tests

**Files:**
- Create: `tests/test_teacher_recruit_taipei_elementary.py`
- Modify: `tests/test_normalizer.py`
- Modify: `tests/test_site_registry.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Write parser/client tests**

Create tests that import `TaipeiElementaryRecruitClient` and `parse_downloads`, feed fixture HTML with two `Download.ashx` PDF links and one ODT appeal link, and assert:

```python
self.assertEqual([download.file_type for download in downloads], ["question_answer", "question_answer"])
self.assertEqual([download.subject_name for download in downloads], ["基礎類科知能", "普通科"])
self.assertEqual([download.subject_code for download in downloads], ["basic-category-knowledge", "general"])
```

- [ ] **Step 2: Verify RED**

Run:

```powershell
& 'D:\user\WebstormProjects\taiwan_examination_web\.venv\Scripts\python.exe' 'D:\user\WebstormProjects\taiwan_examination_web\tests\test_teacher_recruit_taipei_elementary.py'
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.providers.teacher_recruit_taipei_elementary'`.

### Task 2: Provider Implementation

**Files:**
- Create: `app/providers/teacher_recruit_taipei_elementary/__init__.py`
- Create: `app/providers/teacher_recruit_taipei_elementary/client.py`
- Create: `app/providers/teacher_recruit_taipei_elementary/provider.py`

- [ ] **Step 1: Implement filename decoding**

Decode official `Download.ashx` filenames by checking `n`, then `u`, then URL path basename:

```python
def _decode_download_name(url: str) -> str:
    parsed = urlparse(url)
    values = parse_qs(parsed.query)
    for key in ("n", "u"):
        encoded = values.get(key, [""])[0]
        if encoded:
            decoded = _decode_base64_query_value(encoded)
            return Path(decoded).name
    return Path(unquote(parsed.path)).name
```

- [ ] **Step 2: Implement paper parsing**

Keep only PDF filenames containing `含答案`, strip sequence numbers and `_含答案`, and emit `question_answer` downloads.

- [ ] **Step 3: Implement client/provider methods**

Use `ARTICLE_URLS_BY_YEAR = {2025: "<official Taipei article URL>"}` and emit `SourceExamPage` with source id `teacher-recruit-taipei-elementary-114`.

- [ ] **Step 4: Verify GREEN**

Run the provider test file again. Expected: 3 tests pass.

### Task 3: Registry, Workflow, And Docs

**Files:**
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Create: `.github/workflows/sync-teacher-recruit-taipei-elementary.yml`
- Create: `docs/developer/providers/teacher_recruit_taipei_elementary-spec.md`
- Modify: `docs/developer/providers/teacher_recruit-source-index.md`
- Modify: `docs/developer/providers/teacher_recruit_city_sources-spec.md`
- Modify: `docs/developer/providers/requested-topic-support.md`
- Modify: `docs/superpowers/spec/2026-06-28-teacher-exams-design.md`

- [ ] **Step 1: Register provider**

Add `teacher_recruit_taipei_elementary` to provider registry, default site provider list, and default site `public_min_years_by_canonical_prefix`.

- [ ] **Step 2: Add canonical mapping**

Map `teacher-recruit-taipei-elementary-` to `teacher-recruit-taipei-elementary` / `臺北市國小教師甄試`.

- [ ] **Step 3: Add provider-only workflow**

Create `sync-teacher-recruit-taipei-elementary.yml` scheduled at `55 5 * * 2` and run:

```yaml
python -m app sync-full --provider teacher_recruit_taipei_elementary --site-id default
```

- [ ] **Step 4: Update specs**

Record the source as implemented, official, public, downloadable, and current-year scoped. Keep the broader 教甄 source family marked partial.

### Task 4: Crawl And Verify

**Files:**
- Generated/modified: `data/providers/teacher_recruit_taipei_elementary/**`
- Generated/modified: `mirror/providers/teacher_recruit_taipei_elementary/**`
- Generated/modified: `data/sites/default/**`

- [ ] **Step 1: Crawl provider**

Run:

```powershell
uv run python -m app sync-full --provider teacher_recruit_taipei_elementary --site-id default
```

Expected: one ROC 114 exam, 12 mirrored official PDFs, no provider failures.

- [ ] **Step 2: Run targeted verification**

Run:

```powershell
& 'D:\user\WebstormProjects\taiwan_examination_web\.venv\Scripts\python.exe' 'D:\user\WebstormProjects\taiwan_examination_web\tests\test_teacher_recruit_taipei_elementary.py'
& 'D:\user\WebstormProjects\taiwan_examination_web\.venv\Scripts\python.exe' -m unittest discover -s 'D:\user\WebstormProjects\taiwan_examination_web\tests' -p 'test_site_registry.py'
```

Expected: all targeted tests pass.

- [ ] **Step 3: Inspect feed count**

Read `data/sites/default/bundles.json` and confirm `臺北市國小教師甄試` appears with 12 files.

### Task 5: Completion Review

- [ ] **Step 1: Check git diff**

Run:

```powershell
git -c safe.directory='D:/user/WebstormProjects/taiwan_examination_web' -C 'D:\user\WebstormProjects\taiwan_examination_web' status --short
```

- [ ] **Step 2: Report verification evidence**

Summarize exact commands run, crawl output, updated counts, and any blocked checks.
