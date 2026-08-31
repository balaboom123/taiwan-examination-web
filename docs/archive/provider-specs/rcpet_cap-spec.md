# Provider Spec: `rcpet_cap`

## Summary

- `provider_id`: `rcpet_cap`
- status: active
- target site: `default`
- source family: Research Center for Psychological and Educational Testing CAP archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

- source domain: `cap.rcpet.edu.tw`
- source URL: `https://cap.rcpet.edu.tw/examination.html`
- source access: public web pages; exam papers hosted as Google Drive links
- source cadence: yearly archive updates after each May examination administration; historical Google Drive file IDs may also be replaced
- authentication: none
- licensing: public download access is verified, but the repository records no explicit redistribution license; release use still needs the source-family legal/takedown decision
- rate-limit posture: conservative scheduled sync; the main page loads per-year content into an iframe via a `<select>` dropdown

## Discovery Model

The main `examination.html` page contains a `<select id="exam">` dropdown whose `<option>` values point to exact per-event iframe pages. Regular events use `exam/{roc_year}/{roc_year}exam.html`; the `111c` reference event uses `exam/111c/111practice.html`. The provider caches this dropdown for one process, uses the main page as year-level evidence, and records each exact iframe URL as event-level evidence.

The 2026-07-29 snapshot contains 14 AD year buckets (2013–2026) and 15 event identities. `data/providers/rcpet_cap/source-manifest.json` represents all 15 retained events with no source-only or local-only event IDs.

Years with special status:

- 民國 102 (2013): pilot program (試辦) materials only
- 民國 111 (2022): includes supplementary reference test (參考試題) materials

Parsed subject/file identities include:

| Subject key | Chinese name / role |
|-------------|---------------------|
| `all-subjects` | 參考答案 / 試題說明 |
| `writing` | 寫作測驗 |
| `chinese` | 國文 |
| `english-reading` | 英語閱讀 |
| `english-listening` | 英語聽力 or listening archive |
| `math` | 數學 |
| `social` | 社會 |
| `science` | 自然 |

Current retained state is 15 raw events and 136 normalized records with zero sync failures and zero review-queue entries. Live reconciliation on 2026-07-29 found every parsed subject/file role and source URL equal to retained state after refreshing one changed 2014 `試題說明` file. The former official file remains a valid PDF, but the current link serves different bytes; the mirror now records SHA-256 `f0a5d0a1e5a8c6cd81661ae3c07c5e3f05684ed1ad2e73e099c2adf1781963a9`.

Provider-owned outputs live under:

- `data/providers/rcpet_cap/`
- `mirror/providers/rcpet_cap/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-rcpet-cap.yml`

That workflow is provider-only. It refreshes `data/providers/rcpet_cap/` and does not publish the aggregated `default` site on its own.

The primary operator commands are:

```bash
python -m app discover --provider rcpet_cap \
  --manifest data/providers/rcpet_cap/source-manifest.json --write-manifest
python -m app sync-full --provider rcpet_cap --site-id default
```

A full sync reuses valid mirror paths. If an official historical link changes to different bytes at the same logical paper identity, operators must verify the replacement and force a narrow mirror refresh before a scoped incremental sync; URL-only manifest agreement is insufficient.

## Normalization Rules

- all normalized records carry `provider_id = "rcpet_cap"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `rcpet-cap`
  - `canonical_name`: `國中教育會考`
- year values stored as Gregorian integers; the ROC year is derived (Gregorian − 1911)
- the pilot event (`cap-102`) and reference event (`cap-111c`) retain distinct official event identities and are intentionally included in scope

The provider does not own a public release tag. Release tags are assigned later by site publication.

## Publication Integration

After provider sync completes, publish the `default` site separately when every required provider state and mirror input for that site is available:

```bash
python -m app publish-site --site-id default --repository <owner>/<repo>
```

Canonical site-owned outputs then live under:

- `data/sites/default/bundles.json`
- `data/sites/default/release-assets.json`
- `bundles/sites/default/`

For compatibility during the migration, the `default` site may also refresh legacy root-level outputs such as `data/bundles.json`.
