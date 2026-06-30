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
| status | active |
| source name | GEPT 全民英檢 official practice materials (LTTC) |
| source type | public web source |
| current implementation scope | official GEPT practice PDFs, ZIPs, and listening MP3s across five proficiency levels |
| current raw data ownership | `data/providers/gept_cert/` |
| current mirror ownership | `mirror/providers/gept_cert/` |
| current sync workflows | `sync-gept-cert.yml` |
| current CLI entrypoints | `sync-full --provider gept_cert --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes one canonical bundle `gept-cert`; public publication remains site-owned |

### Provider: `tocfl_cert`

| Field | Value |
| --- | --- |
| provider_id | `tocfl_cert` |
| status | active |
| source name | TOCFL 華語文能力測驗 official reference downloads |
| source type | public web source |
| current implementation scope | official TOCFL downloadable reference materials from tocfl.edu.tw |
| current raw data ownership | `data/providers/tocfl_cert/` |
| current mirror ownership | `mirror/providers/tocfl_cert/` |
| current sync workflows | `sync-tocfl-cert.yml` |
| current CLI entrypoints | `sync-full --provider tocfl_cert --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes one canonical bundle `tocfl-cert`; public publication remains site-owned |

### Provider: `hakka_cert`

| Field | Value |
| --- | --- |
| provider_id | `hakka_cert` |
| status | active |
| source name | 客語能力認證 official materials (客家委員會) |
| source type | public web source |
| current implementation scope | official Hakka certification vocabulary PDFs and question bank PDFs; audio ZIPs excluded until language bundles can be sharded |
| current raw data ownership | `data/providers/hakka_cert/` |
| current mirror ownership | `mirror/providers/hakka_cert/` |
| current sync workflows | `sync-hakka-cert.yml` |
| current CLI entrypoints | `sync-full --provider hakka_cert --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes one canonical bundle `hakka-cert`; public publication remains site-owned |

### Provider: `taigi_cert`

| Field | Value |
| --- | --- |
| provider_id | `taigi_cert` |
| status | active |
| source name | 臺灣台語語言能力認證 official materials (教育部) |
| source type | public web source |
| current implementation scope | official Taiwan Taiwanese certification sample exam PDFs, MP3s, and ZIPs |
| current raw data ownership | `data/providers/taigi_cert/` |
| current mirror ownership | `mirror/providers/taigi_cert/` |
| current sync workflows | `sync-taigi-cert.yml` |
| current CLI entrypoints | `sync-full --provider taigi_cert --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes one canonical bundle `taigi-cert`; public publication remains site-owned |

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
| status | planned |
| source name | Securities & Futures Institute certification exam archive |
| source type | public web source |
| current implementation scope | planned multi-bundle provider for securities and futures certifications |
| target scoped ownership | `data/providers/sfi_cert/` |
| target mirror ownership | `mirror/providers/sfi_cert/` |
| planned sync workflows | `sync-sfi-cert.yml` |
| planned CLI entrypoints | `sync-full --provider sfi_cert --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes ~10 canonical bundle assets (one per certification type); public publication remains site-owned |

### Provider: `tabf_cert`

| Field | Value |
| --- | --- |
| provider_id | `tabf_cert` |
| status | planned |
| source name | Taiwan Academy of Banking and Finance certification exam archive |
| source type | public web source |
| current implementation scope | planned multi-bundle provider for banking and finance certifications |
| target scoped ownership | `data/providers/tabf_cert/` |
| target mirror ownership | `mirror/providers/tabf_cert/` |
| planned sync workflows | `sync-tabf-cert.yml` |
| planned CLI entrypoints | `sync-full --provider tabf_cert --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes ~12 canonical bundle assets (one per certification type); public publication remains site-owned |

### Provider: `tii_cert`

| Field | Value |
| --- | --- |
| provider_id | `tii_cert` |
| status | planned |
| source name | Taiwan Insurance Institute certification exam archive |
| source type | public web source |
| current implementation scope | planned multi-bundle provider for insurance certifications |
| target scoped ownership | `data/providers/tii_cert/` |
| target mirror ownership | `mirror/providers/tii_cert/` |
| planned sync workflows | `sync-tii-cert.yml` |
| planned CLI entrypoints | `sync-full --provider tii_cert --site-id default` |
| operator docs | `docs/operator/runbook.md`, `docs/operator/recovery.md` after onboarding |
| notes | contributes ~4 canonical bundle assets (one per certification type); public publication remains site-owned |

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
| current input providers | `moex` |
| target input providers | `moex`, `ceec_gsat`, `cpc_recruit`, `moea_recruit`, `taipower_recruit`, `taisugar_recruit`, `twc_recruit`, `rcpet_cap`, `wdasec_skill`, `sfi_cert`, `tabf_cert`, `tii_cert`, `teacher_qual`, `teacher_recruit_taipei_junior`, `teacher_recruit_tainan`, `gept_cert`, `tocfl_cert`, `hakka_cert`, `taigi_cert`, `tqc_cert`, `ipas_cert` |
| current publication ownership | root-level `data/bundles.json`, `data/release-assets.json`, `data/lootlabs-links.json` |
| target scoped ownership | `data/sites/default/` |
| current bundle storage | `bundles/` |
| target bundle storage | `bundles/sites/default/` |
| current release tag | `moex-bundles` |
| target release strategy | site-owned publication; one or more release tags; shard before 900 assets |
| current deploy workflows | `deploy-pages.yml` |
| current publish ownership | sync workflows plus `.github/scripts/release_assets.py` |
| current frontend surface | `frontend/` |
| legacy output surface | none |
| gating provider | LootLabs, optional by build/deploy path |
| notes | current site still uses MOEX-shaped naming, needs site-scoped cutover, and will eventually absorb one CEEC bundle asset without splitting the public site |

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
| gating provider | |
| notes | |

## Secret And Integration Registry

Current shared integrations:

| Integration | Current owner | Purpose |
| --- | --- | --- |
| GitHub release token via `GH_TOKEN` | site publication workflows | upload/prune bundle assets |
| `LOOTLABS_API_KEY` | current default site | content-locker link generation |

Future rule:

- secrets SHOULD be documented per site or provider owner instead of assumed global whenever different sites/providers have different credentials or integrations

## Change Control Checklist

When updating this registry, also update:

- `docs/developer/contracts.md` if a contract owner changes
- `docs/developer/migration-plan.md` if the cutover sequence changes
- `docs/developer/source-onboarding.md` if onboarding rules change
- operator docs if workflow ownership or trigger paths change
