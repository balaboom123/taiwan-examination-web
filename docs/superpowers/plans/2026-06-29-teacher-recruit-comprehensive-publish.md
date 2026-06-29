# Teacher Recruit Comprehensive Publish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish every currently approved official 教甄 source from the teacher-exam spec on the default public site.

**Architecture:** Reuse the existing provider/client pattern. Each source gets a small parser, emits `SourceExamPage`, and feeds the existing sync, mirror, normalizer, bundle, release, and GitHub Pages pipeline.

**Tech Stack:** Python stdlib `html.parser`, `json`, `urllib.request`, `urllib.parse`; existing `SourceProvider`; unittest/pytest; GitHub Actions workflow YAML; existing `publish-site` and release upload scripts.

---

### Task 1: New Taipei Provider

**Files:**
- Create: `app/providers/teacher_recruit_newtaipei/client.py`
- Create: `app/providers/teacher_recruit_newtaipei/provider.py`
- Create: `app/providers/teacher_recruit_newtaipei/__init__.py`
- Test: `tests/test_teacher_recruit_newtaipei.py`

- [ ] **Step 1: Write parser tests**

Cover `parse_candidate_notices()`, `detail_matches_notice()`, `parse_detail_downloads()`, and tokenized `download_file()`. The fixture must include one kept notice, one skipped 疑義 notice, one matching detail with `attachment2`, and one token endpoint returning `[{"token": "download-token"}]`.

- [ ] **Step 2: Verify red**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_recruit_newtaipei.py -q`

Expected: import failure for missing provider module.

- [ ] **Step 3: Implement client and wrapper**

Use the official list API:

```text
https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/temopn_newtea_list
```

Use detail and token APIs:

```text
https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/temopn_edu/uuid/<uuid>
https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/download/<fileUuid>
https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/d/<token>
```

Keep paper notices containing `試題`, `題目`, or `答案`; skip `疑義`, `成績`, `錄取`, `試場`, `分配`, `報名`, and `查詢`. Validate detail title/tag against the list row before accepting attachments.

- [ ] **Step 4: Verify green**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_recruit_newtaipei.py -q`

Expected: all tests pass.

### Task 2: Taoyuan Elementary Provider

**Files:**
- Create: `app/providers/teacher_recruit_taoyuan_elementary/client.py`
- Create: `app/providers/teacher_recruit_taoyuan_elementary/provider.py`
- Create: `app/providers/teacher_recruit_taoyuan_elementary/__init__.py`
- Test: `tests/test_teacher_recruit_taoyuan_elementary.py`

- [ ] **Step 1: Write parser tests**

Cover `parse_answer_page()` with question, suggested-answer, final-answer, and skipped 疑義 links from:

```text
https://elementary.tyc.edu.tw/web/answer.aspx?openExternalBrowser=1
```

- [ ] **Step 2: Verify red**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_recruit_taoyuan_elementary.py -q`

Expected: import failure for missing provider module.

- [ ] **Step 3: Implement client and wrapper**

Group files by subject label. Classify `試題` as `question`, `建議答案` as `answer`, and `正確答案` as `corrected_answer`; skip 疑義/釋疑 material.

- [ ] **Step 4: Verify green**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_recruit_taoyuan_elementary.py -q`

Expected: all tests pass.

### Task 3: Kaohsiung Provider

**Files:**
- Create: `app/providers/teacher_recruit_kaohsiung/client.py`
- Create: `app/providers/teacher_recruit_kaohsiung/provider.py`
- Create: `app/providers/teacher_recruit_kaohsiung/__init__.py`
- Test: `tests/test_teacher_recruit_kaohsiung.py`

- [ ] **Step 1: Write parser tests**

Cover regular elementary ZIP links from `teaexam` and special-education PDF links from `special`.

- [ ] **Step 2: Verify red**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_recruit_kaohsiung.py -q`

Expected: import failure for missing provider module.

- [ ] **Step 3: Implement client and wrapper**

Use:

```text
https://exam.kh.edu.tw/teaexam/index.jsp?cnt=board/board.jsp&now_page=2
https://exam.kh.edu.tw/special/index.jsp
```

Keep `試題.zip`, `答案.zip`, `正確答案.zip`, and special-ed filenames containing `試題教育局`, `參考答案教育局`, or `正確答案-`. Skip duplicate URL-encoded copies, lists, venues, vacancies, brochures, and teaching-demo topics.

- [ ] **Step 4: Verify green**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_recruit_kaohsiung.py -q`

Expected: all tests pass.

### Task 4: Central Alliance Provider

**Files:**
- Create: `app/providers/teacher_recruit_central_alliance/client.py`
- Create: `app/providers/teacher_recruit_central_alliance/provider.py`
- Create: `app/providers/teacher_recruit_central_alliance/__init__.py`
- Test: `tests/test_teacher_recruit_central_alliance.py`

- [ ] **Step 1: Write parser tests**

Cover `type=question`, `type=referenceanswer`, and `type=finalanswer` links for A/B/C level pages from:

```text
https://qa115-tse-cl.twrecruit.com.tw/Subject/news.php
https://qa115-tse-cl.twrecruit.com.tw/Ans2/news.php
```

- [ ] **Step 2: Verify red**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_recruit_central_alliance.py -q`

Expected: import failure for missing provider module.

- [ ] **Step 3: Implement client and wrapper**

Implement A/B/C only: 幼兒園, 國小, 國中. Group by subject name parsed from filenames after stripping `115中策_`, `_試題`, `試題`, and `答案.pdf`.

- [ ] **Step 4: Verify green**

Run: `.venv\Scripts\python.exe -m pytest tests/test_teacher_recruit_central_alliance.py -q`

Expected: all tests pass.

### Task 5: Registry, Normalization, Workflows

**Files:**
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `app/models.py`
- Modify: `app/sync.py`
- Modify: `tests/test_site_registry.py`
- Modify: `tests/test_normalizer.py`
- Modify: `tests/test_workflows.py`
- Create: `.github/workflows/sync-teacher-recruit-newtaipei.yml`
- Create: `.github/workflows/sync-teacher-recruit-taoyuan-elementary.yml`
- Create: `.github/workflows/sync-teacher-recruit-kaohsiung.yml`
- Create: `.github/workflows/sync-teacher-recruit-central-alliance.yml`

- [ ] **Step 1: Write failing registry tests**

Add provider IDs and canonical prefixes:

```text
teacher_recruit_newtaipei -> teacher-recruit-newtaipei / 新北市教師甄試
teacher_recruit_taoyuan_elementary -> teacher-recruit-taoyuan-elementary / 桃園市國小教師甄試
teacher_recruit_kaohsiung -> teacher-recruit-kaohsiung / 高雄市教師甄試
teacher_recruit_central_alliance -> teacher-recruit-central-alliance / 中區策略聯盟教師甄試
```

Add `question_answer` support for combined official files.

- [ ] **Step 2: Verify red**

Run: `.venv\Scripts\python.exe -m pytest tests/test_site_registry.py tests/test_normalizer.py tests/test_workflows.py -q`

Expected: failures for missing registry entries and workflows.

- [ ] **Step 3: Register and add workflows**

Add the four providers to registry/default site/normalizer. Set public minimum years to 1 for each `teacher-recruit-*` prefix. Add weekly schedules staggered after the existing Tuesday teacher workflows.

- [ ] **Step 4: Verify green**

Run: `.venv\Scripts\python.exe -m pytest tests/test_site_registry.py tests/test_normalizer.py tests/test_workflows.py -q`

Expected: all tests pass.

### Task 6: Sync, Publish, And Public Verification

**Files:**
- Generated: `data/providers/teacher_recruit_newtaipei/**`
- Generated: `data/providers/teacher_recruit_taoyuan_elementary/**`
- Generated: `data/providers/teacher_recruit_kaohsiung/**`
- Generated: `data/providers/teacher_recruit_central_alliance/**`
- Generated: `data/sites/default/**`
- Generated: `bundles/sites/default/*.zip`
- Generated/release: GitHub release assets for new or changed bundles

- [ ] **Step 1: Run provider syncs**

Run:

```powershell
.venv\Scripts\python.exe -m app sync-full --provider teacher_recruit_newtaipei --site-id default
.venv\Scripts\python.exe -m app sync-full --provider teacher_recruit_taoyuan_elementary --site-id default
.venv\Scripts\python.exe -m app sync-full --provider teacher_recruit_kaohsiung --site-id default
.venv\Scripts\python.exe -m app sync-full --provider teacher_recruit_central_alliance --site-id default
```

- [ ] **Step 2: Publish site metadata**

Run:

```powershell
.venv\Scripts\python.exe -m app publish-site --site-id default --repository balaboom123/taiwan-examination-web
```

Expected: default-site metadata includes the four new canonical teacher-recruit bundles.

- [ ] **Step 3: Run verification**

Run backend tests, frontend data tests, frontend build, and `git diff --check`.

- [ ] **Step 4: Commit and publish**

Commit code, docs, generated data, and site metadata. Upload missing release ZIPs, push to GitHub, wait for Pages deploy, then verify `https://balaboom123.github.io/taiwan-examination-web/data/sites/default/frontend-bundles.json` contains the new teacher bundles.
