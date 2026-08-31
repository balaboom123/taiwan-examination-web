# Provider Spec: `tabf_cert`

## Summary

- `provider_id`: `tabf_cert`
- status: implemented; bounded current-source discovery captured, retained/public identity contaminated
- target site: `default`
- canonical archive: `https://www.tabf.org.tw/LicenseHistoryExam.aspx`
- machine-readable evidence: `data/providers/tabf_cert/source-manifest.json`
- publication shape: eight generated financial-certification bundles, currently unsafe because date and taxonomy errors affect 211 records

This audit is evidence-only. It does not change the adapter, retained state, mirrors, generated bundles, frontend feed, releases, or deployment.

## Authoritative source boundary

TABF states that its history page provides only the most recent three written-test editions for reference. The bounded 2026-08-01 capture contains 19 official category rows, 50 PHID events, and 127 public PDFs totaling 58,493,699 bytes. All 127 returned HTTP 200 with PDF signatures.

FIT is an explicit exception rather than a rolling three-edition archive. TABF says it stopped publishing FIT questions and answers from edition 3 and intentionally retains editions 1 and 2. Those eight subject-edition events date to 2020. The remaining current page spans 2023–2026: one advanced-credit event each in 2023 and 2024, 28 events in 2025, and 12 events in 2026.

The page also delegates `金融市場常識與職業道德` downloads to SFI. That external family is not duplicated under `tabf_cert`.

| Official category | Current PHIDs | Correct identity |
| --- | --- | --- |
| 初階授信 | `421`, `444`, `448` | `credit-junior` |
| 進階授信 | `381`, `412`, `445` | `credit-senior` |
| 初階外匯 | `428`, `436`, `461` | `fx-junior` |
| 理財規劃 | `420`, `437`, `450` | `financial-planning` |
| 信託業務 | `424`, `430`, `457` | `trust-business` |
| 銀行內控（一般金融） | `419`, `441`, `454` | `bank-internal-control-general` |
| 銀行內控（消費金融） | `422`, `443`, `455` | `bank-internal-control-consumer` |
| 信託法規乙科 | `425`, `432`, `458` | `trust-law-single-subject` |
| 家族信託規劃顧問師 | `416`, `433`, `446` | `family-trust-advisor` |
| 風險管理 | `429`, `435`, `460` | `risk-management` |
| 衍生性金融商品銷售 | `427`, `438`, `462` | `derivatives-sales` |
| 金融科技力 | `418`, `434`, `447` | `fintech` |
| 防制洗錢與打擊資恐 | `423` | `aml` |
| 高齡金融規劃顧問師 | `426`, `440`, `459` | `senior-financial-planning-advisor` |
| 永續發展基礎能力 | `431`, `439` | `sustainability` |
| FIT 考科 I–IV | `274`–`281` | four distinct `fit-subject-*` tracks |

## Retained, normalized, and public state

Local state remains 99 raw pages, 98 unique event IDs, 252 normalized records, 129 unique source URLs, 252 checksum-valid mirrors, zero sync failures, and eight generated/public bundles.

Current-source byte reconciliation is strong but identity reconciliation is not:

- 125 of 127 current official URLs are retained and every overlapping live checksum matches a local mirror;
- PHID `431` contributes the two source-only current PDFs;
- four local-only URLs belong to stale PHIDs `449` and `456`; the duplicated PHID `456` raw page makes those four URLs six normalized records;
- 47 PHIDs and their URLs are duplicated across both 2025 and 2026;
- only 16 of 50 corrected official event IDs overlap local event IDs;
- 41 current file records use the correct event identity, while 205 current local references use a wrong year or category and six more records are stale/local-only;
- file-level source status is 2 source-only, 2 retained only under correct identity, 39 retained under both correct and duplicate wrong identity, and 84 retained only under wrong identity;
- all 252 normalized records are projected into eight site/frontend/release bundles, so 211 wrong or stale records are publicly represented.

Generated-manifest agreement does not detect the defect because raw pages, normalized records, bundles, frontend metadata, and release metadata all inherited the same adapter output.

## Root cause and fail-closed discovery contract

The current adapter extracts anchor text and PHID but discards the containing official category row. Most anchors contain only an edition number, not a year. The adapter substitutes the caller-supplied year, so repeated runs assigned the same PHID to 2025 and 2026. It then guesses category from subject labels; only 6 of 19 official rows survive that classification exactly. Initial/advanced credit, both bank-internal-control variants, trust-law-only, family trust, derivatives, high-age planning, sustainability, and all FIT subjects are flattened or misclassified.

A corrected adapter must:

1. parse the containing official table row and preserve all 19 reviewed category identities;
2. snapshot PHID, row, edition label, source date evidence, and PDF URL together;
3. reject unknown/duplicate rows, PHIDs, URLs, and unreviewed category growth;
4. derive event year from explicit ROC labels or validated PDF/HTTP date evidence, never the caller's current year;
5. preserve the FIT editions 1–2 exception and reject any assumption that FIT is a current-year event;
6. detect rolling-window additions/removals without silently deleting retained evidence; and
7. stop before download while the asset host's robots policy disallows `/BEExam`, unless an approved policy interpretation or written permission is recorded.

## Safe migration sequence

1. Keep the provider-only scheduled refresh off releasable branches.
2. Preserve this manifest, the 99 raw pages, 252 normalized records, mirror checksums, and generated bundle checksums as audit evidence.
3. Implement and test a row-aware, date-aware discovery parser without overwriting retained state.
4. Generate corrected provider state in an isolated staging location and compare all 127 current source files against the 125 matching mirrors.
5. Review 34 source-only and 82 local-only event identities, including stale PHIDs `449` and `456`, then migrate or quarantine the 211 wrong/stale published records atomically through raw, normalized, bundle, frontend, and release projections.
6. Do not fetch further assets or republish until robots-policy and redistribution decisions are approved.
7. Run focused tests plus aggregate source-inventory, strict catalog/history, publication, release-plan, frontend, and production-build gates.

No mirror deletion, history rewrite, release upload, or deployment is authorized by this spec.

## Legal and technical restrictions

The official page offers PDFs for reference and explains how to download them, but no exam-PDF republication license was found. TABF pages display an all-rights-reserved footer, and the site agreement contains no redistribution grant. Download availability is not treated as permission to publish copies in GitHub releases.

`https://www.tabf.org.tw/robots.txt` returns HTTP 200 text with wildcard `Allow: /`. The distinct asset host policy at `https://service.tabf.org.tw/robots.txt` returns HTTP 200 text whose wildcard rules disallow `/BEExam`, the path containing every accepted PDF. Automated mirroring is therefore blocked pending an approved policy interpretation or written permission.

## Completion conditions

TABF is complete only when:

- all 19 official category rows, 50 current PHID events, and 127 current files are represented or explicitly blocked/excluded;
- event years and editions are evidence-derived, and no PHID is duplicated into a synthetic year;
- all category variants and four FIT subjects remain distinct;
- the 34 source-only and 82 local-only event identities have reviewed dispositions;
- no wrong-year, wrong-category, duplicate, or stale TABF record remains in retained state, bundles, frontend metadata, or release metadata;
- rolling-window changes fail closed and refresh evidence;
- robots-policy and legal/takedown approval exists for any automated fetch or public redistribution; and
- aggregate release gates pass on the same commit.
