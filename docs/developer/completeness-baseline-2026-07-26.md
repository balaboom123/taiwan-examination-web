# Completeness Baseline — 2026-07-28

This report records the baseline and bounded corrective cycles, including the MOEX source/identity reconciliation and the targeted WDASEC 2008–2024 historical refreshes. Baseline inspection was read-only; the cycles regenerated only targeted provider/site state, added validation/deployment gates, and fixed one v2 targeted-publication keying defect, and reconciled generated review state. No provider-source data was fabricated, no public upload/deploy was performed, and no history was rewritten.

## Executive result

The repository has a working provider-to-frontend pipeline, but the archive is not complete under the requested definition. The current snapshot has:

- 35 registered providers and 192,407 normalized paper records.
- 3,244 physical site/release bundle assets, represented as 3,241 logical frontend rows, across 11 release shards after the scoped WDASEC 2008–2024 and MOEX worker-promotion refreshes.
- 0 current sync-failure records, but 631 current MOEX review-queue entries and 4,283 review-confidence records isolated by event.
- 0 event-level download gaps, 50 normalization gaps, 8 normalized-but-not-published events, and 327 explicit publication-policy exclusions after the HCE, MOEX historical, MOEX worker-promotion, New Taipei, TCTE, and WDASEC 2008–2024 targeted repairs. The policy-aware provider-to-site check finds 3,241 expected and 3,241 actual logical site IDs, with zero missing or extra IDs.
- only one checked-in source manifest: `data/providers/moex/source-manifest.json`.
- no complete live source probe: the serial probe was stopped after it blocked at the CEEC GSAT discovery request; bounded probes now provide provider-specific evidence for selected gaps.

The current source state and the current public projection are therefore different completeness questions. MOEX 2025 and 2026 data are present locally; the remaining 2025-2026 groups absent from the site are 35 and 13 one-year groups containing 339 and 105 records, respectively, under the documented two-year public-bundle policy. Separate normalization gaps remain. Generated-manifest agreement alone is not evidence that every official source item is public or that the source itself has been exhaustively discovered.

The practical definition of complete for this project is:

> Every discoverable official public source inside the documented scope is either covered, explicitly blocked with reproducible evidence, or intentionally excluded with a reason. “Unknown” is not a completion state.

## Authority and method

The evidence hierarchy used here is:

1. Executable provider and site registries, schemas, and pipeline behavior in `app/`, `catalog/`, and `schemas/`.
2. Provider specifications and source indexes in `docs/developer/providers/`.
3. Current provider state, mirrors, bundles, and site feeds as generated operational state.
4. Git history for historical failure/review snapshots.

The year ranges in the matrix are repository-documented or repository-observed ranges. They are not presented as a fresh assertion that each external site is unchanged today because the live probe was not completed. A source row marked “covered” means covered in the declared repository scope, not a claim that the provider’s entire historical universe is complete.

Official/public access is not the same as a redistribution license. The repository documentation does not establish a blanket license for source PDFs, ZIPs, audio, or answer keys. Source-specific copyright, takedown, rate-limit, and redistribution review remains required before a release is treated as legally safe.

## End-to-end data flow

| Stage | Current implementation and evidence | Completeness risk |
| --- | --- | --- |
| Official source discovery | app/providers/base.py defines discovery, page fetch, HEAD, and download contracts. Provider clients implement source-specific HTML/API/WebForms parsing. MOEX has a versioned source manifest; the other 34 providers do not. | Without a manifest or equivalent discovery evidence for every provider, missing years and newly published files cannot be distinguished from intentional scope. |
| Probe and change detection | `app/probe.py` and `app/history_audit.py` compare source events and local state. `history-audit --probe-sources` can call live discovery. | The live run was stopped at `ceec_gsat` after a 60-second URL-opening wait; there is no complete current external-source inventory. |
| Mirroring | `app/sync.py` validates file signatures, records checksums, reuses valid files, and writes provider-scoped mirrors. `app/storage.py` uses SHA-256 and a dedupe index. | The mirror is about 52 GB and is ignored operational state. Current failure queues are empty, but historical failure provenance must be retained separately. |
| Normalization and identity | app/normalizer.py emits NormalizedPaper records and review candidates. app/classification.py derives exam identity v2 dimensions and isolates unresolved evidence by event. | 4,283 records still have review confidence; 50 events have normalization gaps. A passing review-isolation audit means records are safely separated, not semantically resolved. |
| Bundling | `app/bundler.py` groups by v2 bundle ID, preserves legacy entries, validates mirror inputs, splits oversized archives, and applies site year policy. | The current default site is deliberately multi-year for most bundles. Provider state can contain valid single-year or unprojected bundles that are not public. |
| Site publication and release projection | app/publisher.py aggregates the 35 providers, filters by site policy, assigns v2 release tags, and writes data/sites/default/. app/bundler.py and scripts/validate_publication.py share the public-year eligibility rule. Targeted state selection now uses bundle_id for v2 records and canonical_id only for legacy records; a regression covers shared legacy IDs across independent v2 groups. | The current snapshot has zero provider-derived logical IDs missing from or extra in the site inventory, but event-level history gaps remain. Local release planning does not verify that remote GitHub release assets actually exist. |
| Frontend display | `frontend/src/` consumes `frontend-bundles.json`; `frontend/build/` contains generated-feed and pure-logic tests. `App.tsx` supplies search, filters, sorting, pagination, and download rows. | There are no source-level component tests, browser tests, accessibility tests, or end-to-end tests. |
| CI and deployment | .github/workflows/ci.yml runs Python tests, strict catalog/history audits, publication/release checks, and frontend test/lint/build. GitHub Pages is canonical production; Netlify is preview-only. deploy-pages.yml repeats those data gates and frontend test/lint before upload. | Provider-specific refresh workflows still do not all run aggregate publication gates, and the strict history gate correctly blocks deployment on unresolved event gaps. |

## Git and worktree baseline

Remote information was fetched with `git fetch --all --prune`; local work was not reset, rebased, overwritten, published, or deployed.

| Item | Baseline |
| --- | --- |
| Current branch | `agent/exam-coverage-and-mirror-dedup` |
| Report-capture HEAD before the MOEX worker-promotion cycle | `483c685` (`docs: clarify baseline snapshot timing`) |
| WDASEC 2024 cycle start | `4176b97` (`reconcile generated review state and audit gate`) |
| Divergence at report capture vs latest fetched main | `6 behind / 23 ahead` (`origin/main...HEAD`) |
| Divergence at report capture vs tracked upstream | `0 behind / 18 ahead` (`@{upstream}...HEAD`) |
| Uncommitted tracked files at report capture | None |
| Untracked files at report capture | `PLAN.md` only (about 40 KB); it remains intentionally preserved and excluded from commits |
| Large untracked files | None; the 52 GB mirror and 57 GB bundles are ignored operational state, not untracked Git files |
| Audit starting HEAD | `1bf01863013dffbfc89b5b7d4b49702d38dbec7e` (`fix: repair workflow YAML command scalars`) |
| Tracked upstream at audit start | `origin/agent/exam-coverage-and-mirror-dedup`; divergence `0 ahead / 0 behind` |
| Latest fetched main | `origin/main` / `origin/HEAD` at `d3af20f` (`chore: refresh CEEC AST provider data`, 2026-07-25) |
| Current branch vs latest main at audit start | `5 ahead / 6 behind` |
| Unique current-branch commits at report capture | 21 relative to latest `origin/main`; 16 relative to tracked upstream; see `git log` for the reviewable list |
| Unique latest-main commits | `d3af20f`, `4168bea`, `59ed533`, `b197b3f`, `306f10c`, `de3f461` |
| Corrective-cycle change set | CI/workflow gates, app bundling/publication/history/state logic, MOEX/TCTE/teacher/provider state, generated indexes, review-state reconciliation, focused tests, and completeness/operator reports; intentionally not published remotely |
| Untracked files at audit baseline | `PLAN.md` only; it remains intentionally preserved and excluded from the corrective-cycle commit |
| Large ignored operational state | data/ about 374 MB; mirror/ about 52 GB; bundles/ about 57 GB |

At audit start the branch had no unpushed commits relative to its own upstream but was five commits ahead and six behind the fetched latest main. The current checkpoint remains local and reviewable; the final handoff reports live divergence because each documentation commit changes the count. Do not merge, rebase, reset, or cherry-pick until the divergence has been reviewed.

### Post-baseline bounded source/release investigation

- A read-only WDASEC adapter fetch of official session 202411040001 returned 207 paper rows. The normal pipeline then refreshed all six 2024 sessions into current provider state: 453 normalized papers, 422 valid mirrored payloads, zero failures, and approximately 400 MB. Scoped local publication added the eligible multi-year groups to the default site. Follow-up official probes found five 2008 sessions with 342 paper URLs, six 2009 sessions with 342 paper URLs, six 2011 sessions with 400 paper URLs, seven 2012 sessions with 426 paper URLs, six 2013 sessions with 499 paper URLs, six 2014 sessions with 479 paper URLs, six 2015 sessions with 498 paper URLs, six 2016 sessions with 534 paper URLs, six 2017 sessions with 519 paper URLs, six 2018 sessions with 534 paper URLs, six 2019 sessions with 412 paper URLs, six 2020 sessions with 437 paper URLs, six 2021 sessions with 443 paper URLs, five 2022 sessions with 456 paper URLs, and five 2023 sessions with 447 paper URLs, all with zero discovery/detail errors; the targeted pipeline mirrored and normalized all 6,795 papers across 2008–2023 with zero sync failures. Four of five 2008 events are complete, with one explicitly excluded; all six 2009 events are published complete; three 2011 events are complete, with three explicitly excluded; all 2013–2014 sessions, all 2016–2021 sessions, all five 2022 and 2023 sessions, and all six 2024 sessions are published complete; five 2012 events are complete, with two explicitly excluded, and one 2015 event remains explicitly excluded. The remaining 33 raw WDASEC events through 2007 are normalization gaps and require a separate storage/release decision.
- The WDASEC 2023 refresh changed the aggregate local projection from 3,098 to 3,115 physical assets and from 3,095 to 3,112 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2022 refresh added 456 normalized papers and changed the aggregate local projection from 3,115 to 3,129 physical assets and from 3,112 to 3,126 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2021 refresh added 443 normalized papers and changed the aggregate local projection from 3,129 to 3,137 physical assets and from 3,126 to 3,134 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2020 refresh added 437 normalized papers and changed the aggregate local projection from 3,137 to 3,139 physical assets and from 3,134 to 3,136 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2019 refresh added 412 normalized papers and changed the aggregate local projection from 3,139 to 3,140 physical assets and from 3,136 to 3,137 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2018 refresh added 534 normalized papers and changed no aggregate site count because all affected identities were already in existing multi-year bundles (3,140 physical assets and 3,137 logical frontend rows); it did not upload or deploy any release.
- The WDASEC 2017 refresh added 519 normalized papers and changed no aggregate site count because all affected identities were already in existing multi-year bundles (3,140 physical assets and 3,137 logical frontend rows); it did not upload or deploy any release.
- The WDASEC 2016 refresh added 534 normalized papers and changed the aggregate local projection from 3,140 to 3,141 physical assets and from 3,137 to 3,138 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2015 refresh added 498 normalized papers and changed the aggregate local projection from 3,141 to 3,144 physical assets and from 3,138 to 3,141 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2014 refresh added 479 normalized papers and changed the aggregate local projection from 3,144 to 3,145 physical assets and from 3,141 to 3,142 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2013 refresh added 499 normalized papers and changed the aggregate local projection from 3,145 to 3,180 physical assets and from 3,142 to 3,177 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2012 refresh added 426 normalized papers and changed the aggregate local projection from 3,180 to 3,194 physical assets and from 3,177 to 3,191 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2011 refresh added 400 normalized papers and changed the aggregate local projection from 3,194 to 3,197 physical assets and from 3,191 to 3,194 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2010 refresh added 369 normalized papers and changed the aggregate local projection from 3,197 to 3,244 physical assets and from 3,194 to 3,241 logical frontend rows; it did not upload or deploy any release.
- The WDASEC 2009 refresh added 342 normalized papers and changed no aggregate site count because all affected identities were already in existing multi-year bundles (3,244 physical assets and 3,241 logical frontend rows); it did not upload or deploy any release.
- The WDASEC 2008 refresh added 342 normalized papers and changed no aggregate site count because all affected identities were already in existing multi-year bundles (3,244 physical assets and 3,241 logical frontend rows); it did not upload or deploy any release.
- A full Hakka historical publication attempt failed closed on one 2,094,415,387-byte listening ZIP, above the 1,900,000,000-byte multipart target. The failure exposed a bundler safety defect: stale parts could be removed before entry-size validation. The fix and regression test now validate source sizes before writing and preserve existing assets on failure.
- A read-only New Taipei list/detail/token probe found one official senior-teacher question/answer paper. The normal pipeline mirrored and normalized it with zero failures or review records, and a targeted local publication updated the existing bundle to five papers (20,542,479 bytes); history changed from 292 to 291 normalization gaps and from 716 to 717 completed events.
- A bounded 2026-07-26 teacher-source probe showed that all Central Alliance subject/final pages returned HTTP 200 but every paper row said `已截止` and exposed no file link; the three empty raw events are therefore source-expired evidence, not parser failures. The documented Kaohsiung regular and special endpoints both returned HTTP 404; its stale local special state was preserved and its elementary normalization gap remains an official-endpoint blocker.
- A live TCTE probe found that the ROC 92–94 official year pages use historical anchor-based layouts with direct paper/answer links. The backwards-compatible parser fix covered 420 normalized records (140, 140, and 140) with zero sync failures and approximately 174 MB of unique payloads; ROC 90–91 remain separate scope items because their answer surfaces are non-per-subject or non-downloadable.
- A bounded official MOEX refresh of the 148 historical normalization gaps recovered 137 events, added 35,402 normalized records, and produced zero sync failures. Eleven remain evidence-backed source/file blockers: eight official result pages return 查無結果 (094030, 094100, 094200, 094250, 093040, 093090, 093180, 093240), while 093170 has corrected-answer placeholders, 090270 has answer placeholders, and 085210 has a question placeholder.
- A full offline catalog migration now rebuilds the generated review queue from current papers instead of preserving stale rows. It removed 204 stale MOEX keys (147 legacy rows with empty evidence and 57 rows superseded by current classification), leaving 692 current review keys before the source-marker pass; the historical 166-key comparison is 105 high, 60 medium, and 1 review. The subsequent exact official `晉升士級` event-title mapping covered event IDs 082040, 082260, 084190, 084200, 084230, 085050, 085300, and 086250: 185 paper records moved to `promotion-worker-rank` at medium confidence, 61 current review keys were removed, no new review keys were added, and the current queue is 631.
- No public release, deployment, history rewrite, credential use, or remote publication occurred. The ignored mirror/bundle cache is operational state and is not evidence that remote release assets exist.

The scoped Hakka republish failed closed when one official listening ZIP exceeded the 1.9 GB multipart target. The failed, unreferenced 29.8 GB ignored temporary archive was removed; the preserved legacy current-year archive and reconstructed ignored current-year parts remain local, while no release was uploaded. The bundler now preflights source-entry sizes and preserves existing assets before an oversized-entry failure. The publication validator also received a one-line syntax repair that was verified locally.

## Validation baseline

| Check | Result | Interpretation |
| --- | --- | --- |
| uv run pytest -q | **524 passed, 70 subtests passed** in 1.81 s | Python functional baseline is green. |
| Standard-library trace over the Python suite | **9,974/11,915 executable app lines (83.71%)** across 101 traced app modules | `app/__main__.py` was not imported. This is line coverage only; it provides no branch coverage or live-source coverage. |
| python3 scripts/validate_publication.py | **Pass**: 3,244 site bundles, 3,241 frontend bundles, 3,244 release assets, 10 schemas; expected and actual logical site IDs both 3,241 | Generated publication shapes and provider-derived public eligibility agree. This is not official-source completeness, remote-asset verification, or proof that oversized Hakka audio is releasable. |
| python3 -m app plan-release | **Pass**: 3,244 physical bundles across 11 release shards | Local release capacity is within the 900-per-shard target and 1,000-per-shard hard limit. It does not prove remote release assets exist. |
| python3 -m app audit-catalog | **Pass**: 192,407 records; 4,283 review records; 631 queue entries; 770 mixed legacy groups requiring split; 0 stale and 0 missing queue keys | Strict mode passes because all review records have event-specific isolation, no review record is unapproved, and generated queue keys agree with current papers. It is an identity-safety result, not an archive-completeness result. |
| python3 -m app history-audit | Policy-aware non-strict **pass**; strict **fails** on 50 normalization gaps and 8 normalized-not-published events; 327 events are explicitly excluded by publication policy; download and parser gaps are both 0 | This is the most direct current provider-state/publication gap signal. |
| `python3 -m app migrate-legacy-state --provider moex --mode verify` | **Pass** | Legacy state verification is green. It does not validate current official-source discovery. |
| `bash -n .github/scripts/*.sh && git diff --check` | **Pass** | Shell syntax and whitespace gates are green. |
| Direct Node test runner | **11 passed, 2 failed of 13** | The two failures are `exam-classification` and `search-state`, both unable to import `typescript` because dependencies are not installed. |
| Node experimental coverage | **95.29% line, 80.23% branch, 100% function** over the loaded `frontend/build` modules | This is not frontend application coverage: the failing modules were not loaded and the React/TSX source was not instrumented. |
| `npm ci`, `npm test`, `npm run lint`, `npm run build` | **Not runnable locally** | `npm` is not installed, `/frontend/node_modules` is absent, and `/frontend/dist` is absent. No dependency installation was attempted. |
| Live source probe | **Stopped without a report** | The serial probe blocked in CEEC GSAT discovery at a 60-second URL open. This is an operational/network blocker, not evidence that CEEC or any later source is unavailable. |

Python linting is not configured in `pyproject.toml` or CI. The repository has Python tests and shell/whitespace checks, but no Ruff, Black, mypy, pylint, or flake8 gate.

## Source-coverage matrix

`raw → papers` is the current provider-state count. The range is AD unless stated otherwise. A range can contain internal gaps; the count of distinct year buckets is included where it matters.

### Registered providers

| Provider | Official source URL | Category and declared source scope | Source availability evidenced in repo | Local coverage (`raw → papers`) | Status | Restrictions / notes |
| --- | --- | --- | --- | --- | --- | --- |
| `moex` | https://wwwq.moex.gov.tw/exam/ | Ministry of Examination civil, professional, judicial, police, law, medical, and related public examinations | 1992-2026 retained in current raw state; 2025/2026 manifest has 21/8 exam codes | 1992-2026, 28 year buckets; 694 → 178,386 | **Partial / P0** | ASP.NET/official PDF endpoints; current source-manifest covers only 2025-2026. The latest bounded refresh recovered 137 historical events with 35,402 normalized records and zero sync failures; 11 events remain source/file blockers. Current MOEX history status is 11 normalization-gap events and 319 policy-excluded events; the source is not complete. |
| `ceec_gsat` | `https://www.ceec.edu.tw/xmfile?xsmsid=0J052424829869345634` | CEEC 學科能力測驗 / GSAT archive | 2011–2026 observed in provider state; live discovery was not completed | 2011–2026, 16 buckets; 94 → 367 | **Covered in declared scope; live verification blocked** | Public CEEC pages/PDFs, conservative pacing; no paid publications or browser automation. |
| `ceec_ast` | `https://www.ceec.edu.tw/xmfile?xsmsid=0J052427632928416650` | CEEC 分科測驗 general-paper archive | 2022–2026 in current state; provider spec is stale at 2022–2025 | 2022–2026; 30 → 169 | **Partial** | Public static/PDF source; special-paper and special-answer-sheet pages are intentionally excluded. History audit classifies 2 single-year events as excluded by publication policy. |
| `cpc_recruit` | `https://www.cpc.com.tw/News.aspx?n=32&sms=8969` | CPC Corporation company recruitment written papers | 2009–2025 observed | 2009–2025, 14 buckets; 14 → 17 | **Covered in declared scope** | Official CPC pages and linked files; the joint/MOEA page redirects to a Taipower archive handled by `moea_recruit`, so it must not be duplicated here. |
| `gept_cert` | `https://www.gept.org.tw/Exam_Intro/t01_introduction.asp` | GEPT official practice and listening materials by proficiency level | Current-year material scope; current state 2026 | 2026; 1 → 34 | **Covered, current-materials scope** | Practice materials, PDFs/ZIPs, and MP3s, not a full historical exam archive. Public source; reuse license not established. |
| `hakka_cert` | `https://elearning.hakka.gov.tw/hakka/download-files` | Hakka certification vocabulary/question-bank and audio materials | 2018–2026 observed across paginated official downloads | 2018–2026, 9 buckets; 11 → 156 | **Partial / release-capacity blocker** | PDFs and listening ZIPs are mirrored. Eight historical events remain normalized-but-not-published. A 2,094,415,387-byte official audio ZIP exceeds the 1.9 GB multipart target, so the current GitHub-release projection cannot publish the complete bundle without a scope or storage decision. |
| `hce_cmu` | https://spbcm.cmu.edu.tw/page/384 | CMU post-baccalaureate Chinese medicine entrance papers | 2021–2026 in current state | 2021–2026; 6 → 30 | **Covered in declared scope** | Public university pages/PDFs; the six retained events now publish all 30 mirrored papers. |
| `hce_nsysu` | `https://www.nsysu.edu.tw/p/412-1000-94.php?Lang=zh-tw` | NSYSU post-baccalaureate medicine entrance papers | 2022–2026 in current state | 2022–2026; 5 → 5 | **Covered in declared scope** | Official university/library archive; source availability still needs a bounded live verification. |
| `hce_nthu` | https://adms.site.nthu.edu.tw/p/403-1207-6125-1.php?Lang=zh-tw | NTHU post-baccalaureate medicine entrance papers | 2022–2026 in current state | 2022–2026; 5 → 24 | **Covered in declared scope** | Public admissions archive; the five retained events now publish all 24 mirrored papers. |
| `hce_tcu` | `https://admissions.tcu.edu.tw/?page_id=62` | Tzu Chi University post-baccalaureate Chinese medicine entrance papers | Current 2026 source scope | 2026; 1 → 8 | **Covered, current-year scope** | Public university source; historical archive not established. |
| `ipas_cert` | `https://ipd.nat.gov.tw/ipas/` | iPAS professional certification learning/question materials | Current-year scope; 2026 observed | 2026; 4 → 62 | **Covered, current-materials scope** | ISE/AIAP/OIA/AIOT source resources; some codes expose learning guides rather than past questions. |
| `jlpt_cert` | `https://www.jlpt.jp/e/samples/sampleindex.html` | JLPT official sample workbook and listening materials | Official sample sections for 2012 and 2018 observed | 2012 and 2018; 2 → 116 | **Covered, sample-materials scope** | Not a historical archive of every JLPT sitting; includes PDF/audio. Official source, no blanket redistribution license verified. |
| `moea_recruit` | `https://service.taipower.com.tw/exam/info.aspx` | Ministry of Economic Affairs state-owned-enterprise joint recruitment papers | 2001–2026 observed | 2001–2026, 21 buckets; 21 → 370 | **Partial / ownership review** | All 370 checksums are identical to `taipower_recruit`; decide whether these are two official exam families or duplicate source ownership before claiming coverage. |
| `post_recruit` | `https://svc.tabf.org.tw/115post02//Paper/Year` | Chunghwa Post first-test recruitment papers on an explicitly commissioned TABF host | 2023–2025 accepted in provider spec | 2023–2025; 3 → 112 | **Partial / refresh pending** | Third-party mirrors are rejected; current-year source availability and commissioning evidence need refresh. |
| `rcpet_cap` | `https://cap.rcpet.edu.tw/examination.html` | RCPET CAP / teacher-education screening exam papers | 2013–2026 observed | 2013–2026, 14 buckets; 15 → 136 | **Covered in declared scope** | Public page uses per-year iframe links; conservative scheduled sync. |
| `sfi_cert` | `https://www.sfi.org.tw/Node?id=217` | Securities and Futures Institute certification materials | 2025–2026 observed | 2025–2026; 15 → 30 | **Covered, current-materials scope** | Certification exam PDFs; scope and redistribution permissions remain provider-specific. |
| `special_admission` | `https://cis.ncu.edu.tw/EnableSys/admissionInfo/examInfo/question` | University special-admission / special-selection papers in the accepted 大學組 / 共同 scope | 2013–2026 documented | 2013–2026, 14 buckets; 14 → 216 | **Covered in declared scope** | No third-party mirrors; only accepted subjects and official paper assets. |
| `tabf_cert` | `https://www.tabf.org.tw/LicenseHistoryExam.aspx?PHID=424` | TABF banking/finance certification sample and historical materials | 2025–2026 observed | 2025–2026; 99 → 252 | **Covered, current-materials scope** | Paginated official source; source taxonomy is certification material, not a universal exam archive. |
| `taigi_cert` | `https://ttg.moe.edu.tw/tmt/view.php?page=resource` | Ministry of Education Taiwanese-language certification sample papers/audio | Current 2026 material scope | 2026; 3 → 35 | **Covered, current-materials scope** | A/B/C forms, PDFs/MP3s/ZIPs; source scope is sample materials. |
| `taipower_recruit` | `https://www.taipower.com.tw/2289/2544/2554/2557/simpleList` | Taipower recruitment written papers and answer keys | ROC 90 onward / AD 2001 through recent administrations | 2001–2026, 21 buckets; 21 → 370 | **Partial / ownership review** | Exact checksum duplicate of all `moea_recruit` paper records; multiple sessions can occur in a year. |
| `taisugar_recruit` | `https://www.taisugar.com.tw/chinese/News_Index.aspx?p=3&n=10080` | Taisugar recruitment paper announcements | 2025 observed | 2025; 1 → 1 | **Partial** | Listing mixes recruitment notices and exam material; one event is normalized but not published. |
| `tcte_tve` | `https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y` | TCTE 四技二專統一入學測驗 / TVE archive | Raw listing 2001–2026; ROC 92–94 direct paper/answer links verified; ROC 90–91 use irregular answer surfaces | raw 2001–2026; papers 2003–2026, 24 buckets; 26 → 2,956 | **Partial / historical format** | The adapter now covers ROC 92–94 anchor-based pages. ROC 90 exposes direct question links plus a non-downloadable HTML answer matrix; ROC 91 exposes direct question links plus a combined answer PDF. Those two years require an explicit scope/attachment decision. |
| `teacher_qual` | `https://tqa.rcpet.edu.tw/TEA_Exam/TEA03.aspx` | National teacher qualification exam | Source selector ROC 094–115 / AD 2005–2026 | 2005–2026, 22 buckets; 23 → 23 | **Covered in declared scope** | ASP.NET WebForms postbacks; 2018 is a format transition and 2017 is sample-only. Those semantics must remain visible in any completeness metric. |
| `teacher_recruit_central_alliance` | `https://qa115-tse-cl.twrecruit.com.tw/Subject/news.php` | Central-region annual teacher-selection question/answer site | Current 115 school year / AD 2026 only | 2026; 3 → 0 | **Blocked / source expired** | Annual vendor domain; official provenance comes from Taichung, Keelung, and Hsinchu sources. On 2026-07-26 all three subject/final page pairs returned HTTP 200 with paper rows marked `已截止` and no downloadable links. This is source-side expiry, not a parser failure. |
| `teacher_recruit_kaohsiung` | `https://exam.kh.edu.tw/teaexam/` | Kaohsiung elementary and special-education teacher recruitment | Current 2026 scope | 2026; 2 → 2 | **Partial / source endpoint blocker** | ZIP/PDF question and answer files; lists, venues, vacancies, brochures, duplicates, and teaching-demo topics are intentionally skipped. On 2026-07-26 both documented regular and special endpoints returned HTTP 404; one elementary normalization gap remains and no replacement official endpoint has been verified. |
| `teacher_recruit_newtaipei` | `https://career.ntpc.edu.tw/module/newtea/module/newtea/ap/out-announce?c=01` | New Taipei education-personnel joint-selection written papers | Current 2026 scope | 2026; 4 → 5 | **Covered, current-year scope** | Public list/detail/token API; the targeted 2026 senior-teacher paper refresh now leaves all four retained events complete. Teaching-demo, score, and list notices remain intentionally skipped. |
| `teacher_recruit_tainan` | `https://qualify.tn.edu.tw/trexamps/` | Tainan elementary and pre-K special-ed teacher recruitment | Current 2026 scope | 2026; 1 → 3 | **Covered, current-year scope** | Historical reconstruction is intentionally excluded until a stable official archive is found. |
| `teacher_recruit_taipei_elementary` | `https://www.gov.taipei/News_Content.aspx?n=D0042A87C2F0270A&sms=78D644F2755ACCAA&s=0E5FFDCD602F05C2` | Taipei elementary teacher joint recruitment | Reviewed 114 school year / AD 2025 | 2025; 1 → 12 | **Covered, reviewed current-year scope** | Fixed official article map; city-wide news listing is not treated as an archive. |
| `teacher_recruit_taipei_junior` | `https://www.doe.gov.taipei/News_Content.aspx?n=E831CA0A5CD0193D&sms=78D644F2755ACCAA&s=4A85C1A3A3BD7C48` | Taipei junior-high formal teacher recruitment | Reviewed 2024–2025 | 2024–2025; 2 → 68 | **Covered in reviewed scope** | Fixed official article map; no automatic future-year discovery until a stable endpoint exists. |
| `teacher_recruit_taoyuan_elementary` | `https://elementary.tyc.edu.tw/web/answer.aspx?openExternalBrowser=1` | Taoyuan elementary teacher joint recruitment | Current 2026 scope | 2026; 1 → 21 | **Covered, current-year scope** | Direct question/suggested/final answer files; appeal, score/list, and venue material skipped. |
| `tii_cert` | `https://edu.tii.org.tw/exam/users/exam_intro/1` | Taiwan Insurance Institute certification materials | 2025–2026 observed | 2025–2026; 3 → 5 | **Covered, current-materials scope** | Multiple official exam-intro pages; historical breadth not established. |
| `tocfl_cert` | `https://tocfl.edu.tw/tocfl/index.php/exam/download` | TOCFL reference and official mock-test question/audio/answer/script materials | 2022, 2024, and 2026 resource years observed | 2022–2026, 3 buckets; 3 → 95 | **Covered, reference/mock scope** | This is not a complete archive of every administered TOCFL exam; direct mock downloads are public. |
| `tqc_cert` | `https://www.tqc.org.tw/TQCNet/ExamPaper.aspx` | TQC certification sample-paper archive | 2015–2026 observed | 2015–2026, 11 buckets; 11 → 44 | **Covered in declared sample scope** | Paginated public source; sample papers rather than a complete sitting archive. |
| `twc_recruit` | `https://www.water.gov.tw/ch/Subject/Detail/59619?nodeId=715` | Taiwan Water Corporation recruitment papers | ROC 103–114 / AD 2014–2025, with source-list gaps documented | 2014–2025, 10 buckets; 10 → 10 | **Partial / sparse official archive** | Provider documents missing listing years as source sparsity, not automatically as parser failures. Current-year availability needs re-probe. |
| `wdasec_skill` | `https://owinform.wdasec.gov.tw/ExamNet/owInform/PastQuestions.aspx` | Workforce Development Agency skills-evaluation past questions | Raw sessions 2001–2026; usable paper records 2008–2026 after the 2026-07-28 refresh | raw 2001–2026; papers 2008–2026, 19 buckets; 143 → 8,267 | **Partial / P0 / storage blocker** | ASP.NET WebForms/ViewState/postbacks; three administrations per year. Official 2008–2024 refreshes produced 7,590 papers (342, 342, 369, 400, 426, 499, 479, 498, 534, 519, 534, 412, 437, 443, 456, 447, and 453) with zero sync failures; 105 event records are published complete and five are explicitly excluded by site policy, with five unpublished bundle IDs across those exclusions. Four of five 2008 events are complete and one is explicitly excluded; all six 2009 events are published complete; six of seven 2010 events are complete and one is explicitly excluded; three of six 2011 events are complete and three are explicitly excluded; five of seven 2012 events are complete and two are explicitly excluded; one 2015 event remains excluded. Eligible multi-year groups now appear in the local default site. The remaining 33 older raw events through 2007 are normalization gaps. |

### Known candidates, exclusions, and watch sources

These rows are part of the documented completeness scope review, but they are not registered active providers.

| Source / topic | Official source URL | Category | Available range | Local coverage | Status | Evidence / restriction |
| --- | --- | --- | --- | --- | --- | --- |
| HCE ISU | `https://www.isu.edu.tw/admissions` | ISU post-baccalaureate medicine entrance | Unknown | None | **Blocked / missing** | Official admissions pages exposed admission information but no public full-paper archive or direct paper/answer downloads. |
| HCE KMU | `https://enr.kmu.edu.tw/bac/bacm005.php` | KMU post-baccalaureate medicine entrance | Unknown | None | **Blocked / missing** | Official page exposed brief/schedule material, not a full-paper archive. |
| HCE NCHU | `https://recruit.nchu.edu.tw/college-exam/medicine/index-medicine.aspx?examc=F` | NCHU post-baccalaureate medicine entrance | Unknown | None | **Blocked / missing** | Official paths exposed forms, schedules, and dispute notices, not a full-paper archive. |
| TOPIK | `https://www.topik.go.kr/` | Korean-language proficiency exam | Browser practice/current flows; no stable paper range established | None | **Blocked** | Repository source proof found streamed/browser practice but no stable direct downloadable PDF/past-paper archive. |
| iCAP | `https://icap.wda.gov.tw/` | Competency standards and resource platform | Resource years, not exam years | None | **Intentionally out of scope** | Official resources are not an exam-paper archive. Add only if non-paper competency-resource bundles become an explicit product requirement. |
| 軍校正期班 / 專業軍官班 | Official MND recruitment surfaces; no accepted stable URL recorded | Military recruitment examinations | Unknown | None | **Blocked** | No stable official public historical/sample-paper archive was verified. |
| K-12 teacher-selection portal | `https://personnel.k12ea.gov.tw/tsn/` | National teacher openings/announcements | No paper archive | None | **Intentionally excluded** | Official portal exposes vacancies/news rather than downloadable past papers. |
| MOE teacher-opening portal | `https://tjn.moe.edu.tw/EduJin/Opening/Index` | National teacher openings/search | No paper archive | None | **Intentionally excluded** | Official portal is a job/opening search surface, not a paper archive. |
| Taichung / Keelung / Hsinchu teacher sites | `https://txg115-ts-e.twrecruit.com.tw/doubt.php`, `https://psexam.kl.edu.tw/Home/Index_Ann`, `https://prsteacher.hcc.edu.tw/Module/Bulletin/Index.php` | Teacher recruitment provenance/watch sources | One current year | Covered indirectly by Central Alliance provenance | **Intentionally not separate providers** | Their official notices point candidates to the Central Alliance paper site; annual vendor domains are not assumed to be historical archives. |
| Shuati coverage reference | `https://www.shuati.tw/exams` | Third-party coverage index | Not an official source | None | **Intentionally out of scope as a source** | Used only as a discovery checklist; the pipeline must not mirror third-party files. |

## Gap investigations

### Teacher recruitment

Teacher recruitment is correctly described as partial. The repository currently has seven recruitment-paper providers plus `teacher_qual`, but most recruitment providers are intentionally current-year or fixed-article scoped. The source index explicitly rejects national opening portals as paper archives, treats Taichung/Keelung/Hsinchu as provenance for the Central Alliance, and refuses a broad county/school crawler.

The immediate data defects are:

- `teacher_recruit_central_alliance`: 3 raw current-year events, 0 normalized papers; the official pages currently mark every paper `已截止` and provide no files.
- `teacher_recruit_newtaipei`: no remaining normalization-gap event in the reviewed 2026 scope; the targeted refresh added the senior-teacher paper and answer asset.
- `teacher_recruit_kaohsiung`: 1 normalization-gap event; both documented current endpoints returned HTTP 404 in the bounded probe.
- Current-year-only scope for Taipei elementary, Taoyuan, Tainan, New Taipei, Kaohsiung, and Central Alliance is intentional, but must remain visible in completion metrics.

The appropriate completion unit is therefore “every source-index row has a documented decision and every implemented row has complete current-year assets,” not “all county and school teacher recruitment is archived.”

### TOPIK, iCAP, and military recruitment

The three decisions are already documented and should not be silently reopened during implementation:

- TOPIK is blocked pending a stable official direct-download paper archive.
- iCAP is intentionally outside the paper-exam product; a separate non-paper resource product would require an explicit scope decision.
- Military recruitment is blocked pending a stable official historical/sample-paper archive.

Each blocked decision needs an evidence date and a recheck cadence, not an empty provider directory.

### MOEX 2025–2026

The named “missing MOEX 2025 data / empty 2025–2026 exam-code lists” symptom does not reproduce in the current or latest fetched `origin/main` state:

- 2025 manifest: 21 exam codes, 21 raw exam pages, 6,479 paper records.
- 2026 manifest: 8 exam codes, 8 raw exam pages, 2,559 paper records.

A subsequent bounded source refresh also confirmed official current rows for 112010 and six ROC-112 events; all 1,480 new normalized paper records are mirrored with zero provider failures. The remaining publication discrepancy is the documented single-year policy, not an empty code-list symptom.

- 2025 has 709 normalized bundle groups; 674 are represented in the site for ROC year 114, and the remaining 35 groups contain 339 records, all single-year groups.
- 2026 has 298 normalized bundle groups; 285 are represented in the site for ROC year 115, and the remaining 13 groups contain 105 records, all single-year groups.
- Publication validation now reports 3,244 site assets, 3,241 frontend rows, and 3,244 release assets; the provider-derived expected logical set and site logical set are both 3,241 with zero difference. The MOEX worker-promotion cycle contributed 14 physical/frontend/release assets and changed no non-MOEX bundle; the subsequent WDASEC 2023, 2022, 2021, 2020, 2019, 2015, 2014, 2013, 2012, 2011, 2010, 2009, and 2008 cycles contributed 17, 14, 8, 2, 1, 3, 1, 35, 14, 3, 47, 0, and 0 physical/frontend/release assets, respectively; the 2018 and 2017 cycles added no new site identity, while the 2016 cycle contributed one new identity.

The stale multi-year projection and the eligible multi-year targeted publication gaps are resolved. The remaining decision is whether the default site should expose a narrow current-year exception for these 444 single-year MOEX records; enabling a broad MOEX one-year override would expand the release beyond the current design, so it remains an explicit scope decision.

### Historical MOEX failures and reviews

The user-supplied counts are reproducible in Git commit `d42b0bd`:

- `data/providers/moex/sync-failures.json`: 5,403 records, all `stage=bundle`, all for ROC year 113.
- `data/providers/moex/review-queue.json`: 972 records, representing 166 unique semantic keys after deduplication.

Comparison against current state:

| Historical record | Current evidence | Result |
| --- | --- | --- |
| 5,403 failure keys | Every key has a current normalized paper and a valid mirrored payload | **0 still-valid mirror failures; 5,403 resolved at mirror level** |
| 5,403 failure keys | 5,375 failure rows map to bundle IDs occurring in `data/sites/default/bundles.json` | **5,375 public** |
| 5,403 failure keys | 28 failure rows map to valid mirrored papers whose logical groups remain outside the current site inventory | **28 policy-excluded publication items**, not active download failures |
| 166 unique review keys | 1 exact semantic key remains in the current generated MOEX review queue | **1 still valid as an unresolved review key** |
| 166 unique review keys | 165 keys remain in current normalized papers and now classify as 105 high and 60 medium | **165 reclassified; no historical key is missing from current papers** |
| Current failure files | All 35 provider failure files are empty | **No current failure queue**, but this does not prove source completeness |

The current generated queue has 631 deduplicated evidence keys after removing 204 stale rows (147 legacy rows with empty evidence and 57 rows superseded by current classification) and 61 additional keys resolved by the exact official `晉升士級` event-title mapping. The current catalog audit’s 4,283 review-confidence records are a broader record-level population than the historical 972 queue rows. Its `approved_review_isolated_records=4,283` and `unapproved_review_records=0` mean the identity policy is fail-safe; they do not mean the records have been semantically mapped or publicly published. The 28 historical failure rows outside the site are consistent with the current single-year publication policy and still require an explicit scope decision.

Only MOEX has a current source manifest. For the other providers, the same historical reconciliation cannot be made against a source manifest until provider-scoped manifests or equivalent discovery snapshots exist.

## Testing and validation gaps

### What is covered now

- Python unit/integration tests cover provider parsers, normalization, bundling, catalog audits, workflows, migrations, and storage behavior; the refreshed trace observed 9,974/11,915 executable app lines (83.71%) across 101 app modules, with `app/__main__.py` not imported.
- Pure frontend feed and logic tests cover generated bundle conversion, publication metadata, search-state behavior, and classification helpers when the TypeScript dependency is available.
- Publication schema and release-capacity validators run in CI and passed locally.

### What is missing

- No Python branch coverage measurement or configured Python lint gate.
- No frontend source-level test files under `frontend/src`; the 22 TSX components and hooks are not covered by component tests.
- No browser automation for the real built application.
- No accessibility automation (keyboard navigation, focus order, labels, contrast, axe/WCAG checks).
- No responsive/mobile smoke automation.
- No end-to-end test that loads the generated feed, searches/filter/sorts, reloads a shared URL, and follows a real published download URL.
- No automated check that remote GitHub release ZIP names/checksums are present and downloadable; local manifests only describe intended assets.
- No bounded, resumable live-source probe that produces a complete source inventory when one provider stalls.
- The checked-in provider/site registry documentation is stale in places: several providers are still labeled planned and some recorded test/coverage counts predate the current 524-test state.

## Deployment and gate gaps

.github/workflows/ci.yml remains the strongest gate: it runs Python tests, workflow-contract tests, strict catalog and event-level history audits, publication/schema validation, release planning, shell syntax, frontend tests, frontend lint, and frontend build. deploy-pages.yml now repeats the Python/catalog/publication/strict-history/release-plan gates and runs frontend tests and lint before the Pages artifact is uploaded. Its path filter includes application code, provider state, all default-site generated indexes, schemas, and the validator.

The remaining weaknesses are:

1. Most of the 35 provider-specific sync workflows commit only provider state and do not run aggregate site publication, audit, release planning, or frontend gates. Only the broader MOEX incremental/full/audit workflows publish the default site.
2. Provider refresh workflows can still create a newer provider state that waits for aggregate publication; this is now detectable by the provider-to-site validator when deployment or CI runs, but it is not yet prevented at the provider workflow boundary.
3. GitHub release coverage is checked by .github/scripts/release_assets.py in selected workflows, but this local audit did not call GitHub APIs or use credentials. Remote asset existence remains unverified here.
4. The new gate checks logical eligibility and generated metadata; it does not yet inspect every ZIP member/checksum or prove that official-source discovery is exhaustive.

## Prioritized backlog

### P0 — establish trustworthy completeness accounting

1. Decide and document whether the 444 current-year MOEX records excluded by the two-year site policy are intentionally outside the public scope or need a narrow current-year publication exception. Preserve all source records; do not reset or prune while investigating.
2. Add a provider-scoped discovery/manifest contract for every active provider, including source URL, probe timestamp, discovered years/events, file-level eligibility, blocked response evidence, and explicit exclusions.
3. Keep the event-level completeness ledger as the denominator for history-audit strict mode: covered, blocked, or explicitly excluded, with no unknown events.
4. Resolve the 1 still-valid historical review key and the current 631-entry review queue through authoritative mappings or explicit documented isolation decisions; the exact `晉升士級` family is now mapped, while mixed/ambiguous MOEX events remain isolated. Do not merge review records into confident bundles merely to make a count green.
5. Add aggregate publication and integrity gates to provider refresh workflows, or make them produce a clearly marked pending-publication change that cannot be mistaken for a released catalog.

### P1 — source and data-quality reconciliation

1. Recheck Central Alliance when the official annual paper pages expose files again; investigate the Kaohsiung replacement endpoint or accepted archival surface.
2. Resolve the 50 normalization-gap events and 8 normalized-not-published Hakka events; separately disposition the 33 older WDASEC events, its historical payload cost, and oversized Hakka audio before treating them as releasable coverage. The 327 policy-excluded events must remain evidence-backed.
3. Disposition TCTE ROC 90–91: ROC 90 has a non-downloadable HTML answer matrix, while ROC 91 has a combined answer PDF; either represent those official surfaces explicitly or keep them outside the per-subject paper denominator with evidence.
4. Reconcile the 770 mixed legacy groups requiring split and document the current physical/logical distinction: 3,244 physical assets, 3,241 logical IDs, with the policy-aware expected logical set equal to the site set.
5. Decide ownership of the exact 370-record/370-checksum duplication between `moea_recruit` and `taipower_recruit`.
6. Refresh stale provider specifications and the human registry so documented source scope, current year ranges, and test counts match executable state.
7. Establish a legal/takedown record for each source family before expanding release scope.

### P2 — validation surface

1. Add a maintained Python coverage command with line and branch reports and a practical threshold.
2. Restore the frontend toolchain in CI/local development and measure coverage over `frontend/src`, not only generated `frontend/build` modules.
3. Add browser smoke tests for the real production build, including search/filter/share/download flows and mobile layout.
4. Add accessibility checks for keyboard operation, focus visibility/order, form labels, semantic landmarks, and automated WCAG/axe violations.
5. Add an end-to-end release smoke check that verifies a sample release asset by name, checksum, and HTTP response.

### P3 — deferred source decisions

1. Recheck TOPIK only if a stable official direct-download paper archive appears.
2. Decide whether iCAP competency resources belong in this product; do not add them as exam papers by implication.
3. Recheck official MND surfaces for military recruitment papers.
4. Expand teacher recruitment only through source-index-approved official paper archives; do not build a broad county/school crawler.
5. Recheck HCE ISU, KMU, and NCHU only when public full-paper evidence exists.

## Measurable completion criteria

The completeness goal should be considered achieved only when all of the following are true for the explicitly approved scope:

1. The source matrix names every discovered official source, provider owner, category, URL, source year/event range, local range, legal review state, and status. Every row is `covered`, `blocked with evidence`, or `intentionally out of scope with a reason`; no row is `unknown`.
2. Every active provider has a current provider-scoped manifest or an equivalent signed/generated discovery snapshot. For each source event, the ledger can show raw page, eligible files, mirror checksum, normalized identity, public bundle, and release asset—or the precise blocked/excluded reason.
3. `history-audit --strict` passes with `download_gap=0`, `normalization_gap=0`, `normalized_not_published=0`, and `parser_gap=0` after approved blocked/excluded items are represented explicitly outside the covered denominator.
4. `audit-catalog --strict` passes with no unapproved review records, no stale or missing review-queue keys, no unexplained mixed legacy groups, and a documented disposition for every review-confidence record. A review-isolated record is not counted as complete unless its source scope and public visibility are also resolved.
5. Current provider state, site bundles, frontend feed, release-assets metadata, and actual remote release assets agree exactly for all covered records. The site/frontend set equality and release checksums are verified in CI.
6. MOEX 2025 and 2026 manifest counts, source events, normalized papers, site bundles, and release assets reconcile with zero empty-code-list or stale-publication discrepancies; any single-year exclusions are explicit, measured, and approved.
7. Teacher recruitment rows meet their declared scope: current-year providers contain all eligible official paper/answer files for the reviewed year, historical providers contain every documented source year, and watch/reject rows have evidence.
8. Every release shard remains below the 900 safety target and never approaches the 1,000 hard limit without an approved sharding plan.
9. Python and frontend tests, lint, coverage, browser smoke, accessibility, and end-to-end release checks are required on pull requests; deployment is conditional on the same green commit.
10. No credentials are stored in the repository, no source is mirrored from a private/third-party substitute, and every source family has an operator-reviewed redistribution/takedown decision.

## Blockers requiring a decision

- **Scope:** Should “complete” include practice/sample/reference materials and audio, or only administered examination papers and answer keys?
- **Teacher breadth:** Is the approved scope the current source-index set, or should every official county, city, and school recruitment source be pursued?
- **Teacher endpoint retention:** Should Central Alliance and Kaohsiung remain explicitly blocked with stale local state until their official pages recover, or may a newly verified official replacement/archive be added to the accepted source scope?
- **TCTE historical scope:** Should ROC 90/91 count as covered when ROC 90 exposes an HTML answer matrix and ROC 91 exposes one combined answer PDF, or should only per-subject downloadable question/answer files count?
- **Deferred topics:** Should iCAP non-paper resources be allowed, and should TOPIK/military recruitment remain blocked until direct-download evidence exists?
- **Source ownership:** Should the duplicate MOEA/Taipower records remain as two official categories, or should one become the canonical owner with an explicit alias?
- **Publication policy:** Should valid single-year bundles be public, or is the current multi-year default policy still intentional? This directly affects how source coverage and public coverage are reported.
- **Legal posture:** Is there an approved basis for redistributing official PDFs/audio in GitHub releases, or should the project store metadata/links only for some providers?
- **Release capacity:** Is the current GitHub Release/Pages architecture acceptable as the archive grows toward the 900-asset safety target and tens of gigabytes of local operational state? The official Hakka audio blocker and WDASEC historical refresh make this a current scope decision, not a future-only concern?
- **Integrity gate:** The strict event-level audit still fails on 50 normalization gaps and 8 normalized-not-published Hakka events; download and parser gaps are 0, and 327 events are explicitly policy-excluded. Which historical items may be explicitly blocked/excluded, including the 11 MOEX source/file blockers and 33 older WDASEC events, and which must be repaired before deployment is allowed?
- **Branch integration:** Should the local commits unique to `agent/exam-coverage-and-mirror-dedup` be intentionally ported onto latest `origin/main`, or should implementation start from latest main and preserve this branch only as an audit reference?

## Safest branch and release strategy

1. Keep the audit branch and its pre-existing `PLAN.md` intact as the baseline reference. The current corrective cycle is a reviewable local change on this branch; do not rebase it in place.
2. After reviewing the final local-cycle divergence of `24 ahead / 6 behind` from `origin/main` (`19 ahead` of the tracked upstream branch), create a fresh implementation branch from fetched `origin/main` (`d3af20f`). Port only intentionally selected changes by review/cherry-pick; do not merge generated data blindly.
3. Work in small provider/gate pull requests. Keep source-scope/manifest changes separate from generated mirror/bundle refreshes and from frontend changes.
4. Run the full CI contract before any source sync that could change `data/sites/default`, `bundles/`, or release metadata. Treat provider-only refreshes as pending until aggregate publication and release checks pass.
5. Use a dedicated data/release change only after source manifests, normalization review, mirror checksums, site publication, release planning, and remote asset coverage agree. Merge to `main` through CI; let GitHub Pages deploy only the green merge commit.
6. Do not upload, prune, delete, reset, rewrite history, or deploy from this workspace. Any future release operation should be a separately approved, auditable change with credentials confined to CI or an approved operator environment.
