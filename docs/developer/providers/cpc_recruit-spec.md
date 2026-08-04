# Provider Spec: cpc_recruit

## Summary

- provider_id: cpc_recruit
- status: partial
- target site: default
- source family: CPC Corporation company-specific recruitment
- accepted automated input: CPC's static doctoral recruitment exam-paper archive
- discovery manifest: data/providers/cpc_recruit/source-manifest.json
- publication shape: one canonical bundle owned by the default site

The static CPC page is fully enumerated, but the provider is not complete. Newer
company-specific recruitment papers are handled by annual contractor sites whose
paper routes are currently login-gated or no longer enumerable. The retained
catalog and published bundle also contain 12 operational recruitment brochures
that were historically misclassified as question papers.

## Authoritative source boundary

| Source | Role | Current disposition |
|---|---|---|
| https://www.cpc.com.tw/News.aspx?n=32&sms=8969 | CPC employment-information hub | Provenance and source-family discovery |
| https://www.cpc.com.tw/News_Content.aspx?n=32&s=826 | Doctoral recruitment exam papers | Included; exactly five packages |
| https://www.cpc.com.tw/News_Content.aspx?n=32&s=825 | Doctoral recruitment brochures | Excluded; brochures are not papers |
| https://www.cpc.com.tw/News_Content.aspx?n=32&s=824 | Operational recruitment brochures | Excluded; exactly 15 brochure PDFs |
| https://www.cpc.com.tw/News_Content.aspx?n=32&s=844 | MOEA joint recruitment redirect | Delegated to moea_recruit; do not duplicate |
| https://cpc114.twrecruit.com.tw/news/ | ROC 114 / AD 2025 contractor | Provenance only; both paper routes require login |
| https://cpcdr113.twrecruit.com.tw/ | ROC 113 / AD 2024 doctoral contractor | Blocked; no public listing and current TLS hostname mismatch |

The AD 2025 contractor provenance is confirmed by the official MOEA announcement
at https://www.moea.gov.tw/MNS/Populace/news/News.aspx?kind=5&menu_id=44&news_id=120632.
The AD 2024 doctoral contractor provenance is confirmed by
https://www.moea.gov.tw/MNS/populace/news/News.aspx?kind=5&menu_id=44&news_id=115818.

The following AD 2025 paper routes redirect to login and must not be bypassed:

- https://cpc114.twrecruit.com.tw/bulletin/?c=itemBulletin
- https://cpc114.twrecruit.com.tw/bulletin/?c=examBulletin

Other annual or special-purpose contractor domains are not silently folded into
this provider. They require official provenance, an explicit scope decision, and
an independently enumerable public paper surface.

## Included static archive

The accepted s=826 page exposes these five packages and no other doctoral paper
years:

| AD year | ROC year | Format | Bytes | SHA-256 |
|---:|---:|---|---:|---|
| 2009 | 98 | RAR | 4,400,180 | d405a14d684b5886990a1631bc77c2336445fa84e4914328577aec04ccb7bb92 |
| 2011 | 100 | ZIP | 1,352,522 | 59573915f772d39347f8bb837d81640b1c610f4f22408c7664ed7870c37ae5a7 |
| 2012 | 101 | RAR | 1,767,077 | bda4b363e48d7faa3114027fe9addb6eba140e90fbdcd645a0b7dcee73ab193f |
| 2013 | 102 | RAR | 3,586,393 | 3418c2cbeb085fb5e4e1b734daaf2c6692fb4a36fd68988a12aaef4af8ac9912 |
| 2019 | 108 | RAR | 2,965,120 | 8704223da20b6fdcf1a1985acf3beab36c31ceaf7854e3122c04405db4e17ad8 |

All five live files, totaling 14,071,292 bytes, were byte-identical to the
retained mirror on 2026-07-31. Page fingerprints, source URLs, storage keys,
verification timestamps, access blockers, and licensing evidence are retained
in the provider manifest.

This proves the current static page boundary only. It does not prove that all
historical or contracted CPC recruitment papers are discoverable.

## Excluded brochure archive and retained contamination

The s=824 page contains 15 operational recruitment brochures for ROC years
98, 100–111, 113, and 114. Those files describe recruitment rules and subjects;
they are not examination papers.

Twelve brochures are already retained as normalized question records:

- mixed with valid doctoral archives: AD 2009, 2012, and 2019;
- brochure-only events: AD 2015–2018, 2020–2022, 2024, and 2025.

The current generated CPC bundle therefore contains 17 files: five genuine
doctoral-paper archives and 12 misclassified brochures. The discovery adapter
now excludes brochures, but this checkpoint deliberately does not delete,
rewrite, or republish retained data. A separate reviewed migration must:

1. define whether brochures are quarantined, reclassified into a non-paper
   document family, or removed from publication;
2. update raw pages, normalized papers, history, bundles, and frontend data as
   one coherent change;
3. verify that the resulting bundle contains only the approved document scope;
4. preserve an audit trail for every removed or reclassified record.

Until that migration is complete, cpc_recruit remains partial and this branch is
not safe to merge into a branch where the scheduled full sync runs unattended.

## Discovery and parsing model

The provider:

1. fetches only News_Content.aspx?n=32&s=826;
2. extracts CPC Download.ashx links;
3. reads the ROC year from visible text or the decoded n filename parameter;
4. emits one cpc-recruit-{ROC year} event for each represented year;
5. preserves the official listing page as both year and exam discovery
   provenance;
6. treats linked RAR or ZIP packages as question archives.

The generic parse_employment_page helper remains independently testable against
brochure-shaped HTML, but the provider's input path does not call it for s=824.

Provider-owned state lives under:

- data/providers/cpc_recruit/
- mirror/providers/cpc_recruit/

The source-only discovery command is:

    python -m app discover --provider cpc_recruit --write-manifest --manifest data/providers/cpc_recruit/source-manifest.json

The normal full-sync command remains:

    python -m app sync-full --provider cpc_recruit --site-id default

Do not run or merge the scheduled full-sync change until the retained brochure
migration and publication decision above are complete.

## Normalization and publication

Newly parsed events use the category and raw exam name
中油新進博士級人員甄試. The legacy canonical identity remains cpc-recruit /
中油新進人員甄試 for bundle compatibility; changing that public identity is a
separate data-migration decision.

The provider does not own a public release tag. Site publication happens later
through the default site pipeline. A source manifest is evidence of discovery;
it is not authorization to publish and does not establish bundle correctness.

## Legal and technical posture

- CPC's government-site open-data declaration at
  https://www.cpc.com.tw/cp.aspx?n=2559 grants broad attributed reuse for
  material within CPC's copyright, subject to stated exclusions. It does not
  establish third-party ownership rights for every archived examination item.
- https://www.cpc.com.tw/robots.txt resolves to the CPC HTML homepage, so no
  machine-readable robots policy was found.
- Default TLS validation succeeds for www.cpc.com.tw and ws.cpc.com.tw.
- The retired AD 2024 doctoral contractor hostname currently fails default TLS
  hostname validation.
- Contractor login gates are recorded as blockers and are not bypassed.
- Discovery and sync must use conservative request rates and retain exact source
  provenance and checksums.
