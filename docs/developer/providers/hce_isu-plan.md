# ISU HCE Source-Proof Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether `hce_isu` can be implemented from an official I-Shou University source.

**Status:** Source-gated; rechecked 2026-07-05. The official ISU admissions portal exposes `學士後中醫學系` as an item, but no official public full-paper archive or direct paper/answer downloads were found in the checked source path. No provider code is wired.

**Architecture:** Source-proof first, then add one provider only if public direct downloads exist.

**Tech Stack:** Documentation gate, then Python provider pipeline if accepted.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/hce_isu-spec.md`

- [x] Find the official I-Shou University admission-system page.
- [x] Check direct downloads for at least one of: 化學, 國文, 生物學, 英文.
- [x] Record source-gate failure in the spec because no public paper downloads were found.
- [x] Stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/hce_isu/client.py`
- Create: `app/providers/hce_isu/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_hce_isu.py`
- Create: `.github/workflows/sync-hce-isu.yml`

- [ ] Write parser tests with one accepted year and one subject.
- [ ] Emit source IDs in the form `hce_isu:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `hce_isu` and canonical bundle `hce-isu`.
- [ ] Run `uv run pytest tests/test_hce_isu.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
