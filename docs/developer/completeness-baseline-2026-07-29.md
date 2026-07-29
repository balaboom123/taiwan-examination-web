# Completeness Baseline — 2026-07-29

This is the current baseline for the long-running completeness goal. It records the official-source inventory, the source-to-frontend flow, current generated-state reconciliation, validation gaps, and the decisions still required. It does not claim that generated manifests prove archive completeness. No source was fabricated, no credentials were exposed, no history was rewritten, and no release or deployment was performed.

## Executive result

The repository has a functioning source → mirror → normalize → bundle → frontend pipeline, but the archive is not complete under the agreed definition.

- 35 providers are registered in the default site. Current retained state contains 1,379 raw event pages and 226,287 normalized paper records after recovering MOEX AD 2017 and AD 2019–2021 and newly listed AD 2026 events.
- The local default projection contains 3,357 physical site/release assets, 3,354 frontend logical rows, and 12 planned release shards.
- Current generated state has five MOEX download failures. All five are exact, reviewed file-level placeholder exceptions; they are not ignored failures. Three affected events retain 377 valid normalized records.
- The strict history audit reports 1,020 published-complete events, 15 event-level blocked exceptions, 3 partially blocked events, 332 publication-policy exclusions, and 8 normalized-but-not-published Hakka events. It reports zero parser gaps, zero normalization gaps, zero unclassified failure rows, and zero orphaned coverage exceptions.
- The current MOEX review queue is 655 entries; the catalog audit isolates 4,379 review-confidence records with no stale/missing queue keys and no unapproved review records. These are identity-safety results, not proof of semantic completeness.
- A reviewed machine-readable scope inventory now covers all 35 registered providers and 10 candidate/watch sources. Its validator matches exact local years, raw event counts, normalized record counts, and failure counts; MOEX now has a complete 35-year/870-code official discovery manifest, while the other 34 providers lack current discovery snapshots and 89 MOEX-listed events remain unrepresented locally.
- The inventory currently classifies registered providers as 22 covered, 12 partial, and 1 blocked; candidate/watch rows are 5 blocked and 5 intentionally out of scope. Every row has an official-source field, availability note, restriction, and evidence reference.

The practical completion definition is:

> Every discoverable official public source inside the documented scope is either covered, explicitly blocked with reproducible evidence, or intentionally excluded with a reason. “Unknown” is not a completion state.

The current archive fails that definition because source discovery is not yet exhaustive across all providers, eight Hakka events remain outside the public projection for a storage/release reason, and several scope/legal decisions remain open.

## End-to-end data flow and trust boundaries

| Stage | Current implementation | Remaining completeness risk |
| --- | --- | --- |
| Official discovery | Provider contracts and adapters in `app/providers/`; reviewed scope is machine-validated by `catalog/source-inventory.json` and `scripts/validate_source_inventory.py`; MOEX discovery/probe state is manifest-backed. | 34 providers have no equivalent current manifest. MOEX’s 870-code manifest identifies 89 official event codes not yet represented locally; a manifest is not archive coverage by itself. |
| Probe and change detection | `app/probe.py` and `app/history_audit.py`; source probing is optional and read-only. | A complete serial live probe was not achieved because an upstream request stalled; bounded source checks are provider-specific. |
| Fetch and mirroring | `app/sync.py`, `app/storage.py`, provider-scoped mirrors, checksums, payload-signature validation. | Current HTML placeholders correctly become failures; the five current failures are evidence-backed but still unavailable. |
| Reviewed coverage accounting | `catalog/source-coverage/<provider_id>.json` records narrow event/file blockers and intentional exclusions. Strict audit matches exact current raw events/failures and flags conflicts/orphans. | Evidence has to be refreshed when a source changes; the ledger is not a substitute for discovery. |
| Normalization | `app/normalizer.py` and identity-v2 classification produce normalized records and review queues. | 4,379 review-confidence records and 655 MOEX queue entries still need disposition; isolation is not semantic approval. |
| Bundling | `app/bundler.py` builds v2 identity bundles and validates mirrors. | Valid records can remain single-year or too large for the current public release model. |
| Site and release projection | `app/publisher.py`, `data/sites/default/`, `scripts/validate_publication.py`, `plan-release`. | Local metadata does not prove remote GitHub release assets exist; Hakka audio exceeds current size assumptions. |
| Frontend display | `frontend/src/` consumes generated `frontend-bundles.json`; build/logic checks exist. | No source-level component, browser, accessibility, responsive, or end-to-end coverage. |
| CI/deployment | CI and Pages workflows run Python/data/frontend gates, but most provider-only workflows stop before aggregate publication. | A provider refresh can wait for publication unless aggregate gates are required at the workflow boundary. |

The workflow audit found that `.github/workflows/ci.yml` and `.github/workflows/deploy-pages.yml` run the Python tests, strict catalog/history audits, publication validation, source-inventory (non-strict) validation, release planning, frontend tests, lint, and build. They do not provide browser, accessibility, or release-download E2E gates. The provider refresh workflows (`sync-*.yml`) generally sync and commit their provider state without those aggregate checks; MOEX incremental/full workflows also publish or upload before a complete post-refresh gate. `discover.yml` produces a read-only artifact and does not write a durable manifest. `sync-full.yml` retains an explicit hosted-bootstrap bypass input, which is a controlled operational escape hatch requiring a policy decision.

## Git and worktree baseline

Remote metadata was fetched with `git fetch --all --prune`; no reset, rebase, overwrite, push, release upload, or deployment occurred.

| Item | Current observation |
| --- | --- |
| Branch | `agent/exam-coverage-and-mirror-dedup` |
| Initial audit checkpoint | `254aa70` (`audit source coverage blockers and baseline`) |
| Preparation commit | `b579bc6` (`data: recover MOEX discovery and 2021 coverage`) |
| Final report handoff | Documentation follow-up after the preparation commit; history is preserved, not rewritten |
| Latest fetched `origin/main` | `8be0e4f` (`chore: refresh TABF cert provider data`, 2026-07-27) |
| Divergence from `origin/main` at final handoff | 7 behind / 55 ahead |
| Divergence from tracked upstream at final handoff | 0 behind / 50 ahead; all are unpushed |
| Tracked uncommitted files at final handoff | None |
| Untracked user work at final handoff | `PLAN.md` only; preserved and excluded from both checkpoints |
| Large untracked files | None after the preparation commit. Ignored operational trees are approximately 412 MB `data/`, 57 GB `mirror/`, and 62 GB `bundles/`; size is not release evidence. |

The audit checkpoints are local and reviewable. No remote branch, release, deployment, credential state, or history was rewritten.

## Validation baseline

| Check | Current result | Interpretation |
| --- | --- | --- |
| Focused new/audit/CLI tests | **56 passed** | Discovery-manifest writing, exact source-exception matching, conflict/orphan handling, strict targeted partial mode, and existing audit behavior are covered. |
| Full Python tests | **531 passed, 72 subtests passed** in 19.86 s via `uv run pytest -q` | Python functional baseline is green. |
| `python3 scripts/validate_publication.py` | **Pass**: 3,357 site bundles, 3,354 frontend bundles, 3,357 release assets, 18 JSON schema/catalog files | Generated publication and provider-derived public eligibility agree. This does not prove official-source completeness or remote-asset existence. |
| `python3 -m app plan-release` | **Pass**: 3,357 bundles across 12 shards | Local shard capacity is within the 900 safety target; it does not verify remote releases. |
| `python3 scripts/validate_source_inventory.py` | **Pass**: 35 providers and 10 candidates; local state matches the reviewed inventory; 1 discovery manifest is present, 34 are missing, and 89 manifest events are unrepresented | This is a scope/state-drift gate, not proof of live source completeness. `--require-discovery-manifests` remains intentionally failing until the 34 provider snapshots and 89 MOEX events are resolved. |
| `python3 scripts/validate_source_inventory.py --require-discovery-manifests` | **Exit 1**: complete discovery remains unresolved for 35 providers (34 missing manifests plus MOEX’s 89 unrepresented events) | This is the authoritative completeness blocker; it prevents a manifest-only completeness claim. |
| `python3 -m app history-audit --strict` | **Exit 1**: only the 8 Hakka `normalized_not_published` events remain unresolved; 15 blocked and 3 partial events are evidence-backed | The gate no longer hides the five current MOEX download failures and rejects coverage-exception conflicts/orphans. |
| `python3 -m app audit-catalog --strict` | **Pass**: 226,287 records; 4,379 review records; 655 queue entries; 776 mixed legacy groups; 0 stale/missing queue keys; 0 unapproved review records | Identity/review state is fail-safe, not a claim that every official source is covered. |
| Python line coverage | **83.66% executed lines**: 10,416/12,451 across 103 `app` modules, measured with standard-library `trace` | No branch coverage or threshold is configured; this is a reproducible measurement, not a CI gate. |
| Python lint | **No configured gate** | No Ruff/Black/mypy/pylint/flake8 command exists in the repository. |
| Frontend direct tests | **11 passed, 2 failed** via the existing Node entrypoint | Two test modules cannot import `typescript`; npm dependencies are absent. The passing subset is 11 tests. |
| Frontend coverage | **95.29% line, 80.23% branch, 100% function** over the two runnable generated `frontend/build` modules using Node’s built-in coverage | Not source-level React/TSX coverage; the two failing TypeScript-transpilation modules were not loaded. |
| `npm ci`, frontend test/lint/build | **Not runnable in the baseline environment** | `npm` is unavailable and `frontend/node_modules`/`frontend/dist` are absent; no dependency install was attempted. |
| Browser/UI/accessibility/E2E | **Missing** | No real-browser, keyboard/focus, WCAG/axe, responsive, shared-link, or release-download smoke gate exists. |

## Source-coverage matrix

The matrix below preserves the repository’s documented 35-provider scope and candidate/watch sources. “Covered” means covered in the declared repository scope, not a claim that every external historical item was freshly discovered. Exact current blocker evidence is stored under `catalog/source-coverage/`.

`raw → papers` is the current provider-state count. The range is AD unless stated otherwise. A range can contain internal gaps; the count of distinct year buckets is included where it matters.

### Registered providers

| Provider | Official source URL | Category and declared source scope | Source availability evidenced in repo | Local coverage (`raw → papers`) | Status | Restrictions / notes |
| --- | --- | --- | --- | --- | --- | --- |
| `moex` | https://wwwq.moex.gov.tw/exam/ | Ministry of Examination civil, professional, judicial, police, law, medical, and related public examinations | 1992–2026 official listing captured; 35 years and 870 exam codes | 1992–2026, 32 year buckets; 781 → 209,838 | **Partial / P0** | ASP.NET/official PDF endpoints; the official discovery manifest is complete for the current 870-code listing, but 89 listed historical events remain unsynced in 1994, 1998, and 2007. Eight historical result pages are documented as no-result blockers, and five exact file URLs return the same HTML placeholder; three affected events retain 377 valid normalized records. |
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
| `tcte_tve` | `https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y` | TCTE 四技二專統一入學測驗 / TVE archive | Raw listing 2001–2026; ROC 90/91 direct pages rechecked 2026-07-29 and returned HTTP 404 | raw 2001–2026; papers 2003–2026, 24 buckets; 26 → 2,956 | **Partial / blocked historical events** | ROC 90/91 are retained raw events with reviewed 404 evidence in `catalog/source-coverage/tcte_tve.json`; ROC 92–94 and later paper/answer surfaces remain covered in declared scope. |
| `teacher_qual` | `https://tqa.rcpet.edu.tw/TEA_Exam/TEA03.aspx` | National teacher qualification exam | Source selector ROC 094–115 / AD 2005–2026 | 2005–2026, 22 buckets; 23 → 23 | **Covered in declared scope** | ASP.NET WebForms postbacks; 2018 is a format transition and 2017 is sample-only. Those semantics must remain visible in any completeness metric. |
| `teacher_recruit_central_alliance` | `https://qa115-tse-cl.twrecruit.com.tw/Subject/news.php` | Central-region annual teacher-selection question/answer site | Current 115 school year / AD 2026; three official categories rechecked 2026-07-29 | 2026; 3 → 0 | **Blocked / source expired** | All subject/final page pairs returned HTTP 200, `已截止`, and no links; fingerprints and category mapping are recorded in `catalog/source-coverage/teacher_recruit_central_alliance.json`. Provenance remains official through Taichung, Keelung, and Hsinchu notices. |
| `teacher_recruit_kaohsiung` | `https://exam.kh.edu.tw/teaexam/` | Kaohsiung city elementary and special-education teacher recruitment | Current 2026 scope; regular and special endpoints rechecked 2026-07-29 | 2026; 2 → 2 | **Partial / source endpoint blocker** | Regular endpoint returned HTTP 404 (993 bytes) and special endpoint HTTP 404 (146 bytes); exact hashes are in `catalog/source-coverage/teacher_recruit_kaohsiung.json`. Special local papers remain covered; the elementary event is explicitly blocked. |
| `teacher_recruit_newtaipei` | `https://career.ntpc.edu.tw/module/newtea/module/newtea/ap/out-announce?c=01` | New Taipei education-personnel joint-selection written papers | Current 2026 scope | 2026; 4 → 5 | **Covered, current-year scope** | Public list/detail/token API; the targeted 2026 senior-teacher paper refresh now leaves all four retained events complete. Teaching-demo, score, and list notices remain intentionally skipped. |
| `teacher_recruit_tainan` | `https://qualify.tn.edu.tw/trexamps/` | Tainan elementary and pre-K special-ed teacher recruitment | Current 2026 scope | 2026; 1 → 3 | **Covered, current-year scope** | Historical reconstruction is intentionally excluded until a stable official archive is found. |
| `teacher_recruit_taipei_elementary` | `https://www.gov.taipei/News_Content.aspx?n=D0042A87C2F0270A&sms=78D644F2755ACCAA&s=0E5FFDCD602F05C2` | Taipei elementary teacher joint recruitment | Reviewed 114 school year / AD 2025 | 2025; 1 → 12 | **Covered, reviewed current-year scope** | Fixed official article map; city-wide news listing is not treated as an archive. |
| `teacher_recruit_taipei_junior` | `https://www.doe.gov.taipei/News_Content.aspx?n=E831CA0A5CD0193D&sms=78D644F2755ACCAA&s=4A85C1A3A3BD7C48` | Taipei junior-high formal teacher recruitment | Reviewed 2024–2025 | 2024–2025; 2 → 68 | **Covered in reviewed scope** | Fixed official article map; no automatic future-year discovery until a stable endpoint exists. |
| `teacher_recruit_taoyuan_elementary` | `https://elementary.tyc.edu.tw/web/answer.aspx?openExternalBrowser=1` | Taoyuan elementary teacher joint recruitment | Current 2026 scope | 2026; 1 → 21 | **Covered, current-year scope** | Direct question/suggested/final answer files; appeal, score/list, and venue material skipped. |
| `tii_cert` | `https://edu.tii.org.tw/exam/users/exam_intro/1` | Taiwan Insurance Institute certification materials | 2025–2026 observed | 2025–2026; 3 → 5 | **Covered, current-materials scope** | Multiple official exam-intro pages; historical breadth not established. |
| `tocfl_cert` | `https://tocfl.edu.tw/tocfl/index.php/exam/download` | TOCFL reference and official mock-test question/audio/answer/script materials | 2022, 2024, and 2026 resource years observed | 2022–2026, 3 buckets; 3 → 95 | **Covered, reference/mock scope** | This is not a complete archive of every administered TOCFL exam; direct mock downloads are public. |
| `tqc_cert` | `https://www.tqc.org.tw/TQCNet/ExamPaper.aspx` | TQC certification sample-paper archive | 2015–2026 observed | 2015–2026, 11 buckets; 11 → 44 | **Covered in declared sample scope** | Paginated public source; sample papers rather than a complete sitting archive. |
| `twc_recruit` | `https://www.water.gov.tw/ch/Subject/Detail/59619?nodeId=715` | Taiwan Water Corporation recruitment papers | ROC 103–114 / AD 2014–2025, with source-list gaps documented | 2014–2025, 10 buckets; 10 → 10 | **Partial / sparse official archive** | Provider documents missing listing years as source sparsity, not automatically as parser failures. Current-year availability needs re-probe. |
| `wdasec_skill` | `https://owinform.wdasec.gov.tw/ExamNet/owInform/PastQuestions.aspx` | Workforce Development Agency skills-evaluation past questions | Raw sessions 2001–2026; usable paper records 2001–2026 after the 2026-07-28 refresh | raw 2001–2026; papers 2001–2026, 26 buckets; 143 → 10,695 | **Partial / storage and scope blocker** | Official AD 2001–2024 refreshes produced 10,018 records with zero sync failures; policy exclusions remain explicit. Event `201309140001` is now represented as a reviewed blocked empty result with 2026-07-29 evidence in `catalog/source-coverage/wdasec_skill.json`. |

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

## Current gap investigations

### Teacher recruitment

Teacher recruitment remains intentionally partial. The approved source index contains seven implemented recruitment providers plus `teacher_qual`, with many providers deliberately current-year or fixed-article scoped. National opening portals and third-party paper mirrors are not paper sources.

- Central Alliance has three AD 2026 raw events and zero paper records. Official subject/final pages were rechecked on 2026-07-29; all categories are marked `已截止` with no links. They are explicitly blocked, not treated as parser failures.
- Kaohsiung special-education records remain covered locally. The regular and special documented endpoints both returned HTTP 404 on 2026-07-29; only the elementary event is blocked because the special event already has valid local records.
- Expansion to every official county, city, or school recruitment source requires a scope decision and a stable official paper endpoint. No private/third-party replacement is acceptable.

### TOPIK, iCAP, and military recruitment

TOPIK remains blocked pending a stable official direct-download paper archive. iCAP is intentionally outside the exam-paper product unless non-paper competency resources are explicitly approved. Military recruitment remains blocked pending a stable official public historical/sample-paper archive. These are documented candidate decisions, not empty provider placeholders.

### MOEX 2025–2026 and historical failures

The named missing-MOEX symptom is resolved for the current listing: the official discovery snapshot contains 21 AD 2025 codes and 10 AD 2026 codes, with 21/21 and 10/10 local raw events and 6,479/2,820 normalized records. The remaining 35 AD 2025 and 13 AD 2026 one-year groups (339 and 105 records in the prior reconciliation) are excluded by the current multi-year public policy, not by empty code lists. The official listing now covers 35 years and 870 codes; 2017 was recovered with 22 events and 8,581 records, 2019 with 20 events and 8,520 records, 2020 with 21 events and 6,370 records, and 2021 with 22 events and 7,343 records, while 89 historical listed events remain unrepresented locally. Whether to publish single-year groups is a scope/capacity decision.

The historical 5,403 MOEX failure records and 972 review records remain reconciled as follows:

- all 5,403 historical failure keys have current normalized/mirrored counterparts; none is a current mirror failure;
- all 5,403 historical failure events are present in the current 870-event MOEX discovery manifest;
- 5,375 map to current generated public bundle identities and 28 map to valid records whose groups remain excluded by publication policy;
- the 972 historical review rows reduce to 166 semantic keys; 165 are represented by current normalized records and one exact key remains unresolved;
- the current 655-entry queue and 4,379 review-confidence records are broader current populations and must not be counted as complete merely because they are isolated.

The current bounded MOEX refresh recovered 377 valid records from three previously affected events, 261 records from the two newly listed 2026 events, 7,343 records from the newly recovered 2021 year, 6,370 records from the newly recovered 2020 year, 8,520 records from the newly recovered 2019 year, and 8,581 records from the newly recovered 2017 year. It also produced no new failures: the same five exact HTML-placeholder download failures remain. Eight no-result event pages and those five file failures are represented in `catalog/source-coverage/moex.json`; strict audit reports them as blocked/partial rather than silently dropping them.

The one historical semantic key that still intersects the current review queue is `086080` / `專門職業及技術人員土地登記專業`. The retained official event title is `086年特種考試土地登記專業代理人考試、第一次土地登記專業代理人檢覈`; its 11 paper records use category codes `001` and `002`, and the source exposes no separate authoritative level label for those codes. The classifier therefore sees two source-event markers—`特種考試` and `檢覈`—and deliberately keeps both category groups review-isolated. The same collision affects the related 084270 and 085100 land-registration events; 093030 has a different multi-marker conflict. This is a valid ambiguity record, not a parser failure or a missing mirror. Resolving it requires an explicit official mapping from category/code to exam level, or an approved decision to retain event-specific review isolation.

### Hakka and WDASEC

Eight Hakka events are normalized but not published because one official audio ZIP is approximately 2,094,415,387 bytes, beyond the current release/storage target. This needs an approved storage or scope decision.

WDASEC AD 2001–2024 refreshes remain mirrored and normalized with zero sync failures. The AD 2002 event `201309140001` is an official empty result with a retained raw page and a 2026-07-29 evidence capture; it is now a reviewed `blocked` event, not an unresolved normalization gap. The remaining WDASEC policy exclusions continue to be explicit and measurable.

## Prioritized backlog

### P0 — completeness accounting and release safety

1. Complete a provider-scoped manifest or equivalent authoritative discovery snapshot for the remaining 34 active providers, then recover or explicitly block the 89 official MOEX events listed without local state. The reviewed inventory, MOEX discovery writer, and local-state/event-coverage gate are now in place, but they do not replace source recovery.
2. Resolve the eight Hakka normalized-but-not-published events through an approved storage/release or scope decision; do not count local normalization as public coverage.
3. Decide whether the 444 current-year MOEX single-year records should remain outside the public site policy or receive a narrow approved exception.
4. Disposition the one unresolved historical MOEX semantic review key and the broader 655/4,379 current review populations through authoritative mappings or explicitly approved isolation scope.
5. Make aggregate publication, strict history, catalog, release-plan, frontend, and build gates mandatory after provider refresh workflows, not only at deployment; current provider sync workflows commit/publish without these aggregate checks.

### P1 — source and data quality

1. Recheck Central Alliance and Kaohsiung when official pages recover; update the narrow exception entries so repaired material becomes covered.
2. Resolve TCTE ROC 90/91 scope for irregular answer surfaces, or retain the current 404 evidence with a documented cadence.
3. Decide whether identical MOEA/Taipower records are two official families or one canonical owner with aliases.
4. Reconcile stale provider specifications and source year ranges against executable state and manifests.
5. Establish source-family legal/takedown decisions before widening redistribution or release scope.

### P2 — validation surface

1. Add maintained Python line/branch coverage and a practical threshold.
2. Restore frontend dependencies and measure coverage over `frontend/src`, not generated build modules.
3. Add browser smoke tests for search/filter/sort, shared URLs, responsive layout, and real download-link handling.
4. Add accessibility automation for keyboard navigation, focus order/visibility, labels, landmarks, contrast, and axe/WCAG checks.
5. Add an end-to-end release smoke check for sample asset name, checksum, and HTTP response.

### P3 — deferred source decisions

1. Recheck TOPIK only when a stable official direct-download archive appears.
2. Decide separately whether iCAP non-paper resources belong in this product.
3. Recheck official MND military-recruitment surfaces.
4. Expand teacher recruitment only through source-index-approved official archives.

## Measurable completion criteria

Completion requires all of the following for an explicitly approved scope:

1. The source matrix names every discoverable official source, provider owner, category, official URL, available range, local range, legal/technical restriction, and status. Every row is `covered`, `blocked with evidence`, or `intentionally out of scope with a reason`; no row is `unknown`.
2. Every active provider has a current authoritative manifest or equivalent discovery snapshot. The reviewed inventory must match local state, and each event/file can be traced through raw page, eligible source files, mirror checksum, normalized identity, public bundle, and release asset—or to a precise, current blocked/excluded ledger entry.
3. `history-audit --strict` passes with zero `download_gap`, `sync_failure_recorded`, `normalization_gap`, `coverage_exception_conflict`, `coverage_exception_orphan`, `normalized_not_published`, and `parser_gap`. `blocked`, `partially_blocked`, and `excluded_by_publication_policy` are allowed only when backed by current evidence and approved scope.
4. `audit-catalog --strict` passes with no unapproved review records, stale/missing review keys, or unexplained identity splits; every review-confidence record has a documented disposition.
5. Provider state, mirrors, site bundles, frontend feed, release metadata, and actual remote release assets agree exactly for covered records; local generated-manifest agreement alone is insufficient.
6. MOEX current manifests, source events, normalized records, site projection, and release assets reconcile, including an explicit decision on current-year single-year groups.
7. Teacher recruitment and deferred-topic rows satisfy their declared source-index scope and have current recheck evidence for blocked/watch decisions.
8. Every release shard remains below the 900 safety target and every oversized asset has an approved storage path.
9. Python/frontend tests, lint, coverage, browser, accessibility, and release E2E checks are required on pull requests and deployment uses the same green commit.
10. Legal/takedown decisions are recorded for each source family; no credentials or private/third-party source files are used.

## Blockers requiring your decision

- What is the approved content scope: administered papers and answers only, or also sample/practice/reference/audio materials?
- Should valid single-year MOEX groups be public despite the current two-year policy?
- Is Hakka’s oversized official audio releasable through a different approved storage architecture, or should those events be intentionally out of scope?
- Should teacher scope remain the current source index, or expand to every official county/city/school recruitment archive?
- Should Central Alliance and Kaohsiung stay blocked until official pages recover, and what recheck cadence is acceptable?
- Should TCTE ROC 90/91 irregular surfaces count as covered, or only per-subject downloadable paper/answer files?
- Should TOPIK, iCAP, and military recruitment remain blocked/out of scope until direct-download evidence is found?
- What legal basis permits redistributing official PDFs, ZIPs, audio, and answer keys in GitHub releases?
- Should MOEA/Taipower byte-identical records remain separate official categories or share one canonical owner?
- Should the 34 providers without manifests be required to produce current discovery snapshots before any completeness claim?

## Safest branch/release strategy

1. Keep `agent/exam-coverage-and-mirror-dedup` as a local audit/reference branch. Do not rebase it in place; at baseline capture before this cycle it was 7 behind and 52 ahead of fetched `origin/main`, with 47 local commits beyond its tracked upstream.
2. Finish this preparation as one reviewable local commit (or two clearly separated commits: pipeline/audit code and generated MOEX/site state), explicitly excluding pre-existing untracked `PLAN.md`.
3. Create a fresh implementation branch from fetched `origin/main` after review. Port only the source-coverage ledger, strict gate, focused tests, and intentionally selected data changes by review/cherry-pick; do not merge generated state blindly.
4. Implement one provider/source family at a time. Keep source-scope decisions, manifests, generated mirrors, publication changes, and frontend changes reviewable separately.
5. Require the aggregate gates on every provider refresh before treating a change as releasable. Run release upload/deploy only in an approved CI/operator environment after legal and remote-asset checks pass.
6. Do not publish, deploy, prune, delete, reset, rewrite history, or expose credentials from this workspace.
