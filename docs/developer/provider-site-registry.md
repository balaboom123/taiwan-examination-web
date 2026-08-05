# Provider And Site Registry

This document is the human-readable ownership registry for active and planned providers and sites.

Update this file whenever a provider or site is added, renamed, deprecated, or materially re-scoped.

## Registry Rules

- Every provider MUST have one registry entry.
- Every site MUST have one registry entry.
- Provider IDs and site IDs MUST be stable.
- A provider registry entry MUST identify its owning sync workflow.
- A site registry entry MUST identify its owning release and deploy workflows.

## Active Providers

### Provider: `moex`

| Field | Value |
| --- | --- |
| provider_id | `moex` |
| status | active |
| source name | Ministry of Examination exam archive source |
| source type | public web source |
| current implementation scope | single active provider in repo |
| current raw data ownership | root-level `data/exams/`, `data/papers/`, `data/review-queue.json`, `data/sync-failures.json`, `data/source-manifest.json` |
| target scoped ownership | `data/providers/moex/` |
| current mirror ownership | `mirror/` |
| target mirror ownership | `mirror/providers/moex/` |
| current sync workflows | `sync-incremental.yml`, `sync-full.yml`, `audit-recent.yml`, `discover.yml` |
| current CLI entrypoints | `discover`, `probe-latest`, `sync-targeted`, `sync-incremental`, `sync-full` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | current provider used as migration baseline |

### Provider: `teacher_recruit_tainan`

| Field | Value |
| --- | --- |
| provider_id | `teacher_recruit_tainan` |
| status | active |
| source name | 臺南市國小教師甄選網 |
| source type | public web source |
| current implementation scope | current-year 教師甄試 provider for Tainan elementary and pre-K special-ed recruitment papers |
| current raw data ownership | `data/providers/teacher_recruit_tainan/` |
| current mirror ownership | `mirror/providers/teacher_recruit_tainan/` |
| current sync workflows | `sync-teacher-recruit-tainan.yml` |
| current CLI entrypoints | `sync-full --provider teacher_recruit_tainan --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes one canonical bundle asset, `teacher-recruit-tainan`; public publication remains site-owned |

### Provider: `teacher_recruit_taipei_junior`

| Field | Value |
| --- | --- |
| provider_id | `teacher_recruit_taipei_junior` |
| status | active |
| source name | 臺北市政府教育局國中教師聯合甄選公告 |
| source type | public web source |
| current implementation scope | Taipei junior-high formal teacher recruitment question and answer PDFs from reviewed DOE article pages |
| current raw data ownership | `data/providers/teacher_recruit_taipei_junior/` |
| current mirror ownership | `mirror/providers/teacher_recruit_taipei_junior/` |
| current sync workflows | `sync-teacher-recruit-taipei-junior.yml` |
| current CLI entrypoints | `sync-full --provider teacher_recruit_taipei_junior --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes one canonical bundle asset, `teacher-recruit-taipei-junior`; public publication remains site-owned |

### Provider: `gept_cert`

| Field | Value |
| --- | --- |
| provider_id | `gept_cert` |
| status | implemented; source audit partial and retained/public identity migration required |
| source name | GEPT 全民英檢 official practice materials (LTTC) |
| source type | five current public level pages plus a removed historical pretest listing |
| current implementation scope | five source-year 2022 level events with 34 listed records/32 unique URLs; the removed July 2009 pretest index separately listed 108 entries |
| current raw data ownership | `data/providers/gept_cert/` |
| current mirror ownership | `mirror/providers/gept_cert/` |
| current sync workflows | `sync-gept-cert.yml` exists but must stay off releasable branches pending identity, payload, historical-scope, and legal decisions |
| current CLI entrypoints | `sync-full --provider gept_cert --site-id default` |
| operator docs | `docs/developer/providers/gept_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | all 34 current public records use a synthetic 2026 event/year, three point at wrong bytes after label collisions, the historical listing is removed, and LTTC redistribution authority is unresolved |

### Provider: `jlpt_cert`

| Field | Value |
| --- | --- |
| provider_id | `jlpt_cert` |
| status | implemented; declared 2012/2018 workbook scope complete, release blocked |
| source name | JLPT Official Practice Workbook materials |
| source type | official two-section sample-workbook page |
| current implementation scope | 2012 and 2018 workbook PDFs/MP3s; 2 events, 116 unique URLs |
| current raw data ownership | `data/providers/jlpt_cert/` |
| current mirror ownership | `mirror/providers/jlpt_cert/` |
| current sync workflows | `sync-jlpt-cert.yml` must remain off releasable branches pending rights review |
| current CLI entrypoints | `sync-full --provider jlpt_cert --site-id default` |
| operator docs | `docs/developer/providers/jlpt_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | exact URL agreement is limited to the official workbook denominator; third-party N1/N2 text and all listening audio have separate restrictions, and no blanket republication grant is recorded |

### Provider: `tocfl_cert`

| Field | Value |
| --- | --- |
| provider_id | `tocfl_cert` |
| status | implemented; source audit partial and identity migration required |
| source name | TOCFL 華語文能力測驗 official reference and rolling mock-bank downloads |
| source type | official reference page plus rolling 2,138-question mock-bank page |
| current implementation scope | 3 filename-dated reference assets and 92 rolling-bank assets; all 95 URLs retained |
| current raw data ownership | `data/providers/tocfl_cert/` |
| current mirror ownership | `mirror/providers/tocfl_cert/` |
| current sync workflows | `sync-tocfl-cert.yml` must remain off releasable branches pending identity and rights decisions |
| current CLI entrypoints | `sync-full --provider tocfl_cert --site-id default` |
| operator docs | `docs/developer/providers/tocfl_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | the adapter assigns synthetic AD 2026 identity to 92 assets from a rolling bank last declared updated in October 2025; copyright permits learning/non-commercial use but no blanket GitHub republication grant is recorded |

### Provider: `hakka_cert`

| Field | Value |
| --- | --- |
| provider_id | `hakka_cert` |
| status | active |
| source name | 客語能力認證 official materials (客家委員會) |
| source type | public web source |
| current implementation scope | question banks, sample tests, answers, and paired question audio across bounded primary pages; vocabulary-only materials are intentionally excluded, while the separate official download center remains unintegrated |
| current raw data ownership | `data/providers/hakka_cert/` |
| current mirror ownership | `mirror/providers/hakka_cert/` |
| current sync workflows | `sync-hakka-cert.yml` |
| current CLI entrypoints | `sync-full --provider hakka_cert --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes one canonical bundle per official level category (`hakka-cert-basic-elementary`, `hakka-cert-intermediate-high-intermediate`, `hakka-cert-advanced`); public publication remains site-owned |

### Provider: `taigi_cert`

| Field | Value |
| --- | --- |
| provider_id | `taigi_cert` |
| status | implemented; source audit partial, refresh policy-blocked, identity migration required |
| source name | 臺灣台語語言能力認證 official materials (教育部) |
| source type | official undated self-learning resource page with restrictive robots policy |
| current implementation scope | 35 A/B/C sample assets; 2 general learning PDFs explicitly excluded as non-exam resources |
| current raw data ownership | `data/providers/taigi_cert/` |
| current mirror ownership | `mirror/providers/taigi_cert/` |
| current sync workflows | `sync-taigi-cert.yml` must remain disabled pending written permission or robots-policy change |
| current CLI entrypoints | `sync-full --provider taigi_cert --site-id default` |
| operator docs | `docs/developer/providers/taigi_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | all 35 records use unsupported synthetic 2026 identity, and the public A-form bundle merges A/B/C taxonomy; `/tmt/src/` mirroring and redistribution require approval |

### Provider: `tqc_cert`

| Field | Value |
| --- | --- |
| provider_id | `tqc_cert` |
| status | implemented; source audit partial and payload migration required |
| source name | TQC official sample-paper listing |
| source type | four-page official ASP.NET listing |
| current implementation scope | 44 sample PDFs across 11 publication years; TQC+ remains a separate unapproved family |
| current raw data ownership | `data/providers/tqc_cert/` |
| current mirror ownership | `mirror/providers/tqc_cert/` |
| current sync workflows | `sync-tqc-cert.yml` must remain off releasable branches pending payload and rights decisions |
| current CLI entrypoints | `sync-full --provider tqc_cert --site-id default` |
| operator docs | `docs/developer/providers/tqc_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | all 44 URLs are represented, but nine public records point at wrong bytes after generic-label storage collisions; no sample-paper republication grant is recorded |

### Provider: `ipas_cert`

| Field | Value |
| --- | --- |
| provider_id | `ipas_cert` |
| status | implemented; source audit partial and scope/role migration required |
| source name | iPAS official certification-family downloads |
| source type | current official home page and 16 certification-family sections |
| current implementation scope | only AIAP, AIOT, ISE, and OIA; 62 PDFs under synthetic current-year events |
| current raw data ownership | `data/providers/ipas_cert/` |
| current mirror ownership | `mirror/providers/ipas_cert/` |
| current sync workflows | `sync-ipas-cert.yml` must remain off releasable branches pending scope, role, identity, and rights decisions |
| current CLI entrypoints | `sync-full --provider ipas_cert --site-id default` |
| operator docs | `docs/developer/providers/ipas_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | 12 of 16 official families and 34 paper-like PDFs are omitted, while 46 retained non-paper PDFs are labeled as questions; no blanket republication grant is recorded |

## Planned Providers

Add planned providers here before implementation starts.

### Provider: `ceec_gsat`

| Field | Value |
| --- | --- |
| provider_id | `ceec_gsat` |
| status | planned |
| source name | College Entrance Examination Center GSAT archive |
| source type | public web source |
| current implementation scope | planned same-site provider feeding the existing public catalog |
| target scoped ownership | `data/providers/ceec_gsat/` |
| target mirror ownership | `mirror/providers/ceec_gsat/` |
| planned sync workflows | provider-scoped CEEC sync workflow to be added during migration |
| planned CLI entrypoints | provider-aware sync entrypoint targeting `ceec_gsat` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes exactly one canonical bundle asset for `學科能力測驗`; public publication remains site-owned |

### Provider: `sfi_cert`

| Field | Value |
| --- | --- |
| provider_id | `sfi_cert` |
| status | implemented; source audit partial and retained/public identity migration required |
| source name | Securities & Futures Institute certification exam archive |
| source type | public rolling web source |
| current implementation scope | all question/selected-answer rows on the rolling official page; row labels and PDF headings define category/year/round |
| target scoped ownership | `data/providers/sfi_cert/` |
| target mirror ownership | `mirror/providers/sfi_cert/` |
| planned sync workflows | `sync-sfi-cert.yml` exists but must stay off releasable branches until identity migration and aggregate gates pass |
| planned CLI entrypoints | `sync-full --provider sfi_cert --site-id default` |
| operator docs | `docs/developer/providers/sfi_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | exact current source is 25 events/50 PDFs; all 30 retained/public files match source bytes but are attached to wrong identities, 20 URLs are not retained, and redistribution authority is unresolved |

### Provider: `tabf_cert`

| Field | Value |
| --- | --- |
| provider_id | `tabf_cert` |
| status | implemented; source audit partial and retained/public identity migration required |
| source name | Taiwan Academy of Banking and Finance certification exam archive |
| source type | public rolling web source with an explicit FIT reference exception |
| current implementation scope | all 19 PHID category rows and 127 PDFs on the current official page; containing row and date evidence define category/year |
| target scoped ownership | `data/providers/tabf_cert/` |
| target mirror ownership | `mirror/providers/tabf_cert/` |
| planned sync workflows | `sync-tabf-cert.yml` exists but must stay off releasable branches pending identity, robots-policy, and legal decisions |
| planned CLI entrypoints | `sync-full --provider tabf_cert --site-id default` |
| operator docs | `docs/developer/providers/tabf_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | exact source is 50 events/127 PDFs; 47 PHIDs are duplicated across local years, 211 public records are wrong or stale, PHID 431 is missing, PHIDs 449/456 are stale, and the asset robots policy disallows `/BEExam` |

### Provider: `tii_cert`

| Field | Value |
| --- | --- |
| provider_id | `tii_cert` |
| status | implemented; source audit partial, transport blocked, and retained/public content migration required |
| source name | Taiwan Insurance Institute certification exam archive |
| source type | public message-page listings plus a separate AML download-center history ZIP |
| current implementation scope | three paper-listing families with 10 current events/24 listed files across 2024–2026; all other official exam families require explicit source dispositions |
| target scoped ownership | `data/providers/tii_cert/` |
| target mirror ownership | `mirror/providers/tii_cert/` |
| planned sync workflows | `sync-tii-cert.yml` exists but must stay off releasable branches pending certificate-valid discovery, content migration, and legal decisions |
| planned CLI entrypoints | `sync-full --provider tii_cert --site-id default` |
| operator docs | `docs/developer/providers/tii_cert-spec.md`, `docs/operator/runbook.md`, `docs/operator/recovery.md` |
| notes | four listed papers are retained correctly, 20 are absent, one brochure is published as a question, the AML history ZIP is unresolved, and normal TLS verification fails without an issuer certificate |

Recommended entry format:

### Provider: `<provider_id>`

| Field | Value |
| --- | --- |
| provider_id | `<provider_id>` |
| status | planned |
| source name | |
| source type | |
| current implementation scope | |
| target scoped ownership | `data/providers/<provider_id>/` |
| target mirror ownership | `mirror/providers/<provider_id>/` |
| planned sync workflows | |
| planned CLI entrypoints | |
| operator docs | |
| notes | |

## Active Sites

### Site: `default`

| Field | Value |
| --- | --- |
| site_id | `default` |
| status | active |
| purpose | current public exam bundle catalog |
| input providers | all 35 in `app/site_registry.py`: `moex`, `ceec_gsat`, `ceec_ast`, `tcte_tve`, `special_admission`, `post_recruit`, `hce_cmu`, `hce_tcu`, `hce_nsysu`, `hce_nthu`, `cpc_recruit`, `moea_recruit`, `taipower_recruit`, `taisugar_recruit`, `twc_recruit`, `rcpet_cap`, `wdasec_skill`, `sfi_cert`, `tabf_cert`, `tii_cert`, `teacher_qual`, `teacher_recruit_newtaipei`, `teacher_recruit_taoyuan_elementary`, `teacher_recruit_kaohsiung`, `teacher_recruit_central_alliance`, `teacher_recruit_taipei_junior`, `teacher_recruit_taipei_elementary`, `teacher_recruit_tainan`, `gept_cert`, `jlpt_cert`, `tocfl_cert`, `hakka_cert`, `taigi_cert`, `tqc_cert`, `ipas_cert` |
| publication ownership | `data/sites/default/` (`bundles.json`, `frontend-bundles.json`, `release-assets.json`) |
| bundle storage | `bundles/sites/default/` |
| release tags | `default-bundles-v2-001` … `default-bundles-v2-013`, sharded at 900 assets against GitHub's 1,000-asset ceiling |
| retired release tags | `moex-bundles`, `default-bundles-001`, `default-bundles-002` — no longer referenced by any site catalog; their assets remain published for older links |
| deploy workflows | `deploy-pages.yml`, triggered by a push, by any data-writing workflow completing, and by a daily backstop schedule |
| publish ownership | sync workflows plus `.github/scripts/release_assets.py` |
| frontend surface | `frontend/` |
| legacy output surface | none |
| download gate | frontend LINE social gate |
| notes | the site-scoped cutover and the v2 identity renaming are both complete; asset names are derived from bundle identity and are stable across rebuilds, so publication compares checksums rather than names |

## Planned Sites

Add planned sites here before implementation starts.

Recommended entry format:

### Site: `<site_id>`

| Field | Value |
| --- | --- |
| site_id | `<site_id>` |
| status | planned |
| purpose | |
| input providers | |
| target scoped ownership | `data/sites/<site_id>/` |
| target bundle storage | `bundles/sites/<site_id>/` |
| release tag | |
| deploy workflows | |
| publish ownership | |
| frontend surface | |
| download gate | |
| notes | |

## Secret And Integration Registry

Current shared integrations:

| Integration | Current owner | Purpose |
| --- | --- | --- |
| GitHub release token via `GH_TOKEN` | site publication workflows | upload/prune bundle assets |

Future rule:

- secrets SHOULD be documented per site or provider owner instead of assumed global whenever different sites/providers have different credentials or integrations

## Change Control Checklist

When updating this registry, also update:

- `docs/developer/contracts.md` if a contract owner changes
- `docs/developer/migration-plan.md` if the cutover sequence changes
- `docs/developer/source-onboarding.md` if onboarding rules change
- operator docs if workflow ownership or trigger paths change
