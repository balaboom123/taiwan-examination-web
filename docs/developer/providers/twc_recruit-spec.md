# Provider Spec: `twc_recruit`

## Summary

- `provider_id`: `twc_recruit`
- status: implemented; bounded discovery complete, source usability partial
- target site: `default`
- accepted source family: Taiwan Water Corporation company-specific evaluation-position recruitment (台灣自來水公司評價職位人員甄試)
- canonical archive: `https://www.water.gov.tw/ch/Subject/Detail/59619?nodeId=715`
- current-cycle evidence: `https://water115-re.twrecruit.com.tw/news/?c=news&id=4`
- machine-readable evidence: `data/providers/twc_recruit/source-manifest.json`
- publication shape: one site-owned canonical bundle containing the official annual ZIPs as nested payloads

This provider does not cover the MOEA joint professional-staff examination handled by `moea_recruit`, or Taiwan Water evaluation-to-classified promotion examinations such as the separate ROC 115 `water115-po` contractor site.

## Authoritative source boundary

The canonical Taiwan Water page was captured on 2026-07-31. It was published and updated on 2026-04-10 and exposed exactly ten public annual ZIPs: ROC 103–108, 110–112, and 114 (AD 2014–2019, 2021–2023, and 2025). ROC 109 and 113 are absent from the official page. No enumerable official pre-ROC-103 index or stable public asset namespace was found. Third-party copies are discovery hints only and must not be mirrored or used to guess official URLs.

The stable normalized listing fingerprint is `sha256:c3a68ed9bb2b1f080e859fecb1dc51a30fd21573cf58cdef30d873d5032d3012`. The raw HTML capture hash is evidence for that request only because view counts and versioned asset query values can change independently of the listing.

| ROC | AD | Bytes | ZIP members | Official SHA page | ZIP integrity |
| ---: | ---: | ---: | ---: | --- | --- |
| 103 | 2014 | 7,121,847 | 15 | matches live bytes | passes |
| 104 | 2015 | 9,544,335 | 18 | matches live bytes | passes |
| 105 | 2016 | 6,268,187 | 15 | matches live bytes | passes |
| 106 | 2017 | 8,468,202 | 20 | matches live bytes | passes |
| 107 | 2018 | 6,526,975 | 16 | **does not match** | **fails: one PDF has bad CRC/local-header offset** |
| 108 | 2019 | 6,476,998 | 16 | matches live bytes | passes |
| 110 | 2021 | 7,966,172 | 16 | **does not match** | passes |
| 111 | 2022 | 12,042,852 | 61 | matches live bytes | passes |
| 112 | 2023 | 5,881,729 | 30 | matches live bytes | passes |
| 114 | 2025 | 4,899,383 | 14 | **does not match** | passes |

All ten current live downloads total 75,196,680 bytes and match the retained mirrors byte for byte. Seven Taiwan Water SHA pages match the downloads; ROC 107, 110, and 114 do not. The ROC 107 live and retained ZIP fails both Python and Info-ZIP member validation. Exact live, retained, and official hashes and the member-level failure are recorded in the source manifest.

## Current-cycle blocker

Taiwan Water's ROC 115 / AD 2026 contractor publicly announced the initial papers and reference answers on 2026-05-25. Its paper route, `https://water115-re.twrecruit.com.tw/bulletin/?c=examBulletin`, redirects unauthenticated requests to an applicant-login URL. The canonical Taiwan Water archive has not added ROC 115. This is `login_required`, not a missing-parser result; no login or access control may be bypassed.

## Discovery contract

The adapter fetches the canonical page once per client and parses annual download rows inside the official file-download blocks. Discovery must:

1. reconcile every `/ch/ServerFile/Get/` anchor with a parsed annual event;
2. reject an empty listing or more than 100 entries;
3. reject duplicate ROC years and duplicate asset URLs;
4. accept only HTTPS URLs on `www.water.gov.tw` whose path contains an exact UUID and whose sole query is `nodeId=715`;
5. return the canonical archive URL as stable year/exam provenance; and
6. reject unknown year/event requests before fetching an asset.

Internal year gaps are source facts, not automatically parser failures. A changed source shape that causes candidate/parsed mismatch must fail closed.

The primary operator command remains:

```bash
python3 -m app sync-full --provider twc_recruit --site-id default
```

The provider-only scheduled workflow is `.github/workflows/sync-twc-recruit.yml`. It refreshes and commits provider state but does not run the complete aggregate publication, strict history, catalog, source-inventory, frontend, and build gates. Its output is not releasable until those gates pass separately.

## Retained and normalized state

Provider-owned outputs live under:

- `data/providers/twc_recruit/`
- `mirror/providers/twc_recruit/`

Current retained state is ten raw events, ten normalized records, ten mirrored ZIPs, zero sync failures, and zero review records. Each annual ZIP is intentionally retained as one `file_type = accessible_bundle`; the mirror phase does **not** unpack it into individual normalized papers. Changing that shape requires an approved migration because it changes record identity, mirror layout, bundle contents, and frontend rows.

All normalized records use `provider_id = "twc_recruit"`, Gregorian `year_ad`, and event identity `twc-recruit-<ROC year>`. The canonical category is `台水評價職位人員甄試`.

## Publication integration and validation gap

All ten retained annual ZIPs are currently `published_complete` in one canonical outer bundle:

- `bundles/sites/default/twc-recruit-employment-recruitment-not-applicable-twc-recruit--1e3490bb2a80.zip`
- 75,028,487 bytes
- SHA-256 `5f4567b82ddfa45c3e7478facd6559a386ea15380813caaaca2734356f0d5820`

Site metadata, frontend metadata, and release-asset metadata each contain one matching logical bundle. That agreement does not prove remote release availability.

The outer bundle validator treats each official annual ZIP as an opaque nested file. It therefore passes even though the ROC 107 nested ZIP contains a corrupt PDF member. A future release gate must recursively validate supported nested archives, or the ROC 107 source defect must be explicitly quarantined/blocked under an approved policy.

## Legal and technical restrictions

Taiwan Water's website-data declaration at `https://www.water.gov.tw/ch/Subject/Detail/7889?nodeId=5843` applies Taiwan Government Data Open License 1.0 to copyrightable website data. It permits free, non-exclusive, sublicensable reuse with attribution, subject to caveats for other intellectual-property rights, personal data, moral rights, integrity, and implied endorsement.

`https://www.water.gov.tw/robots.txt` currently contains duplicate wildcard groups with both `Allow: /` and `Disallow: /`. This contradictory policy requires an operator/legal interpretation; it is not silently treated as blanket permission.

## Completion conditions for this provider

This provider can be considered complete only when:

- the exact canonical listing and any current public contractor source are rechecked on the documented cadence;
- every public annual asset traces through a byte-validated mirror and approved publication state;
- the ROC 107 corrupt source ZIP is repaired by Taiwan Water, replaced with independently verifiable official bytes, or explicitly blocked/quarantined by approved policy;
- the ROC 107, 110, and 114 official-SHA disagreements are resolved or formally accepted with evidence;
- ROC 115 either becomes publicly accessible and is reconciled or retains current reproducible login-blocker evidence;
- the pre-ROC-103 and internal-gap boundary remains documented without guessed URLs; and
- legal/robots and nested-archive validation decisions are recorded.
