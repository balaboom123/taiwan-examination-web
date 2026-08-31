# CEEC AST Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `ceec_ast` coverage for the CEEC 分科測驗 general-paper archive.

**Architecture:** Reuse the existing `ceec_gsat` provider shape with AST-specific constants, row parsing, and canonical mapping. Keep one canonical bundle, `ceec-ast`.

**Tech Stack:** Python provider pipeline, stdlib HTML parsing helpers already used by CEEC provider code, existing site publication pipeline, frontend classification mapping.

---

### Task 1: Parser and Provider

**Files:**

- Create: `app/providers/ceec_ast/client.py`
- Create: `app/providers/ceec_ast/provider.py`
- Test: `tests/test_ceec_ast.py`

- [ ] Write parser tests using a fixture row with year `114`, subject `數學甲`, and asset labels `試題內容`, `答題卷`, `選擇(填)題答案`, `非選擇題評分原則`.
- [ ] Implement static page parsing for `https://www.ceec.edu.tw/xmfile?xsmsid=0J052427633128416650`.
- [ ] Emit stable source IDs in the form `ceec_ast:<gregorian_year>:<subject_slug>:<asset_kind>`.
- [ ] Run `uv run pytest tests/test_ceec_ast.py -q`.

### Task 2: Registry and Site Integration

**Files:**

- Modify: `app/providers/registry.py`
- Modify: `app/site_registry.py`
- Modify: `app/normalizer.py`
- Modify: `frontend/src/lib/exam-classification.ts`
- Create: `.github/workflows/sync-ceec-ast.yml`

- [ ] Register provider ID `ceec_ast`.
- [ ] Add canonical bundle mapping `ceec-ast` with display name `分科測驗`.
- [ ] Add default-site support and frontend classification under admission exams.
- [ ] Add a provider-only sync workflow.
- [ ] Run `uv run pytest tests/test_ceec_ast.py tests/test_site_registry.py -q`.
- [ ] Run `npm.cmd --prefix frontend test`.
