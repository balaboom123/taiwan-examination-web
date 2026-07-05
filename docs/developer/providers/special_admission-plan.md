# Special Admission Source-Proof Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether `/exams/special` can become `special_admission`, then implement it only if an official downloadable archive exists.

**Architecture:** Treat this as a source-proof gate first. Provider work starts only after the exact organizer, archive URL, and downloadable file pattern are recorded in the spec.

**Tech Stack:** Documentation gate, then Python provider pipeline only if accepted.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/special_admission-spec.md`

- [ ] Map Shuati `/exams/special` to the official exam name and organizer.
- [ ] Confirm whether official pages expose direct public downloads for the listed subjects.
- [ ] Add accepted source URL, year coverage, file types, and title rules to the spec.
- [ ] If no stable official archive exists, record the rejection reason in the spec and stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/special_admission/client.py`
- Create: `app/providers/special_admission/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_special_admission.py`
- Create: `.github/workflows/sync-special-admission.yml`

- [ ] Write parser tests with one accepted year and one subject.
- [ ] Emit stable source IDs in the form `special_admission:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `special_admission`.
- [ ] Add canonical bundle mapping `special-admission`.
- [ ] Add default-site support and frontend classification under admission exams.
- [ ] Run `uv run pytest tests/test_special_admission.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
