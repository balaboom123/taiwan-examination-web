# Provider Spec: `sfi_cert`

## Summary

- `provider_id`: `sfi_cert`
- status: implemented; bounded current-source discovery captured, retained/public identity contaminated
- target site: `default`
- accepted source family: SFI's public rolling written-test questions and selected-answer PDFs
- canonical archive: `https://www.sfi.org.tw/Node?id=217`
- rights notice: `https://www.sfi.org.tw/Node?id=73`
- machine-readable evidence: `data/providers/sfi_cert/source-manifest.json`
- publication shape: eight canonical financial-certification bundles, currently unsafe because all 30 files are mislabeled

This audit is evidence-only. It does not change the adapter, retained state, mirrors, generated bundles, frontend feed, releases, or deployment.

## Authoritative source boundary

The official page says it provides all test categories from the previous two written-test seasons. The bounded 2026-08-01 capture contains 13 rows, 25 event identities, and 50 public PDFs totaling 11,406,623 bytes. All 50 returned HTTP 200 with PDF signatures. Twelve rows expose question/answer pairs in both rolling folders; one extra sustainability row exposes a Kaohsiung pair in the first folder.

The page-wide headings are not authoritative for every row. Most PDFs are ROC 115 round 1 or ROC 114 round 3, but AML and sustainability payload headings expose older rounds: AML ROC 114 round 4 and ROC 113 round 4; sustainability ROC 114 rounds 4 and 2; and the Kaohsiung paper ROC 114 round 4. Event identity must therefore use the row label plus the PDF heading, not the mutable folder or page-wide heading alone.

| Official row | Code | Current retained interpretation |
| --- | --- | --- |
| 證券投資分析人員 | `04` | not retained under this URL |
| 證券商高級業務員 | `03` | mislabeled as 證券商業務員 |
| 證券商業務員 | `02` | mislabeled as 證券商高級業務員 |
| 證券交易相關法規與實務乙科 | `53` | not retained |
| 期貨商業務員 | `01` | mislabeled as 證券投資分析人員 |
| 期貨信託基金銷售機構銷售人員 | `59` | mislabeled as 企業內部控制 |
| 期貨交易分析人員 | `34` | not retained |
| 投信投顧業務員 | `06` | mislabeled as 期貨商業務員 |
| 投信投顧相關法規乙科 | `40` | mislabeled as 投信投顧業務員 |
| 企業內部控制 | `36` | not retained |
| 防制洗錢與打擊資恐專業人員 | `99` | not retained |
| 永續發展基礎能力測驗 | `81` | mislabeled as AML and assigned wrong years/rounds |
| 永續發展基礎能力測驗（高雄考區） | `82` | flattened into a synthetic ROC 115 round-1 event |

`Download/01` and `Download/02` are mutable presentation slots. They must not be treated as immutable historical identifiers, and numeric codes must not be mapped without the live row label.

## Retained, normalized, and public state

Local state remains 15 raw events, 30 normalized records, 30 mirrored PDFs, zero sync failures, and eight generated/public bundles. Every retained mirror is present, matches its recorded checksum, and still matches the corresponding live URL byte for byte.

That byte agreement exposes rather than resolves the defect:

- all 30 retained files are attached to the wrong official event or certification identity;
- 20 current official URLs are not retained at all;
- only 12 of 25 official event IDs overlap local IDs, but those 12 events still point to wrong files;
- 13 official events are source-only;
- local AML 2025-round-3, AML 2026-round-1, and sustainability 2026-round-1 identities are absent from PDF-derived official identity;
- all 30 files in the eight site/frontend/release bundle rows inherit the wrong identity.

Generated bundle agreement does not detect this because raw pages, normalized records, site metadata, frontend metadata, and release metadata were all derived from the same stale mapping. Strict history also reports no SFI parser gap because its live denominator comes from that adapter. The partial source manifest is the independent denominator.

## Root cause and fail-closed discovery contract

The adapter currently recognizes only codes `01`, `02`, `03`, `06`, `40`, `59`, `81`, and `82`; it misses `04`, `34`, `36`, `53`, and `99`. Its recognized mappings are also stale, and it applies two page-level round headings to every accepted URL.

A corrected adapter must:

1. fetch the canonical page once and reconcile every official download anchor;
2. reject an empty listing, an unknown row label/code, duplicate URLs, or growth beyond an approved bound;
3. pair each numeric URL with its live row label rather than a standalone code table;
4. accept only HTTPS `examweb.sfi.org.tw/Download/<two digits>/<two digits>[a].pdf` URLs;
5. derive the event year and round from a validated PDF heading when it conflicts with the page-wide heading;
6. keep standard and Kaohsiung sustainability events distinct; and
7. persist source-page/file fingerprints so rolling-slot replacement is observable.

## Safe migration sequence

1. Disable or hold the provider-only scheduled refresh on releasable branches.
2. Preserve the current manifest, raw/catalog files, mirror checksums, bundle checksums, and wrong-identity map as audit evidence.
3. Implement and test the fail-closed row/PDF-heading parser without pruning mirrors or overwriting retained state.
4. Generate corrected state in an isolated provider staging location and verify all 50 official assets.
5. Review the 13 source-only and three local-only event identities, then atomically replace or quarantine wrong state through raw, normalized, bundle, frontend, and release projections.
6. Do not republish until redistribution authority and takedown handling are approved.
7. Run focused tests plus aggregate source-inventory, strict catalog/history, publication, release-plan, frontend, and production-build gates.

No mirror deletion, history rewrite, release upload, or deployment is authorized by this spec.

## Legal and technical restrictions

The canonical page explicitly offers the PDFs for download, but no exam-PDF republication license was found. SFI's privacy/intellectual-property notice says site software, files, information, and other content are owned by SFI or other rights holders. Download availability is not treated as permission to mirror in public GitHub releases.

`https://www.sfi.org.tw/robots.txt` returns HTTP 200 after resolving to `/NotFound` HTML, so it publishes no machine-readable robots policy at that path. This is not affirmative crawl or redistribution permission.

## Completion conditions

SFI is complete only when:

- every current official row and PDF-derived event identity is represented or explicitly blocked/excluded;
- all 50 currently listed files are attached to the correct category, year, round, and venue;
- the 13 source-only and three local-only identities have reviewed dispositions;
- no wrong-identity SFI file remains in retained state, generated bundles, frontend metadata, or release metadata;
- rolling-slot changes fail closed and produce refreshed evidence;
- legal/takedown approval exists for any public redistribution; and
- aggregate release gates pass on the same commit.
