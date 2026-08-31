# Provider Spec: `taipower_recruit`

## Summary

- `provider_id`: `taipower_recruit`
- status: partial; event discovery is represented, retained assets are incomplete
- target site: `default`
- source family: Taiwan Power Company company-specific new-hire/training-class recruitment papers
- canonical source: `https://www.taipower.com.tw/2289/2544/2554/2557/`
- publication shape: one canonical site-owned bundle

## Source Boundary

Taipower's company-specific 新進僱用人員／養成班 exam is distinct from the Ministry of Economic Affairs joint 新進職員 exam:

- `/2289/2544/2554/2557/` is owned by `taipower_recruit`;
- `/2289/2544/2554/2556/` is owned by `moea_recruit`;
- `https://www.taipower.com.tw/tc/download.aspx?mid=262` is not authoritative because its observed redirect now lands on `/2556/`.

The two providers must not be treated as aliases. The current `moea_recruit` state is an erroneous duplicate of Taipower hiring material; the Taipower ownership is supported by the `/2557/` navigation label, source titles, PDF first-page text, and provider-specific source URLs.

## Official Event Inventory

The latest indexed official HTML exposes 23 event tabs across 22 Gregorian years. ROC 107 has separate May and December sessions.

| Official tab | AD | `q_attribute` | Retained asset records |
| --- | ---: | ---: | ---: |
| ROC 115 | 2026 | 4262 | 20 |
| ROC 114 | 2025 | 4259 | 20 |
| ROC 113 | 2024 | 4256 | 20 |
| ROC 112 | 2023 | 4255 | 20 |
| ROC 111 | 2022 | 4185 | 20 |
| ROC 110 | 2021 | 4071 | 20 |
| ROC 109 | 2020 | 2970 | 20 |
| ROC 108 | 2019 | 2700 | 20 |
| ROC 107 December | 2018 | 2659 | 0 |
| ROC 107 May | 2018 | 1611 | 0 |
| ROC 106 | 2017 | 457 | 20 |
| ROC 105 | 2016 | 458 | 20 |
| ROC 104 | 2015 | 459 | 20 |
| ROC 103 | 2014 | 460 | 20 |
| ROC 102 | 2013 | 461 | 20 |
| ROC 101 | 2012 | 462 | 20 |
| ROC 99 | 2010 | 464 | 20 |
| ROC 97 | 2008 | 466 | 20 |
| ROC 96 | 2007 | 467 | 20 |
| ROC 95 | 2006 | 468 | 14 |
| ROC 94 | 2005 | 469 | 5 |
| ROC 92 | 2003 | 471 | 4 |
| ROC 90 | 2001 | 473 | 7 |

An older unfiltered official index, before ROC 115 appeared, reported exactly 301 subject groups over 31 default-size pages. Indexed filtered pages report 17 groups for ROC 110, 14 for ROC 111, and 15 each for ROC 112 and 113. Retained state has only 20 asset records for each of those events because the old adapter fetched the default first ten groups and did not follow or reject pagination. The two ROC 107 tabs were also invisible to its `年度`-only regular expression.

These observations prove incompleteness, but they do not establish a current exact total: the latest live host cannot presently be enumerated from this environment. `data/providers/taipower_recruit/source-manifest.json` therefore has `files = {}` and partial coverage. It must not be promoted to complete from event-tab agreement alone.

## Current Access Restriction

On 2026-07-31:

- canonical, `simpleList`, legacy-entrypoint, and sample retained PDF requests returned HTTP 202 with a zero-byte AWS WAF challenge;
- the official `hc1` and `hc2` delivery hosts resolved but HTTPS connections timed out from this environment;
- indexed official pages remained available as provenance evidence, with crawl ages of roughly two to five months.

This is a technical enumeration blocker, not evidence that the public archive disappeared. No challenge, login, TLS validation, or access control was bypassed.

## Discovery Contract

Future discovery uses the canonical `/2557/` route and must:

1. parse every official event tab, preserving optional month values;
2. reject an empty tab set, duplicate `(ROC year, month)` identities, unexpected routes, and excessive tab growth;
3. request each tab at `Page=1&PageSize=60`;
4. reject empty, cross-year, or cross-session content;
5. reject duplicate asset URLs across the source family;
6. reject any remaining same-route `Page>1` link;
7. expose the archive URL as year provenance and the filtered tab URL as event provenance.

Stable event IDs are:

- `taipower-recruit-<ROC year>` for ordinary annual events;
- `taipower-recruit-107-5` and `taipower-recruit-107-12` for the two 2018 sessions.

Discovery deliberately fails on the current WAF response instead of interpreting an empty body as an empty archive.

## Retained-State Reconciliation

Current retained state is unchanged by this audit:

- 21 raw events;
- 370 normalized records;
- 370 unique source URLs;
- 370 unique SHA-256 checksums;
- 370 referenced mirror files totaling 194,695,148 bytes;
- zero sync-failure and review-queue rows.

Every retained event is represented by an official tab. The two official ROC 107 sessions are source-only. The retained records are valid Taipower hiring material but are not complete event listings.

The mirror contains eight additional unreferenced PDFs totaling 3,570,035 bytes. First-page text identifies them as MOEA joint 新進職員 material under ROC 91, 93, 100, 101, and 107 paths. They are recorded with exact paths, sizes, and checksums in the source manifest. They were not deleted because mirror cleanup belongs in the reviewed MOEA/Taipower migration.

All 370 retained Taipower source URLs and checksums are duplicated exactly by the incorrect `moea_recruit` state. That duplication is evidence of MOEA contamination, not a reason to discard the Taipower records.

## Normalization and Publication

- normalized records carry `provider_id = "taipower_recruit"`;
- `canonical_id`: `taipower-recruit`;
- `canonical_name`: `台電新進僱用人員甄試`;
- annual and monthly sessions retain distinct `source_exam_id` values;
- answer labels contain `答案` or `解答`; other accepted download labels are questions.

The generated publication currently contains 370 files in bundle `taipower-recruit-employment-recruitment-not-applicable-taipower-recruit`. Site metadata, frontend feed, and release metadata all report 370. The canonical local ZIP is 138,668,672 bytes with SHA-256 `13b11dd4613ef0b77b4c4a5513cd763b0ab08662d675b91a668eb00c2047bec2`.

This generated agreement proves internal consistency only. It does not prove official-source completeness or remote GitHub release availability.

## Legal and Technical Posture

Taipower's open-data declaration permits broad attributed reuse for material within Taipower's copyright, subject to exclusions and third-party rights. It does not independently establish ownership of every examination item. The prior `/robots.txt` capture returned an HTML error page rather than a machine-readable robots policy.

The scheduled workflow is `.github/workflows/sync-taipower-recruit.yml`. It performs provider sync and commits provider data without the complete aggregate publication/test gate. Until live full-listing enumeration and the sibling-provider migration are approved, scheduled output should remain off a releasable branch.

## Safe Migration Sequence

1. Recheck the canonical source from an approved browser-capable environment.
2. Capture all 23 event tabs and every bounded listing page; require no residual pagination.
3. Download and validate every listed public asset through the normal provider path.
4. Review the two ROC 107 sessions and subject/question-answer identities.
5. Preserve the current 370-record audit and eight orphan-file ledger.
6. Replace retained Taipower state only as one provider-scoped raw/catalog/mirror change.
7. Remove Taipower files from the MOEA identity only in the separate reviewed MOEA migration.
8. Rebuild site bundles, frontend feed, and release metadata; run all aggregate gates before any publication decision.

No retained data, mirror file, bundle, release asset, or frontend record was changed by this source audit.
