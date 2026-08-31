# Chunghwa Post Recruitment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `post_recruit` only if Chunghwa Post or its named commissioned host exposes public direct-download written-paper assets.

**Architecture:** Source-proof before code. If accepted, build one small provider that mirrors first-test paper assets into one canonical bundle, `post-recruit`.

**Tech Stack:** Python provider pipeline, existing normalizer and site registry, frontend classification mapping.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/post_recruit-spec.md`

- [ ] Find the official recruitment-year page from Chunghwa Post or the named commissioned host.
- [ ] Confirm at least one written-paper file downloads without login, CAPTCHA, or browser-only state.
- [ ] Add the accepted source URL, year coverage, file types, and title rules to the spec.
- [ ] If the source fails this gate, record the rejection reason in the spec and stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/post_recruit/client.py`
- Create: `app/providers/post_recruit/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_post_recruit.py`
- Create: `.github/workflows/sync-post-recruit.yml`

- [ ] Write parser tests with one recruitment year, one level, and one written subject.
- [ ] Emit stable source IDs in the form `post_recruit:<gregorian_year>:<level_slug>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `post_recruit`.
- [ ] Add canonical bundle mapping `post-recruit`.
- [ ] Add default-site support and frontend classification under recruitment exams.
- [ ] Run `uv run pytest tests/test_post_recruit.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
