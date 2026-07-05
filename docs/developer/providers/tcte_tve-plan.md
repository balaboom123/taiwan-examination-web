# TCTE TVE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `tcte_tve` coverage for the TCTE 四技二專統一入學測驗 paper archive.

**Architecture:** Parse the TCTE yearly listing, follow each `web1.tcte.edu.tw/EXAM/<roc_year>_4y/` page, and publish one canonical bundle, `tcte-tve`.

**Tech Stack:** Python provider pipeline, stdlib URL/HTML handling, existing normalizer and site registry, frontend classification mapping.

---

### Task 1: Parser and Provider

**Files:**

- Create: `app/providers/tcte_tve/client.py`
- Create: `app/providers/tcte_tve/provider.py`
- Test: `tests/test_tcte_tve.py`

- [ ] Write parser tests with one listing row for ROC year `115` and one yearly page containing `共同科目 國文科` plus one professional group row.
- [ ] Parse `https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y`.
- [ ] Parse yearly pages such as `https://web1.tcte.edu.tw/EXAM/115_4y/`.
- [ ] Emit stable source IDs in the form `tcte_tve:<gregorian_year>:<group_slug>:<subject_slug>:<asset_kind>`.
- [ ] Run `uv run pytest tests/test_tcte_tve.py -q`.

### Task 2: Registry and Site Integration

**Files:**

- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `.github/workflows/sync-tcte-tve.yml`

- [ ] Register provider ID `tcte_tve`.
- [ ] Add canonical bundle mapping `tcte-tve` with display name `四技二專統一入學測驗`.
- [ ] Add default-site support and frontend classification under admission exams.
- [ ] Add a provider-only sync workflow.
- [ ] Run `uv run pytest tests/test_tcte_tve.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
