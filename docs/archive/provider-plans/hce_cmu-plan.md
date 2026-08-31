# CMU HCE Source-Proof Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether `hce_cmu` can be implemented from an official China Medical University source.

**Status:** Implemented from the official CMU admission archive. Current local sync: ROC 115 / AD 2026, 8 files, 0 failures. Public bundle: `hce-cmu`.

**Architecture:** Source-proof first, then add one provider only if public direct downloads exist.

**Tech Stack:** Documentation gate, then Python provider pipeline if accepted.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/hce_cmu-spec.md`

- [ ] Find the official China Medical University archive or admission-system page.
- [ ] Confirm direct downloads for at least one of: 化學, 國文, 生物學, 英文.
- [ ] Add accepted source URL, year coverage, file types, and title rules to the spec.
- [ ] If the source fails this gate, record the rejection reason in the spec and stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/hce_cmu/client.py`
- Create: `app/providers/hce_cmu/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_hce_cmu.py`
- Create: `.github/workflows/sync-hce-cmu.yml`

- [ ] Write parser tests with one accepted year and one subject.
- [ ] Emit source IDs in the form `hce_cmu:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `hce_cmu` and canonical bundle `hce-cmu`.
- [ ] Run `uv run pytest tests/test_hce_cmu.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
