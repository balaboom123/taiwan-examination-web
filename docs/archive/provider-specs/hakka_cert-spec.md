# Provider Spec: `hakka_cert`

## Summary

- `provider_id`: `hakka_cert`
- status: active; discovery and publication remain partial
- target site: `default`
- source family: 客語能力認證 official question-bank, sample-test, and paired-audio downloads
- primary source: `https://elearning.hakka.gov.tw/hakka/download-files`
- secondary official source: `https://elearning.hakka.gov.tw/mooc/download.php`

## Declared Scope

The examination archive includes question banks, sample tests, answers, and audio paired with those question materials.

Vocabulary-only lexicons and vocabulary audio are intentionally excluded because they are instructional language resources rather than questions, answers, or sample examinations. Undated proficiency standards and general language-selection packages are also supporting material, not annual exam events. This boundary replaces the older registry text that incorrectly claimed vocabulary PDFs were implemented archive content.

## Source Model

The current provider scans primary level categories `c=2`, `c=3`, and `c=5` and follows same-source pagination. The 2026-08-01 bounded audit found:

- 9 primary listing pages and 607 unique official download links;
- 140 links accepted by the current parser;
- 455 intentionally excluded vocabulary links;
- 5 in-scope ROC 107 intermediate/high-intermediate sample ZIPs missed because their labels use `樣卷`, not the parser's accepted tokens;
- 7 other supporting-material links outside the declared exam scope.

The separate academy download center repeats its links in desktop and mobile markup. After deduplication it exposes 50 unique ROC 113–115 packages: 15 in-scope question-bank audio packages and 35 intentionally excluded vocabulary packages. The provider does not discover this surface.

`data/providers/hakka_cert/source-manifest.json` records listing hashes, current gap URLs, declared sizes, and the exact scope boundary. Its coverage status is deliberately `partial`.

## Retained-State and Identity Risks

Retained state has 11 raw events and 156 normalized records for AD 2018–2026, but it does not represent the same 11 events as the source snapshot:

- `hakka-cert-intermediate-high-intermediate-2018` and its five sample bundles are source-only;
- retained `hakka-cert-intermediate-high-intermediate-2026` is built from undated old materials and is absent from the current exam scope;
- retained `hakka-cert-advanced-2026` is also based on undated labels forced into `MATERIALS_YEAR = 2026`;
- five advanced writing-test ZIPs are classified as `listening_audio` solely because every ZIP suffix is treated as audio;
- 20 current primary ROC 114–115 PDF/ODS URLs are not retained under their current object IDs;
- all 15 download-center question-audio packages are unintegrated; five ROC 113 declared sizes match retained files, while all ten ROC 114–115 sizes differ.

No retained record, mirror, bundle, or publication file is deleted or rewritten by this audit. Parser correction requires a reviewed identity and storage migration because the scheduled workflow currently uses `--prune-orphaned-mirror`.

## Output Model

- source exams: `hakka-cert-<level>-<year>`
- canonical bundles:
  - `hakka-cert-basic-elementary`
  - `hakka-cert-intermediate-high-intermediate`
  - `hakka-cert-advanced`
- current file types: `question`, `listening_audio`
- provider data: `data/providers/hakka_cert/`
- workflow: `.github/workflows/sync-hakka-cert.yml`

The current event model cannot honestly represent undated official sample collections. Do not solve that by assigning the wall-clock year.

## Publication and Release Constraints

Only the three synthetic/current ROC 115 events appear in generated Hakka bundles. Eight historical basic/elementary events are normalized but not published.

The largest retained official asset is 2,094,415,387 bytes. It exceeds the bundler's 1,900,000,000-byte multipart target, although it remains below GitHub's 2 GiB hard limit. A full historical publish therefore fails before output mutation. The largest package declared by the secondary source is 1,858,996,831 bytes.

Generated manifest agreement at bundle-ID level does not prove event or file coverage; strict history remains the event-level release gate.

## Access and Licensing

`https://elearning.hakka.gov.tw/robots.txt` returns HTTP 404, so there is no robots rule to claim as a restriction or permission.

The Hakka Affairs Council's government-site declaration applies Taiwan Government Data Open License 1.0 with attribution, but expressly excludes specially marked audiovisual, image, music, commissioned, and third-party works that require separate permission. The academy agreement also prohibits unauthorized commercial use of the service. Audio republication therefore needs operator/legal review; public download access alone is not redistribution proof.

## Safe Next Migration

1. Add deterministic discovery for the academy download center and deduplicate its repeated markup.
2. Accept `樣卷` as an exam-scope token and classify non-audio ZIPs as an explicit archive type.
3. Replace the wall-clock fallback with a reviewed undated-material identity policy.
4. Compare current ROC 114–115 objects byte-for-byte with retained mirrors before changing source URLs or checksums.
5. Decide whether audio may be republished and select a storage strategy for entries above the multipart target.
6. Migrate retained records, mirrors, bundles, frontend metadata, and history accounting as one reviewed provider-scoped change.
7. Run focused tests plus aggregate source-inventory, publication, release-plan, strict catalog/history, frontend, and build gates before enabling the scheduled refresh on a releasable branch.
