# Provider Spec: `wdasec_skill`

## Summary

- `provider_id`: `wdasec_skill`
- status: active
- target site: `default`
- source family: Workforce Development Agency Skills Evaluation Center past-exam archive
- publication shape: identity-v2 bundle assets split by skill/trade and level under the `default` site

## Source Overview

- source domain: `owinform.wdasec.gov.tw`
- source URL: `https://owinform.wdasec.gov.tw/ExamNet/owInform/PastQuestions.aspx`
- source access: public ASP.NET web application with dynamically rendered content
- source cadence: regular administrations plus separately listed massage and exceptional/rescheduled sessions; the listing changes throughout the year
- authentication: none
- licensing: public download access is verified, but the repository records no explicit redistribution license; release use still needs the source-family legal/takedown decision
- rate-limit posture: conservative; the page is ASP.NET WebForms with ViewState — each category/level selection triggers a postback, so requests must be serialized and paced

## Discovery Model

The provider interacts with the ASP.NET past-exam page via a three-step postback navigation:

1. **Category selection** — click one of three submit buttons (e.g. `btnSelectA` for 全國技能檢定各梯次試題及答案) to reveal a paginated listing
2. **Listing pagination** — a `gvData` GridView shows exam sessions (year + session title + PLAID key), navigated via `__doPostBack('gvData', 'Page$N')`
3. **Detail view** — clicking a row via `__doPostBack('gvData', 'order$N')` opens a `gvFile` GridView showing all trades for that session

The detail table groups rows by trade — the first row shows trade code and name, subsequent rows for the same trade leave those columns empty (inherited by the parser). The listing is cached once per client process. Each PLAID also has a stable official detail route, `PastQuestions.aspx?yserno=<PLAID>`, which the provider uses for event evidence and direct detail fetching after listing discovery.

Available certification levels:

| Level key   | Chinese name |
|-------------|-------------|
| `class_a`   | 甲級         |
| `class_b`   | 乙級         |
| `class_c`   | 丙級         |
| `single`    | 單一級       |

Each trade+level row links to downloadable PDF files:

- 學科測試試題 (written/academic test questions)
- 術科測試試題 (practical/skills test questions)

Provider-owned outputs live under:

- `data/providers/wdasec_skill/`
- `mirror/providers/wdasec_skill/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-wdasec-skill.yml`

That workflow is provider-only. It refreshes `data/providers/wdasec_skill/` and does not publish the aggregated `default` site on its own.

The primary operator commands are:

```bash
python -m app discover --provider wdasec_skill \
  --manifest data/providers/wdasec_skill/source-manifest.json --write-manifest
python -m app sync-full --provider wdasec_skill --site-id default
```

Coverage checkpoint (2026-07-30): the official category listing contains 145 sessions across AD 2001–2026, and `data/providers/wdasec_skill/source-manifest.json` represents all 145 exact PLAID event identities with stable detail URLs. Local state contains 145 raw events and 10,809 normalized paper records with zero sync failures and zero review-queue entries. The two newly listed AD 2026 second-session events (`202607060001` and `202607090001`) contributed 114 current official files. Event-level history accounting reports 136 published-complete events, eight explicit publication-policy exclusions, and one reviewed blocked event.

The blocked AD 2002 event `201309140001` remains in both the official listing and the manifest, but its stable detail page returns HTTP 200, zero detail rows, and `查無資料，請確定輸入資料並重新查詢`. It was rechecked on 2026-07-30; capture evidence is in `catalog/source-coverage/wdasec_skill.json`. Full ASP.NET response hashes are capture-specific because hidden ViewState fields change, so the status, stable event URL, zero parsed rows, and exact no-data marker are the durable evidence. The manifest proves listing/event representation, not that every historical file was freshly re-downloaded; the AD 2001–2024 files were separately refreshed on 2026-07-28 with zero failures. Eight valid events remain outside the public projection under the current publication policy, so this provider remains partial rather than being declared complete from manifest agreement alone.

## Scraping Considerations

The source page is an ASP.NET WebForms application. Key implementation constraints:

- category selection and listing pagination are serialized postbacks carrying `__VIEWSTATE`, `__EVENTVALIDATION`, and `__VIEWSTATEGENERATOR`; detail pages use stable direct `?yserno=` routes after listing identity is verified
- the scraper must parse and replay these hidden fields on each request to maintain server-side session state
- listing pagination fires `__doPostBack`; the scraper replicates that event target/argument once per page and caches the resulting 145-row listing
- a WAF guards the server; requests require proper `Referer` and `Origin` headers plus session cookies via `http.cookiejar.CookieJar`

## Normalization Rules

- all normalized records carry `provider_id = "wdasec_skill"`
- all public records share the `wdasec-skill` canonical source family and split into identity-v2 bundles by trade/skill and level
- canonical bundle identity:
  - `canonical_id`: `wdasec-skill`
  - `canonical_name`: `全國技術士技能檢定`
- each exam record is keyed by trade code + level + year
- year values stored as Gregorian integers; the ROC year is derived (Gregorian − 1911)

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
