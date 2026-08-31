# Taiwan Exam Provider Coverage Spec

## Summary

- audit date: 2026-07-04
- reference source: `https://www.shuati.tw/exams`
- current site data checked: `data/sites/default/frontend-bundles.json`
- current provider registry checked: `app/providers/registry.py` and `app/site_registry.py`

The site does not support every Taiwan exam bucket listed by Shuati. This file is only the coverage audit and routing index. Source-specific requirements live in separate spec and plan files so provider work does not mix unrelated source rules.

## Current Support

| Shuati bucket | Current support |
|---|---|
| `/exams/cap` | `rcpet_cap`, published as `rcpet-cap` |
| `/exams/gsat` | `ceec_gsat`, published as `ceec-gsat` |
| `/exams/teacher` | `teacher_qual`, published as `teacher-qual` |
| `/exams/law` | `moex` |
| `/exams/medical` | `moex` |
| `/exams/professional_senior` | `moex` |
| `/exams/professional_regular` | `moex` |
| `/exams/civil_senior` | `moex` |
| `/exams/civil_local3` | `moex` |
| `/exams/civil_regular` | `moex` |
| `/exams/civil_local4` | `moex` |
| `/exams/civil_junior` | `moex` |
| `/exams/judicial_judicial_junior` | `moex` |
| `/exams/judicial_judicial_regular` | `moex` |
| `/exams/judicial_judicial_senior` | `moex` |
| `/exams/judicial_investigation_regular` | `moex` |
| `/exams/judicial_investigation_senior` | `moex` |
| `/exams/judicial_immigration_regular` | `moex` |
| `/exams/judicial_immigration_senior` | `moex` |
| `/exams/judicial_immigration_special` | `moex` |
| `/exams/judicial_coastguard_junior` | `moex` |
| `/exams/judicial_coastguard_regular` | `moex` |
| `/exams/judicial_coastguard_senior` | `moex` |
| `/exams/police_4th_general` | `moex` |
| `/exams/cpc_recruit` | `cpc_recruit`, published as `cpc-recruit` |
| `/exams/moea_joint` | `moea_recruit`, published as `moea-recruit` |
| `/exams/taipower_recruit` | `taipower_recruit`, published as `taipower-recruit` |

## Unsupported Source Routing

| Priority | Shuati bucket | Subjects | Source spec | Source plan |
|---|---:|---:|---|---|
| P1 | `/exams/ast` | 18 | `docs/developer/providers/ceec_ast-spec.md` | `docs/developer/providers/ceec_ast-plan.md` |
| P1 | `/exams/tve` | 41 | `docs/developer/providers/tcte_tve-spec.md` | `docs/developer/providers/tcte_tve-plan.md` |
| P2 | `/exams/post_recruit` | 8 | `docs/developer/providers/post_recruit-spec.md` | `docs/developer/providers/post_recruit-plan.md` |
| P2 | `/exams/special` | 9 | `docs/developer/providers/special_admission-spec.md` | `docs/developer/providers/special_admission-plan.md` |
| P3 | `/exams/hce_cmu` | 4 | `docs/developer/providers/hce_cmu-spec.md` | `docs/developer/providers/hce_cmu-plan.md` |
| P3 | `/exams/hce_isu` | 4 | `docs/developer/providers/hce_isu-spec.md` | `docs/developer/providers/hce_isu-plan.md` |
| P3 | `/exams/hce_kmu` | 5 | `docs/developer/providers/hce_kmu-spec.md` | `docs/developer/providers/hce_kmu-plan.md` |
| P3 | `/exams/hce_tcu` | 4 | `docs/developer/providers/hce_tcu-spec.md` | `docs/developer/providers/hce_tcu-plan.md` |
| P3 | `/exams/hce_nchu` | 4 | `docs/developer/providers/hce_nchu-spec.md` | `docs/developer/providers/hce_nchu-plan.md` |
| P3 | `/exams/hce_nsysu` | 4 | `docs/developer/providers/hce_nsysu-spec.md` | `docs/developer/providers/hce_nsysu-plan.md` |
| P3 | `/exams/hce_nthu` | 5 | `docs/developer/providers/hce_nthu-spec.md` | `docs/developer/providers/hce_nthu-plan.md` |

## Implementation Results

| Shuati bucket | Provider decision | Public bundle |
|---|---|---|
| `/exams/ast` | implemented from CEEC official archive | `ceec-ast` |
| `/exams/tve` | implemented from TCTE official archive | `tcte-tve` |
| `/exams/post_recruit` | implemented from Chunghwa Post/TABF official archive | `post-recruit` |
| `/exams/special` | implemented from NCU-hosted official archive | `special-admission` |
| `/exams/hce_cmu` | implemented from CMU official archive | `hce-cmu` |
| `/exams/hce_tcu` | implemented from TCU official archive | `hce-tcu` |
| `/exams/hce_nsysu` | implemented from NSYSU official library archive | `hce-nsysu` |
| `/exams/hce_nthu` | implemented from NTHU official admissions archive | `hce-nthu` |
| `/exams/hce_isu` | source-gated; no official public full-paper downloads found | n/a |
| `/exams/hce_kmu` | source-gated; no official public full-paper downloads found | n/a |
| `/exams/hce_nchu` | source-gated; no official public full-paper archive found | n/a |

## Non-Targets

| Shuati bucket | Subjects | Decision |
|---|---:|---|
| `/exams/reading` | 1 | Deferred until it maps to a named official Taiwan exam with public direct downloads. |
| `/exams/_sessions_by_year` | 0 | Skipped because Shuati reports zero subjects and the slug is not a user-facing exam. |

## Product Rule

Do not crawl Shuati as a source. Shuati is a coverage reference only. Providers must use official, public, downloadable, repeatable sources. Browser-only practice pages, login-gated downloads, schedule pages, and third-party mirrors stay out of the bundle pipeline.
