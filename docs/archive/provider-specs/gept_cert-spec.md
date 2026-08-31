# Provider Spec: `gept_cert`

## Summary

- `provider_id`: `gept_cert`
- status: implemented; source audit partial and retained/public migration required
- target site: `default`
- source family: GEPT 全民英檢 official practice/material pages
- source domain: `www.gept.org.tw`

## Declared Source Boundary

The current source denominator is every direct PDF/ZIP link and every MP3 reached through `playAudio` on the five official level-introduction pages:

- 初級: `https://www.gept.org.tw/Exam_Intro/t01_introduction.asp`
- 中級: `https://www.gept.org.tw/Exam_Intro/t02_introduction.asp`
- 中高級: `https://www.gept.org.tw/Exam_Intro/t03_introduction.asp`
- 高級: `https://www.gept.org.tw/Exam_Intro/t04_introduction.asp`
- 優級: `https://www.gept.org.tw/Exam_Intro/t05_introduction.asp`

As checked on 2026-08-01, these pages expose five 2022 level events and 34 listing records: 12 direct PDF/ZIP records and 22 listening-audio records. Two software/reference URLs appear under both middle levels, so the denominator contains 32 unique URLs totaling 183,174,255 bytes. All 32 returned HTTP 200 with standard TLS verification.

The separate historical pretest index at `Exam_Intro/download.asp` was dated July 2009 and listed 108 entries across five level pages. The index and all five level pages now return the same IIS 404 page. Official search-index evidence preserves the listing labels, but a complete live direct-asset denominator cannot currently be reconstructed. The current 34-record scope therefore is not historical completeness. Browser-only iPrep exercises are outside this direct-download archive boundary.

## Source and Output Model

The executable adapter now models one event per level and derives source year 2022 from the material URLs:

- `gept-cert-elementary-2022`
- `gept-cert-intermediate-2022`
- `gept-cert-high-intermediate-2022`
- `gept-cert-advanced-2022`
- `gept-cert-superior-2022`

Direct PDF/ZIP links currently map to `question`; practice-page MP3s map to `listening_audio`. The direct-link role is intentionally marked for review because the source includes writing samples, speaking instructions, practice software, and installation documentation rather than only questions.

Provider state belongs under `data/providers/gept_cert/`, mirrors under `mirror/providers/gept_cert/`, and the existing workflow is `.github/workflows/sync-gept-cert.yml`.

## Reconciliation Baseline

Retained state is stale: it contains one synthetic `gept-cert-materials` event in AD 2026 / ROC 115 with 34 normalized and published records. All 34 therefore use the wrong event/year relative to the source.

Thirty-one records retain the current live bytes. Three records use the wrong bytes because repeated generic labels collapsed distinct URLs onto one storage key:

- intermediate composition points at intermediate translation;
- high-intermediate composition points at high-intermediate translation;
- superior speaking points at superior writing.

The mirror preserves 68 files totaling 715,025,582 bytes. Only 31 storage keys are referenced by current state. The 37 unreferenced files total 357,922,707 bytes and include all 34 source-correct ROC 111 per-level mirrors plus the three distinct ROC 115 files lost by collisions. They are migration evidence and must not be pruned before reviewed reconciliation.

Raw, normalized, bundle, frontend, and release metadata agreement is not evidence of correctness here because every generated layer inherited the same synthetic 2026 identity and collision-prone keys.

## Legal and Technical Restrictions

The removed 2009 page stated that the Ministry of Education authorized publication and allowed unlimited free non-profit download. That wording does not clearly grant republication. Current LTTC terms at `https://www.lttc.ntu.edu.tw/tw/disclaimer` prohibit reproduction, reposting, distribution, alteration, broadcasting, or publication without consent or authorization. Redistribution therefore requires an operator/legal decision.

`https://www.gept.org.tw/robots.txt` returns the same 404 HTML rather than a usable robots policy; this is unknown, not an allow. No access control or TLS check was bypassed.

## Safe Migration Plan

1. Preserve the current retained/public snapshot and all 68 mirror files as audit evidence.
2. Use collision-proof subject identities derived from URL or source position, and review direct-link document roles.
3. Migrate to the five source-derived 2022 event identities and verify every file against the source manifest.
4. Reconcile the removed 108-entry historical archive through an official restored index, written source assistance, or a current evidence-backed blocker; do not infer historical completeness from the current pages.
5. Keep GEPT refresh/republication off releasable branches until identity, payload, historical-scope, and legal decisions are complete and aggregate gates pass.
