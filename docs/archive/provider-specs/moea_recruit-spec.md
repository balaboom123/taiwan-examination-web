# Provider Spec: moea_recruit

## Summary

- provider_id: moea_recruit
- status: partial
- target site: default
- source family: 經濟部所屬事業機構新進職員甄試
- official host: Taiwan Power Company on behalf of the Ministry of Economic Affairs
- discovery manifest: data/providers/moea_recruit/source-manifest.json
- publication shape: one canonical bundle owned by the default site

The official archive is publicly enumerable, but the retained provider state is
not MOEA joint-recruitment data. All 370 retained records are Taipower
company-specific new-hire or training-class papers duplicated under the MOEA
identity. The generated MOEA bundle still publishes those records.

This checkpoint corrects discovery and records the exact mismatch. It does not
delete, replace, or republish retained data.

## Authoritative source boundary

| Source | Role | Current disposition |
|---|---|---|
| https://service.taipower.com.tw/exam/info.aspx | Official examination portal | Provenance; links to the current outline and paper archives |
| https://www.taipower.com.tw/2289/2544/2554/2556/ | 歷年新進職員試題解答 | Included MOEA joint-recruitment source |
| https://www.taipower.com.tw/tc/download.aspx?mid=261 | Legacy MOEA archive route | Included entry point; redirects to /2556 |
| https://www.taipower.com.tw/2289/2544/2554/2555/ | 歷年甄試簡章 | Excluded from paper records; provenance and scope evidence only |
| https://www.taipower.com.tw/2289/2544/2554/2557/ | 歷年新進僱用人員(養成班)試題解答 | Excluded; owned by taipower_recruit |
| https://www.taipower.com.tw/tc/download.aspx?mid=262 | Legacy route currently redirecting to /2556 | Not reliable Taipower-hiring provenance; do not use to merge the two families |

The official navigation labels /2556 as new professional-staff papers and /2557
as Taipower new-hire/training-class papers. These are distinct official exam
families. The identical retained catalogs are therefore a data error, not an
ownership alias.

## Verified official archive

A live 2026-07-31 audit enumerated every year tab at
Page=1&PageSize=200 and rejected any residual same-route Page>1 link.

| AD year | ROC year | Subject groups | Listed files |
|---:|---:|---:|---:|
| 2025 | 114 | 23 | 68 |
| 2024 | 113 | 24 | 70 |
| 2023 | 112 | 24 | 70 |
| 2022 | 111 | 23 | 67 |
| 2021 | 110 | 22 | 64 |
| 2020 | 109 | 26 | 76 |
| 2019 | 108 | 27 | 79 |
| 2018 | 107 | 29 | 85 |
| 2017 | 106 | 29 | 85 |
| 2016 | 105 | 26 | 76 |
| 2015 | 104 | 26 | 76 |
| 2014 | 103 | 25 | 73 |
| 2013 | 102 | 38 | 112 |
| 2012 | 101 | 37 | 109 |
| 2011 | 100 | 25 | 73 |
| 2009 | 98 | 16 | 45 |
| 2008 | 97 | 23 | 66 |
| 2007 | 96 | 23 | 68 |
| 2006 | 95 | 19 | 66 |
| 2004 | 93 | 19 | 37 |
| 2002 | 91 | 11 | 21 |
| **Total** |  | **515** | **1,486** |

All 1,486 listed asset URLs are unique. The manifest preserves the exact year
set, per-year counts, URL-set hashes, year-specific listing URLs, capture-only
HTML fingerprints, and source/legal evidence.

This is a complete listing-level snapshot of the current official archive. It
is not asset completeness: the 1,486 PDFs have not yet been downloaded,
signature-checked, or byte-reconciled into corrected MOEA provider state.

## Discovery and parsing model

The provider:

1. fetches the legacy mid=261 entry point and reads the official year tabs;
2. requires at least one unique year tab and rejects more than 100;
3. constrains every tab to the canonical /2556 listing route;
4. requests each year once at Page=1&PageSize=200;
5. rejects empty pages, cross-year content, duplicate asset URLs, and any
   residual Page>1 pagination;
6. emits one moea-recruit-{ROC year} event per represented year;
7. preserves the exact year-specific listing URL as year and exam provenance;
8. labels events as 經濟部所屬事業機構新進職員甄試.

The old adapter accepted only page 1. For ROC 114 that meant 10 of 23 subject
groups and 29 of 68 files. The corrected bounded pagination contract is covered
by focused tests.

Provider-owned paths are:

- data/providers/moea_recruit/
- mirror/providers/moea_recruit/

The source-only discovery command is:

    python -m app discover --provider moea_recruit --write-manifest --manifest data/providers/moea_recruit/source-manifest.json

The normal full-sync command remains:

    python -m app sync-full --provider moea_recruit --site-id default

Do not run or merge the scheduled full sync against retained state until the
migration below is approved and rehearsed in an isolated data/mirror path.

## Retained-state and publication mismatch

Current retained MOEA state has 21 raw events and 370 normalized records for AD
2001, 2003, 2005–2008, 2010, 2012–2017, and 2019–2026.

Every one of those records contains Taipower new-hire or training-class labels.
The complete source-URL set and checksum set are byte-for-byte duplicates of
taipower_recruit. The duplicate MOEA mirror occupies 194,695,148 bytes. The
generated MOEA bundle publishes 370 files and is 138,667,426 bytes.

Five official MOEA events are absent locally:

- AD 2002 / ROC 91
- AD 2004 / ROC 93
- AD 2009 / ROC 98
- AD 2011 / ROC 100
- AD 2018 / ROC 107

Five local events do not exist in the official MOEA manifest:

- AD 2001 / ROC 90
- AD 2003 / ROC 92
- AD 2005 / ROC 94
- AD 2010 / ROC 99
- AD 2026 / ROC 115

Sixteen event IDs happen to overlap, but their retained files still belong to
the wrong source family. Event-ID agreement must not be treated as content
coverage.

## Required migration

A reviewed migration must:

1. preserve an audit record of the 370 misclassified rows and their duplicate
   mirror/bundle impact;
2. run corrected MOEA sync into an isolated data and mirror root;
3. download and validate all 1,486 currently listed official assets, recording
   inaccessible or invalid files rather than hiding failures;
4. review question/answer grouping and normalized subject identity before
   replacing public state;
5. replace or quarantine the wrong provider state only with explicit approval;
6. regenerate MOEA history, bundles, frontend data, and release metadata as one
   coherent checkpoint;
7. run focused, aggregate publication, strict history, catalog, and frontend
   gates before the scheduled workflow is re-enabled.

Until that migration is complete, moea_recruit remains partial and must not be
presented as covered.

## Normalization and publication

Corrected events use:

- canonical_id: moea-recruit
- canonical_name: 國營事業聯招（新進職員）
- category: 國營事業聯招（新進職員）
- event label: {ROC year}年度經濟部所屬事業機構新進職員甄試

Site publication happens later through the default-site pipeline. The source
manifest is discovery evidence; it is neither publication authorization nor
proof that mirrors, bundles, frontend data, or release assets are correct.

## Legal and technical posture

- Taipower's government-site open-data declaration at
  https://www.taipower.com.tw/26275/26692/26698/normalPost permits broad,
  attributed reuse for material within Taipower's copyright, subject to stated
  exclusions and third-party rights.
- That declaration does not independently establish ownership of every exam
  item; attribution and takedown handling remain required.
- https://www.taipower.com.tw/robots.txt returns HTTP 200 with an HTML error
  page identifying the resource as not found. No machine-readable robots
  policy was found.
- Default TLS validation succeeds for the archive and PDF host. The separate
  service.taipower.com.tw portal was successfully captured but later TLS
  handshakes intermittently timed out; it is provenance, not a required asset
  path.
- Discovery must remain conservative, bounded, and fail closed on pagination
  or source-route drift.
