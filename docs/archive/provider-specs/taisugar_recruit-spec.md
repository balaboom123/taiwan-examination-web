# Provider Spec: `taisugar_recruit`

## Summary

- `provider_id`: `taisugar_recruit`
- status: partial; current public discovery is byte-reconciled, retained coverage is not
- target site: `default`
- source family: Taiwan Sugar company-specific new-worker and work-study recruitment papers
- canonical source: `https://www.taisugar.com.tw/chinese/News_Index.aspx?p=3&n=10080`
- publication shape: one canonical site-owned bundle when publication policy is satisfied

## Source Boundary

This provider owns Taiwan Sugar's 新進工員 and 產學合作 recruitment papers. It does not own:

- Taiwan Sugar doctoral-level recruitment papers;
- Ministry of Economic Affairs joint new-staff recruitment;
- brochures, result lists, assignments, application forms, or other recruitment notices.

The current official listing contains two doctoral-paper rows (ROC 103 and 109). They are intentionally excluded from the `taisugar-recruit` new-worker identity. The many MOEA joint-recruitment notices on the same page remain under `moea_recruit`.

## Official Public Inventory

The live archive was rechecked on 2026-07-31. It declares 35 news rows over two pages. Eight rows are accepted worker-paper events and expose 49 public files totaling 69,909,204 bytes.

| ROC event | AD identity year | Detail ID | Public files | Bytes | Local records |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 114 | 2025 | 14062 | 1 ZIP | 6,060,841 | 1 |
| 112 | 2023 | 13012 | 2 ZIPs | 13,522,670 | 0 |
| 111 | 2022 | 11543 | 2 ZIPs | 19,591,692 | 0 |
| 110 | 2021 | 10749 | 31 PDFs | 17,025,082 | 0 |
| 109 | 2020 | 9972 | 10 PDFs | 5,799,976 | 0 |
| 108 | 2019 | 8301 | 1 PDF | 4,366,777 | 0 |
| 107 | 2018 | 7845 | 1 PDF | 1,535,677 | 0 |
| 106 | 2017 | 6900 | 1 PDF | 2,006,489 | 0 |

All 49 URLs return HTTP 200 and match PDF or ZIP signatures. Their exact sizes and SHA-256 checksums are in `data/providers/taisugar_recruit/source-manifest.json`.

The ROC 109 title is `109新進工員甄試考題` and omits `年`. ROC 106–109 use `甄試考題`; ROC 110–114 use `甄試試題`. Discovery must recognize both forms without admitting doctoral rows.

## Current-Cycle Restriction

The official ROC 115 / AD 2026 announcement links the commissioned contractor at `https://tsc115-re.twrecruit.com.tw/news/`. Its navigation exposes `試題公告 / 疑義`, but an unauthenticated request to `https://tsc115-re.twrecruit.com.tw/bulletin/?c=examBulletin` returns HTTP 302 to the contractor login page. The Taiwan Sugar archive has no ROC 115 paper announcement as of the audit.

This is an evidence-backed access blocker, not evidence that no 2026 papers exist. No login, challenge, or access control was bypassed.

## Discovery Contract

The listing uses ASP.NET postback pagination. Adding `page=N` to the query string is ignored and returns page one. Discovery must:

1. fetch page one and parse the official page selector, declared row count, `__VIEWSTATE`, and `__EVENTVALIDATION`;
2. reject missing pagination state, more than 50 pages, changed page/row totals, duplicate detail URLs, empty pages, or a final row-count mismatch;
3. submit each later page through `ctl00$MainContent$wucNews_index$ddlPager` and the official `前往` control;
4. accept only titles containing `新進工員` and either `甄試試題` or `甄試考題`;
5. reject duplicate accepted ROC-year identities;
6. follow each accepted detail page and accept public PDF and ZIP links only under that detail's `/upload/UserFiles/News/<id>/` path;
7. reject empty details, cross-detail file paths, unsupported hosts/routes, and duplicate file URLs;
8. expose the archive URL as year provenance and the detail URL as event provenance.

The previous adapter violated this contract in two independent ways: it stopped on page one because that page currently has no paper row, and its query-string page requests did not advance the source. Even if it had reached page two, it accepted only ZIPs and would have dropped the 44 public PDFs.

## File Semantics

- labels that contain only `答案` map to `answer`;
- labels that contain `解答`, or both `試題` and `答案`, map to `question_answer`;
- other accepted files map to `question`.

The source-level assets remain ZIPs or PDFs. The current pipeline does not unpack ZIP members into separately normalized records, despite the previous specification saying it did.

## Retained and Publication State

The audit did not alter retained data:

- 1 raw event and 1 normalized record, ROC 114 / AD 2025;
- 1 referenced mirror ZIP, 6,060,841 bytes;
- zero sync failures and zero review records;
- retained source URL and SHA-256 exactly match the current official asset;
- seven public source events and 48 public files are absent locally.

History classifies the retained event as `excluded_by_publication_policy`. It is normalized and mirrored, but the current multi-year publication policy does not produce a Taiwan Sugar site, frontend, or release bundle. This is a policy exclusion, not public coverage.

Changing the corrected parser's file types or adding the seven missing events requires a reviewed provider migration. No sync was run during this audit.

## Legal and Technical Posture

Taiwan Sugar's government-data declaration publishes copyrightable website data under CC0-1.0. The declaration retains caveats for other intellectual-property rights, personal data, specially excluded works, moral rights, malicious alteration, and implied endorsement. Those caveats still require a source-family legal/takedown decision before release.

`robots.txt` does not disallow the recruitment archive or `/upload/` assets. The source validates with the default TLS trust chain.

The workflow `.github/workflows/sync-taisugar-recruit.yml` is manual-only. It runs provider sync and commits provider data without the complete aggregate test, publication, strict-history, frontend, or data-integrity gates. Do not dispatch it until the provider migration and current-cycle scope are approved and the operator is prepared to rebuild the default-site metadata and publish the matching release asset in the same controlled change.

## Safe Migration Sequence

1. Recheck both archive pages and the ROC 115 contractor route.
2. Regenerate the discovery manifest and require exact 35-row, 8-public-event, and 49-file reconciliation unless reviewed source drift explains a change.
3. Preserve the current ROC 114 record and checksum as migration evidence.
4. Fetch all eight public events through the normal provider path without touching doctoral or MOEA rows.
5. Review ZIP/PDF file semantics and whether ZIP-member expansion belongs in scope.
6. Replace provider raw/catalog/mirror state in one isolated migration.
7. Rebuild site, frontend, and release metadata and run every aggregate gate.
8. Publish only after the publication-policy and legal decisions are approved.

No retained record, mirror asset, bundle, frontend feed, release asset, or deployment was changed by this source audit.
