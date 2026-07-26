# Completeness Baseline — 2026-07-26

This report records the baseline and the first corrective cycle. Baseline inspection was read-only; the cycle then regenerated only the targeted default-site publication projection and added validation/deployment gates. No provider-source data was fabricated, no public upload/deploy was performed, and no history was rewritten.

## Executive result

The repository has a working provider-to-frontend pipeline, but the archive is not complete under the requested definition. The current snapshot has:

- 35 registered providers and 147,514 normalized paper records.
- 2,410 physical site/release bundle assets, represented as 2,407 logical frontend rows, across 8 release shards after targeted MOEX reconciliation.
- 0 current sync-failure records, but 649 current MOEX review-queue entries and 2,989 review-confidence records isolated by event.
- 489 event-level download gaps, 299 normalization gaps, and 48 normalized-but-not-published events after the HCE targeted repair. The policy-aware provider-to-site check still finds 2,407 expected and 2,407 actual logical site IDs, with zero missing or extra IDs.
- only one checked-in source manifest: `data/providers/moex/source-manifest.json`.
- no completed live source probe: the serial probe was stopped after it blocked at the CEEC GSAT discovery request.

The current source state and the current public projection are therefore different completeness questions. MOEX 2025 and 2026 data are present locally, and all multi-year groups are now in the site inventory; 517 records remain excluded by the documented two-year public-bundle policy. Generated-manifest agreement alone is not evidence that every official source item is public or that the source itself has been exhaustively discovered.

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
| Official source discovery | `app/providers/base.py` defines discovery, page fetch, HEAD, and download contracts. Provider clients implement source-specific HTML/API/WebForms parsing. MOEX has a versioned source manifest; the other 34 providers do not. | Without a manifest or equivalent discovery evidence for every provider, missing years and newly published files cannot be distinguished from intentional scope. |
| Probe and change detection | `app/probe.py` and `app/history_audit.py` compare source events and local state. `history-audit --probe-sources` can call live discovery. | The live run was stopped at `ceec_gsat` after a 60-second URL-opening wait; there is no complete current external-source inventory. |
| Mirroring | `app/sync.py` validates file signatures, records checksums, reuses valid files, and writes provider-scoped mirrors. `app/storage.py` uses SHA-256 and a dedupe index. | The mirror is about 52 GB and is ignored operational state. Current failure queues are empty, but historical failure provenance must be retained separately. |
| Normalization and identity | `app/normalizer.py` emits `NormalizedPaper` records and review candidates. `app/classification.py` derives exam identity v2 dimensions and isolates unresolved evidence by event. | 2,989 records still have review confidence; 299 events have normalization gaps. A passing review-isolation audit means records are safely separated, not semantically resolved. |
| Bundling | `app/bundler.py` groups by v2 bundle ID, preserves legacy entries, validates mirror inputs, splits oversized archives, and applies site year policy. | The current default site is deliberately multi-year for most bundles. Provider state can contain valid single-year or unprojected bundles that are not public. |
| Site publication and release projection | `app/publisher.py` aggregates the 35 providers, filters by site policy, assigns v2 release tags, and writes `data/sites/default/`. `app/bundler.py` and `scripts/validate_publication.py` now share the public-year eligibility rule. `app/release_tags.py` targets 900 physical assets and hard-fails at 1,000. | The current snapshot has zero provider-derived logical IDs missing from or extra in the site inventory, but event-level history gaps remain. Local release planning does not verify that remote GitHub release assets actually exist. |
| Frontend display | `frontend/src/` consumes `frontend-bundles.json`; `frontend/build/` contains generated-feed and pure-logic tests. `App.tsx` supplies search, filters, sorting, pagination, and download rows. | There are no source-level component tests, browser tests, accessibility tests, or end-to-end tests. |
| CI and deployment | .github/workflows/ci.yml runs Python tests, strict catalog/history audits, publication/release checks, and frontend test/lint/build. GitHub Pages is canonical production; Netlify is preview-only. deploy-pages.yml repeats those data gates and frontend test/lint before upload. | Provider-specific refresh workflows still do not all run aggregate publication gates, and the strict history gate currently blocks deployment on unresolved event gaps. |

## Git and worktree baseline

Remote information was fetched with `git fetch --all --prune`; local work was not reset, rebased, overwritten, published, or deployed.

| Item | Baseline |
| --- | --- |
| Current branch | `agent/exam-coverage-and-mirror-dedup` |
| Audit starting HEAD | `1bf01863013dffbfc89b5b7d4b49702d38dbec7e` (`fix: repair workflow YAML command scalars`) |
| Tracked upstream at audit start | `origin/agent/exam-coverage-and-mirror-dedup`; divergence `0 ahead / 0 behind` |
| Latest fetched main | `origin/main` / `origin/HEAD` at `d3af20f` (`chore: refresh CEEC AST provider data`, 2026-07-25) |
| Current branch vs latest main at audit start | `5 ahead / 6 behind` |
| Unique current-branch commits | `1bf0186`, `d9920b7`, `5b21aed`, `8f38478`, `98aee3b` |
| Unique latest-main commits | `d3af20f`, `4168bea`, `59ed533`, `b197b3f`, `306f10c`, `de3f461` |
| Corrective-cycle change set | .github/workflows/{ci.yml,deploy-pages.yml}, app/bundler.py, app/publisher.py, data/sites/default/{bundles.json,frontend-bundles.json,release-assets.json}, scripts/validate_publication.py, two test files, and this report; intentionally not published remotely |
| Untracked files at audit baseline | `PLAN.md` only; it remains intentionally preserved and excluded from the corrective-cycle commit |
| Large ignored operational state | data/ about 301 MB; mirror/ about 52 GB; bundles/ about 78 GB |

At audit start the branch had no unpushed commits relative to its own upstream but was five commits ahead and six behind the fetched latest main. The corrective cycle is kept as a local reviewable commit; do not merge, rebase, reset, or cherry-pick it until the five-versus-six commit difference has been reviewed.

The attempted full local republish was interrupted before the Hakka bundle completed because it was consuming substantial ignored disk state; no tracked site metadata was damaged by that attempt. The subsequent targeted plans completed, and an unreferenced ignored Hakka base ZIP remains alongside the referenced multipart assets; it was not deleted.

## Validation baseline

| Check | Result | Interpretation |
| --- | --- | --- |
| `uv run pytest -q` | **517 passed, 70 subtests passed** in 1.81 s | Python functional baseline is green. |
| Standard-library trace over the Python suite | **9,773/9,773 executable app lines** across 116/117 app modules | 100% line signal for the traced app modules; `app/__main__.py` was not exercised. This provides no branch coverage and no live-source coverage. |
| `python3 scripts/validate_publication.py` | **Pass after reconciliation and policy gate**: 2,410 site bundles, 2,407 frontend bundles, 2,410 release assets, 10 schemas; expected and actual logical site IDs both 2,407 | Generated publication shapes and provider-derived public eligibility agree. This is not official-source completeness. |
| `python3 -m app plan-release --site-id default ...` | **Pass after reconciliation**: 2,410 physical bundles across 8 shards | Local release capacity is within the 900 target and 1,000 hard limit. It does not prove remote release assets exist. |
| `python3 -m app audit-catalog --site-id default ...` | **Pass after reconciliation**: 147,514 records; 2,989 review records; 649 queue entries; 667 legacy groups requiring split | Strict mode passes because all review records have event-specific isolation and no review record is unapproved. It is an identity-safety result, not an archive-completeness result. |
| `python3 -m app history-audit --site-id default ...` | Post-HCE-repair non-strict **pass**; strict **fails** on 489 download gaps, 299 normalization gaps, and 48 normalized-not-published events; parser gaps 0 | This is the most direct current provider-state/publication gap signal. |
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
| `moex` | https://wwwq.moex.gov.tw/exam/ | Ministry of Examination civil, professional, judicial, police, law, medical, and related public examinations | 1992–2026 retained in current raw state; 2025/2026 manifest has 21/8 exam codes | 1992–2026, 28 year buckets; 694 → 141,504 | **Partial / P0** | ASP.NET/official PDF endpoints; current `source-manifest.json` covers only 2025–2026. Targeted publication added 102 missing policy-eligible logical groups (97 from the 2025–2026 repair plus 5 found by the policy reconciliation). The remaining 43 2025 groups/412 records and 13 2026 groups/105 records are single-year groups excluded by the documented two-year public policy. |
| `ceec_gsat` | `https://www.ceec.edu.tw/xmfile?xsmsid=0J052424829869345634` | CEEC 學科能力測驗 / GSAT archive | 2011–2026 observed in provider state; live discovery was not completed | 2011–2026, 16 buckets; 94 → 367 | **Covered in declared scope; live verification blocked** | Public CEEC pages/PDFs, conservative pacing; no paid publications or browser automation. |
| `ceec_ast` | `https://www.ceec.edu.tw/xmfile?xsmsid=0J052427633128416650` | CEEC 分科測驗 general-paper archive | 2022–2026 in current state; provider spec is stale at 2022–2025 | 2022–2026; 30 → 169 | **Partial** | Public static/PDF source; special-paper and special-answer-sheet pages are intentionally excluded. History audit has 2 normalized-not-published events. |
| `cpc_recruit` | `https://www.cpc.com.tw/News.aspx?n=32&sms=8969` | CPC Corporation company recruitment written papers | 2009–2025 observed | 2009–2025, 14 buckets; 14 → 17 | **Covered in declared scope** | Official CPC pages and linked files; the joint/MOEA page redirects to a Taipower archive handled by `moea_recruit`, so it must not be duplicated here. |
| `gept_cert` | `https://www.gept.org.tw/Exam_Intro/t01_introduction.asp` | GEPT official practice and listening materials by proficiency level | Current-year material scope; current state 2026 | 2026; 1 → 34 | **Covered, current-materials scope** | Practice materials, PDFs/ZIPs, and MP3s, not a full historical exam archive. Public source; reuse license not established. |
| `hakka_cert` | `https://elearning.hakka.gov.tw/hakka/download-files` | Hakka certification vocabulary/question-bank and audio materials | 2018–2026 observed across paginated official downloads | 2018–2026, 9 buckets; 11 → 156 | **Partial** | PDFs and listening ZIPs are mirrored. Eight events are normalized-but-not-published in the current history audit. |
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
| `tcte_tve` | `https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y` | TCTE 四技二專統一入學測驗 / TVE archive | Raw listing 2001–2026; paper downloads documented 2006–2026 | raw 2001–2026; papers 2006–2026, 21 buckets; 26 → 2,536 | **Partial** | Five old events have normalization gaps. Older source rows without downloadable paper assets must be explicitly classified rather than silently omitted. |
| `teacher_qual` | `https://tqa.rcpet.edu.tw/TEA_Exam/TEA03.aspx` | National teacher qualification exam | Source selector ROC 094–115 / AD 2005–2026 | 2005–2026, 22 buckets; 23 → 23 | **Covered in declared scope** | ASP.NET WebForms postbacks; 2018 is a format transition and 2017 is sample-only. Those semantics must remain visible in any completeness metric. |
| `teacher_recruit_central_alliance` | `https://qa115-tse-cl.twrecruit.com.tw/Subject/news.php` | Central-region annual teacher-selection question/answer site | Current 115 school year / AD 2026 only | 2026; 3 → 0 | **Partial / parser blocker** | Annual vendor domain; official provenance comes from Taichung, Keelung, and Hsinchu sources. Current raw events produced no normalized papers. |
| `teacher_recruit_kaohsiung` | `https://exam.kh.edu.tw/teaexam/` | Kaohsiung elementary and special-education teacher recruitment | Current 2026 scope | 2026; 2 → 2 | **Partial** | ZIP/PDF question and answer files; lists, venues, vacancies, brochures, duplicates, and teaching-demo topics are intentionally skipped. One normalization gap remains. |
| `teacher_recruit_newtaipei` | `https://career.ntpc.edu.tw/module/newtea/module/newtea/ap/out-announce?c=01` | New Taipei education-personnel joint-selection written papers | Current 2026 scope | 2026; 4 → 4 | **Partial** | Public list/detail/token API; teaching-demo, score, and list notices are skipped. One normalization gap remains. |
| `teacher_recruit_tainan` | `https://qualify.tn.edu.tw/trexamps/` | Tainan elementary and pre-K special-ed teacher recruitment | Current 2026 scope | 2026; 1 → 3 | **Covered, current-year scope** | Historical reconstruction is intentionally excluded until a stable official archive is found. |
| `teacher_recruit_taipei_elementary` | `https://www.gov.taipei/News_Content.aspx?n=D0042A87C2F0270A&sms=78D644F2755ACCAA&s=0E5FFDCD602F05C2` | Taipei elementary teacher joint recruitment | Reviewed 114 school year / AD 2025 | 2025; 1 → 12 | **Covered, reviewed current-year scope** | Fixed official article map; city-wide news listing is not treated as an archive. |
| `teacher_recruit_taipei_junior` | `https://www.doe.gov.taipei/News_Content.aspx?n=E831CA0A5CD0193D&sms=78D644F2755ACCAA&s=4A85C1A3A3BD7C48` | Taipei junior-high formal teacher recruitment | Reviewed 2024–2025 | 2024–2025; 2 → 68 | **Covered in reviewed scope** | Fixed official article map; no automatic future-year discovery until a stable endpoint exists. |
| `teacher_recruit_taoyuan_elementary` | `https://elementary.tyc.edu.tw/web/answer.aspx?openExternalBrowser=1` | Taoyuan elementary teacher joint recruitment | Current 2026 scope | 2026; 1 → 21 | **Covered, current-year scope** | Direct question/suggested/final answer files; appeal, score/list, and venue material skipped. |
| `tii_cert` | `https://edu.tii.org.tw/exam/users/exam_intro/1` | Taiwan Insurance Institute certification materials | 2025–2026 observed | 2025–2026; 3 → 5 | **Covered, current-materials scope** | Multiple official exam-intro pages; historical breadth not established. |
| `tocfl_cert` | `https://tocfl.edu.tw/tocfl/index.php/exam/download` | TOCFL reference and official mock-test question/audio/answer/script materials | 2022, 2024, and 2026 resource years observed | 2022–2026, 3 buckets; 3 → 95 | **Covered, reference/mock scope** | This is not a complete archive of every administered TOCFL exam; direct mock downloads are public. |
| `tqc_cert` | `https://www.tqc.org.tw/TQCNet/ExamPaper.aspx` | TQC certification sample-paper archive | 2015–2026 observed | 2015–2026, 11 buckets; 11 → 44 | **Covered in declared sample scope** | Paginated public source; sample papers rather than a complete sitting archive. |
| `twc_recruit` | `https://www.water.gov.tw/ch/Subject/Detail/59619?nodeId=715` | Taiwan Water Corporation recruitment papers | ROC 103–114 / AD 2014–2025, with source-list gaps documented | 2014–2025, 10 buckets; 10 → 10 | **Partial / sparse official archive** | Provider documents missing listing years as source sparsity, not automatically as parser failures. Current-year availability needs re-probe. |
| `wdasec_skill` | `https://owinform.wdasec.gov.tw/ExamNet/owInform/PastQuestions.aspx` | Workforce Development Agency skills-evaluation past questions | Raw sessions 2001–2026; usable paper records currently 2025–2026 | raw 2001–2026; papers 2025–2026, 2 buckets; 143 → 677 | **Partial / P0** | ASP.NET WebForms/ViewState/postbacks; three administrations per year. 134 normalization gaps and 5 normalized-not-published events remain. |

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

- `teacher_recruit_central_alliance`: 3 raw current-year events, 0 normalized papers.
- `teacher_recruit_newtaipei`: 1 normalization-gap event.
- `teacher_recruit_kaohsiung`: 1 normalization-gap event.
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

The actual current issue was publication reconciliation. A targeted publication plan for the 153 MOEX 2025–2026 bundle IDs absent from the site was run through the normal publisher:

- 2025 now has 709 normalized bundle groups; 666 are in the site inventory, and the remaining 43 groups contain 412 records, all single-year groups.
- 2026 now has 298 normalized bundle groups; 285 are in the site inventory, and the remaining 13 groups contain 105 records, all single-year groups.
- Publication validation now reports 2,410 site assets, 2,407 frontend rows, and 2,410 release assets; the provider-derived expected logical set and site logical set are both 2,407 with zero difference.

The stale multi-year projection is resolved. The remaining decision is whether the default site should expose a narrow current-year exception for these 517 single-year records; enabling all MOEX single-year groups would add approximately 2,552 historical groups and exceed the current release design, so a broad `moex-*` one-year override is unsafe.

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
| 166 unique review keys | 149 exact semantic keys remain in the current MOEX review queue | **149 still valid as unresolved review keys** |
| 166 unique review keys | 17 keys no longer appear as review keys, while their source events remain current | **17 reclassified; not evidence to delete** |
| Current failure files | All 35 provider failure files are empty | **No current failure queue**, but this does not prove source completeness |

The current catalog audit’s 2,989 review-confidence records are a broader record-level population than the historical 972 queue rows. Its `approved_review_isolated_records=2,989` and `unapproved_review_records=0` mean the identity policy is fail-safe; they do not mean the records have been semantically mapped or publicly published. The 28 historical failure rows outside the site are consistent with the current single-year publication policy and still require an explicit scope decision.

Only MOEX has a current source manifest. For the other providers, the same historical reconciliation cannot be made against a source manifest until provider-scoped manifests or equivalent discovery snapshots exist.

## Testing and validation gaps

### What is covered now

- Python unit/integration tests cover provider parsers, normalization, bundling, catalog audits, workflows, migrations, and storage behavior sufficiently to execute every traced executable app line except `app/__main__.py`.
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
- The checked-in provider/site registry documentation is stale in places: several providers are still labeled planned and some recorded test/coverage counts predate the current 517-test state.

## Deployment and gate gaps

.github/workflows/ci.yml remains the strongest gate: it runs Python tests, workflow-contract tests, strict catalog and event-level history audits, publication/schema validation, release planning, shell syntax, frontend tests, frontend lint, and frontend build. deploy-pages.yml now repeats the Python/catalog/publication/strict-history/release-plan gates and runs frontend tests and lint before the Pages artifact is uploaded. Its path filter includes application code, provider state, all default-site generated indexes, schemas, and the validator.

The remaining weaknesses are:

1. Most of the 35 provider-specific sync workflows commit only provider state and do not run aggregate site publication, audit, release planning, or frontend gates. Only the broader MOEX incremental/full/audit workflows publish the default site.
2. Provider refresh workflows can still create a newer provider state that waits for aggregate publication; this is now detectable by the provider-to-site validator when deployment or CI runs, but it is not yet prevented at the provider workflow boundary.
3. GitHub release coverage is checked by .github/scripts/release_assets.py in selected workflows, but this local audit did not call GitHub APIs or use credentials. Remote asset existence remains unverified here.
4. The new gate checks logical eligibility and generated metadata; it does not yet inspect every ZIP member/checksum or prove that official-source discovery is exhaustive.

## Prioritized backlog

### P0 — establish trustworthy completeness accounting

1. Decide and document whether the 517 current-year MOEX records excluded by the two-year site policy are intentionally outside the public scope or need a narrow current-year publication exception. Preserve all source records; do not reset or prune while investigating.
2. Add a provider-scoped discovery/manifest contract for every active provider, including source URL, probe timestamp, discovered years/events, file-level eligibility, blocked response evidence, and explicit exclusions.
3. Make an event-level completeness ledger the denominator for `history-audit --strict`: covered, blocked, or excluded, with no unknown events.
4. Resolve the 149 still-valid historical review keys and the current review queue through authoritative mappings or explicit documented isolation decisions. Do not merge review records into confident bundles merely to make a count green.
5. Add aggregate publication and integrity gates to provider refresh workflows, or make them produce a clearly marked pending-publication change that cannot be mistaken for a released catalog.

### P1 — source and data-quality reconciliation

1. Repair Central Alliance teacher parsing and the New Taipei/Kaohsiung normalization gaps.
2. Resolve the 299 normalization-gap events and 48 normalized-not-published events reported by the post-HCE history audit, starting with MOEX, WDASEC, TCTE, Hakka, and teacher recruitment; distinguish policy-excluded single-year items from actual publication defects.
3. Reconcile the 667 legacy groups requiring split and document the current physical/logical distinction: 2,410 physical assets, 2,407 logical IDs, with the policy-aware expected logical set equal to the site set.
4. Decide ownership of the exact 370-record/370-checksum duplication between `moea_recruit` and `taipower_recruit`.
5. Refresh stale provider specifications and the human registry so documented source scope, current year ranges, and test counts match executable state.
6. Establish a legal/takedown record for each source family before expanding release scope.

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
4. `audit-catalog --strict` passes with no unapproved review records, no unexplained mixed legacy groups, and a documented disposition for every review-confidence record. A review-isolated record is not counted as complete unless its source scope and public visibility are also resolved.
5. Current provider state, site bundles, frontend feed, release-assets metadata, and actual remote release assets agree exactly for all covered records. The site/frontend set equality and release checksums are verified in CI.
6. MOEX 2025 and 2026 manifest counts, source events, normalized papers, site bundles, and release assets reconcile with zero empty-code-list or stale-publication discrepancies; any single-year exclusions are explicit, measured, and approved.
7. Teacher recruitment rows meet their declared scope: current-year providers contain all eligible official paper/answer files for the reviewed year, historical providers contain every documented source year, and watch/reject rows have evidence.
8. Physical release assets remain below the 900 safety target and never approach the 1,000 hard limit without an approved sharding plan.
9. Python and frontend tests, lint, coverage, browser smoke, accessibility, and end-to-end release checks are required on pull requests; deployment is conditional on the same green commit.
10. No credentials are stored in the repository, no source is mirrored from a private/third-party substitute, and every source family has an operator-reviewed redistribution/takedown decision.

## Blockers requiring a decision

- **Scope:** Should “complete” include practice/sample/reference materials and audio, or only administered examination papers and answer keys?
- **Teacher breadth:** Is the approved scope the current source-index set, or should every official county, city, and school recruitment source be pursued?
- **Deferred topics:** Should iCAP non-paper resources be allowed, and should TOPIK/military recruitment remain blocked until direct-download evidence exists?
- **Source ownership:** Should the duplicate MOEA/Taipower records remain as two official categories, or should one become the canonical owner with an explicit alias?
- **Publication policy:** Should valid single-year bundles be public, or is the current multi-year default policy still intentional? This directly affects how source coverage and public coverage are reported.
- **Legal posture:** Is there an approved basis for redistributing official PDFs/audio in GitHub releases, or should the project store metadata/links only for some providers?
- **Release capacity:** Is the current GitHub Release/Pages architecture acceptable as the archive grows toward the 900-asset safety target and tens of gigabytes of local operational state?
- **Integrity gate:** The strict event-level audit still fails on 489 download gaps, 299 normalization gaps, and 48 normalized-not-published events. Which historical items may be explicitly blocked/excluded, and which must be repaired before deployment is allowed?
- **Branch integration:** Should the five commits unique to `agent/exam-coverage-and-mirror-dedup` be intentionally ported onto latest `origin/main`, or should implementation start from latest main and preserve this branch only as an audit reference?

## Safest branch and release strategy

1. Keep the audit branch and its pre-existing `PLAN.md` intact as the baseline reference. The current corrective cycle is a reviewable local change on this branch; do not rebase it in place.
2. After reviewing the five-versus-six commit divergence, create a fresh implementation branch from fetched `origin/main` (`d3af20f`). Port only intentionally selected changes by review/cherry-pick; do not merge generated data blindly.
3. Work in small provider/gate pull requests. Keep source-scope/manifest changes separate from generated mirror/bundle refreshes and from frontend changes.
4. Run the full CI contract before any source sync that could change `data/sites/default`, `bundles/`, or release metadata. Treat provider-only refreshes as pending until aggregate publication and release checks pass.
5. Use a dedicated data/release change only after source manifests, normalization review, mirror checksums, site publication, release planning, and remote asset coverage agree. Merge to `main` through CI; let GitHub Pages deploy only the green merge commit.
6. Do not upload, prune, delete, reset, rewrite history, or deploy from this workspace. Any future release operation should be a separately approved, auditable change with credentials confined to CI or an approved operator environment.
