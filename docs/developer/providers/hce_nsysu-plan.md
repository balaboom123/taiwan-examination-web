# NSYSU HCE Source-Proof Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether `hce_nsysu` can be implemented from an official National Sun Yat-sen University source.

**Status:** Implemented from the official NSYSU library archive. Current local sync: ROC 115 / AD 2026, 1 combined PDF, 0 failures. Public bundle: `hce-nsysu`.

**Architecture:** Source-proof first, then add one provider only if public direct downloads exist.

**Tech Stack:** Documentation gate, then Python provider pipeline if accepted.

---

### Task 1: Source Proof

**Files:**

- Modify: `docs/developer/providers/hce_nsysu-spec.md`

- [ ] Find the official National Sun Yat-sen University archive or admission-system page.
- [ ] Confirm direct downloads for at least one of: 普通生物及生化概論, 物理與化學, 英文, 計算機概論與程式設計.
- [ ] Add accepted source URL, year coverage, file types, and title rules to the spec.
- [ ] If the source fails this gate, record the rejection reason in the spec and stop before code.

### Task 2: Provider and Integration

**Files:**

- Create: `app/providers/hce_nsysu/client.py`
- Create: `app/providers/hce_nsysu/provider.py`
- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `tests/test_hce_nsysu.py`
- Create: `.github/workflows/sync-hce-nsysu.yml`

- [ ] Write parser tests with one accepted year and one subject.
- [ ] Emit source IDs in the form `hce_nsysu:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Register provider ID `hce_nsysu` and canonical bundle `hce-nsysu`.
- [ ] Run `uv run pytest tests/test_hce_nsysu.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
