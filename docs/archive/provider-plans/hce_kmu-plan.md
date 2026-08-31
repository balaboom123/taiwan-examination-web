# KMU HCE Source-Proof Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether `hce_kmu` can be implemented from an official Kaohsiung Medical University source.

**Status:** Source-gated; rechecked 2026-07-05. The official KMU admissions system exposes the current `學士後醫學系` admissions brief and schedule, but no official public full-paper archive or direct paper/answer downloads were found in the checked source path. No provider code is wired.

**Architecture:** Source-proof first, then add one provider only if public direct downloads exist.

**Tech Stack:** Documentation gate, then Python provider pipeline if accepted.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/hce_kmu-spec.md`

- [x] Find the official Kaohsiung Medical University admission-system page.
- [x] Check direct downloads for at least one of: 普通生物及生化概論, 有機化學, 物理及化學, 英文, 計算機概論與程式設計.
- [x] Record source-gate failure in the spec because no public paper downloads were found.
- [x] Stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/hce_kmu/client.py`
- Create: `app/providers/hce_kmu/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_hce_kmu.py`
- Create: `.github/workflows/sync-hce-kmu.yml`

- [ ] Write parser tests with one accepted year and one subject.
- [ ] Emit source IDs in the form `hce_kmu:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `hce_kmu` and canonical bundle `hce-kmu`.
- [ ] Run `uv run pytest tests/test_hce_kmu.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
