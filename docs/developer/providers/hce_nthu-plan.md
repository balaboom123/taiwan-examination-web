# NTHU HCE Source-Proof Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether `hce_nthu` can be implemented from an official National Tsing Hua University source.

**Status:** Implemented from the official NTHU admissions archive. Current local sync: ROC 115 / AD 2026, 4 files, 0 failures. Public bundle: `hce-nthu`.

**Architecture:** Source-proof first, then add one provider only if public direct downloads exist.

**Tech Stack:** Documentation gate, then Python provider pipeline if accepted.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/hce_nthu-spec.md`

- [ ] Find the official National Tsing Hua University archive or admission-system page.
- [ ] Confirm direct downloads for at least one of: 化學與物理, 生物與生化, 英文, 資訊科學, 進階物理與線性代數.
- [ ] Add accepted source URL, year coverage, file types, and title rules to the spec.
- [ ] If the source fails this gate, record the rejection reason in the spec and stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/hce_nthu/client.py`
- Create: `app/providers/hce_nthu/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_hce_nthu.py`
- Create: `.github/workflows/sync-hce-nthu.yml`

- [ ] Write parser tests with one accepted year and one subject.
- [ ] Emit source IDs in the form `hce_nthu:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `hce_nthu` and canonical bundle `hce-nthu`.
- [ ] Run `uv run pytest tests/test_hce_nthu.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
