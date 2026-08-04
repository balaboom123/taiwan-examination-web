# Provider Spec: `post_recruit`

## Summary

- `provider_id`: `post_recruit`
- implementation status: implemented
- source status: partial; complete only for the bounded live-index scope below
- target site: `default`
- source family: Chunghwa Post nationwide general recruitment papers on its named TABF exam host
- canonical bundle: `post-recruit` / `中華郵政職階人員甄試`

## Accepted official sources

Chunghwa Post directly links the current TABF host and its history index from the official recruitment landing page:

- commissioning/provenance page: `https://www.post.gov.tw/post/internet/Group/index.jsp?ID=1467343194090`
- current general-cycle history index: `https://svc.tabf.org.tw/115post02//Paper/Year`
- immediately prior general-cycle history index: `https://svc.tabf.org.tw/114post01//Paper/Year`
- accepted assets: public direct PDFs under TABF `/_File/Download/<host>/HistoryPaper/`

Third-party exam and cram-school mirrors are never accepted as source evidence.

## Discovery and reconciliation

The provider unions the two still-live nationwide general-cycle indexes and gives the newer host precedence for duplicate years:

| Listing | Enumerated AD years | PDF counts |
| --- | --- | --- |
| `115post02` | 2023–2025 | 47, 13, 52 |
| `114post01` | 2022–2024 | 55, 47, 13 |

The overlapping 60 AD 2023–2024 PDFs are byte-identical across both hosts. The union therefore contains four events and 167 unique source assets, totaling 71,882,559 bytes. Every retained mirror file matches the source-reconciled SHA-256 recorded in `data/providers/post_recruit/source-manifest.json`.

A checked specialist host, `https://svc.tabf.org.tw/115post01//Paper/Year`, exposes 3, 13, and 3 PDFs for AD 2023–2025. All 19 are byte-identical subsets of the accepted general-cycle inventory, so it adds provenance but no records.

Discovery URL semantics are:

- year `search_url`: the live listing that contributed the selected year;
- exam `result_url`: the corresponding TABF history page;
- source event ID: `post-recruit-<roc_year>`;
- duplicate-year rule: first listing in `YEAR_URLS` wins.

## Explicit incompleteness and blockers

This provider does not claim historical archive completeness.

- AD 2026: the current `Paper/Index` route redirects to a login form, while the public history index still stops at AD 2025. No browser/session bypass is allowed.
- Before AD 2022: the known `111post01` year index and history page now return HTTP 404, but at least two search-indexed AD 2019/2021 PDFs still return HTTP 200. The orphaned namespace is not authoritatively enumerable, so guessing numeric file IDs is prohibited.
- Separate ad-hoc, local, disability-only, and specialist recruitments are outside this provider unless they expose a reviewed public paper archive with unique assets. The checked `115post01` specialist view is retained as duplicate evidence.
- TABF `/robots.txt` returns HTTP 404; default TLS validation succeeds.
- No redistribution license was found. Chunghwa Post's copyright declaration says reproduction or reposting of site content requires prior written consent. Mirroring/public release therefore needs legal review even though the PDFs are publicly downloadable.

## Current local state

- covered years: ROC 111–114 / AD 2022–2025
- raw events: 4
- normalized papers: 167
- sync failures: 0
- normalization review records: 0
- source manifest: `data/providers/post_recruit/source-manifest.json`
- provider data: `data/providers/post_recruit/`
- mirror data: `mirror/providers/post_recruit/`
- focused tests: `tests/test_post_recruit.py`
- refresh workflow: `.github/workflows/sync-post-recruit.yml`

## Operation

```bash
python -m app discover --provider post_recruit --write-manifest \
  --manifest data/providers/post_recruit/source-manifest.json
python -m app sync-full --provider post_recruit --site-id default \
  --years 2022 2023 2024 2025
```

The checked-in manifest is enriched after discovery with listing/event evidence and byte-level local/source reconciliation. Do not infer pre-2022 completeness from the four generated event records.

## Normalization and publication

- all normalized records carry `provider_id = "post_recruit"`;
- all accepted events map to `canonical_id = "post-recruit"`;
- canonical name is `中華郵政職階人員甄試`;
- only first-test written-paper assets are in scope;
- oral tests, physical tests, admission tickets, score lists, rosters, and authenticated current-paper views are excluded.
