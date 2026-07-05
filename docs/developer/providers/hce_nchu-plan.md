# NCHU HCE Source-Proof Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether `hce_nchu` can be implemented from an official National Chung Hsing University source.

**Status:** Source-gated; rechecked 2026-07-05. The official NCHU admissions and department pages expose forms, schedules, and an answer-dispute notice, but no official public full-paper archive was found in the checked source path. No provider code is wired.

**Architecture:** Source-proof first, then add one provider only if public direct downloads exist.

**Tech Stack:** Documentation gate, then Python provider pipeline if accepted.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/hce_nchu-spec.md`

- [x] Find the official National Chung Hsing University admission-system and department pages.
- [x] Check direct downloads for at least one of: 化學, 普通生物及生化概論, 物理, 英文.
- [x] Record source-gate failure in the spec because no public paper archive was found.
- [x] Stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/hce_nchu/client.py`
- Create: `app/providers/hce_nchu/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_hce_nchu.py`
- Create: `.github/workflows/sync-hce-nchu.yml`

- [ ] Write parser tests with one accepted year and one subject.
- [ ] Emit source IDs in the form `hce_nchu:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `hce_nchu` and canonical bundle `hce-nchu`.
- [ ] Run `uv run pytest tests/test_hce_nchu.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
