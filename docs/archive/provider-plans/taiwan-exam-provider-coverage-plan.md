# Taiwan Exam Provider Coverage Routing Plan

## Goal

Keep the Taiwan exam coverage audit separate from provider implementation work. Each unsupported source has its own spec and plan file.

## Execution Order

1. Implement `ceec_ast` from the CEEC 分科測驗 source.
2. Implement `tcte_tve` from the TCTE 四技二專統一入學測驗 source.
3. Source-proof and implement `post_recruit` only if Chunghwa Post or its commissioned host exposes public direct downloads.
4. Source-proof `special_admission`; implement only if the official archive is stable and downloadable.
5. Source-proof each HCE school independently; implement only the schools with official public direct downloads.
6. Keep `/exams/reading` and `/exams/_sessions_by_year` out of provider work until their non-target decisions change.

## Current Status

- Implemented and published: `ceec_ast`, `tcte_tve`, `post_recruit`, `special_admission`, `hce_cmu`, `hce_tcu`, `hce_nsysu`, `hce_nthu`.
- Source-gated after official-source checks: `hce_isu`, `hce_kmu`, `hce_nchu`.
- Still non-targets: `/exams/reading`, `/exams/_sessions_by_year`.

## Source Plans

| Source | Plan |
|---|---|
| CEEC 分科測驗 | `docs/developer/providers/ceec_ast-plan.md` |
| TCTE 四技二專統一入學測驗 | `docs/developer/providers/tcte_tve-plan.md` |
| Chunghwa Post recruitment | `docs/developer/providers/post_recruit-plan.md` |
| Special admission | `docs/developer/providers/special_admission-plan.md` |
| China Medical University HCE | `docs/developer/providers/hce_cmu-plan.md` |
| I-Shou University HCE | `docs/developer/providers/hce_isu-plan.md` |
| Kaohsiung Medical University HCE | `docs/developer/providers/hce_kmu-plan.md` |
| Tzu Chi University HCE | `docs/developer/providers/hce_tcu-plan.md` |
| National Chung Hsing University HCE | `docs/developer/providers/hce_nchu-plan.md` |
| National Sun Yat-sen University HCE | `docs/developer/providers/hce_nsysu-plan.md` |
| National Tsing Hua University HCE | `docs/developer/providers/hce_nthu-plan.md` |

## Shared Verification

Run the source plan's focused provider tests first. After a provider is integrated, run:

```bash
uv run pytest -q
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
```

After each site publish, inspect `data/sites/default/frontend-bundles.json` and confirm the expected canonical bundle exists.
