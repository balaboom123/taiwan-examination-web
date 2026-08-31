# TCU HCE Source-Proof Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether `hce_tcu` can be implemented from an official Tzu Chi University source.

**Status:** Implemented from the official TCU admission archive. Current local sync: ROC 115 / AD 2026, 8 files, 0 failures. Public bundle: `hce-tcu`.

**Architecture:** Source-proof first, then add one provider only if public direct downloads exist.

**Tech Stack:** Documentation gate, then Python provider pipeline if accepted.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/hce_tcu-spec.md`

- [ ] Find the official Tzu Chi University archive or admission-system page.
- [ ] Confirm direct downloads for at least one of: 化學, 國文, 生物學, 英文.
- [ ] Add accepted source URL, year coverage, file types, and title rules to the spec.
- [ ] If the source fails this gate, record the rejection reason in the spec and stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/hce_tcu/client.py`
- Create: `app/providers/hce_tcu/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_hce_tcu.py`
- Create: `.github/workflows/sync-hce-tcu.yml`

- [ ] Write parser tests with one accepted year and one subject.
- [ ] Emit source IDs in the form `hce_tcu:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `hce_tcu` and canonical bundle `hce-tcu`.
- [ ] Run `uv run pytest tests/test_hce_tcu.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
