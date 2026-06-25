# Provider Spec: `wdasec_skill`

## Summary

- `provider_id`: `wdasec_skill`
- status: active
- target site: `default`
- source family: Workforce Development Agency Skills Evaluation Center past-exam archive
- publication shape: one canonical bundle asset owned by the `default` site

## Source Overview

- source domain: `owinform.wdasec.gov.tw`
- source URL: `https://owinform.wdasec.gov.tw/ExamNet/owInform/PastQuestions.aspx`
- source access: public ASP.NET web application with dynamically rendered content
- source cadence: three exam administrations per year (roughly March, July, November) with archives updated after each session
- authentication: none
- rate-limit posture: conservative; the page is ASP.NET WebForms with ViewState — each category/level selection triggers a postback, so requests must be serialized and paced

## Discovery Model

The provider interacts with the ASP.NET past-exam page via a three-step postback navigation:

1. **Category selection** — click one of three submit buttons (e.g. `btnSelectA` for 全國技能檢定各梯次試題及答案) to reveal a paginated listing
2. **Listing pagination** — a `gvData` GridView shows exam sessions (year + session title + PLAID key), navigated via `__doPostBack('gvData', 'Page$N')`
3. **Detail view** — clicking a row via `__doPostBack('gvData', 'order$N')` opens a `gvFile` GridView showing all trades for that session

The detail table groups rows by trade — the first row shows trade code and name, subsequent rows for the same trade leave those columns empty (inherited by the parser).

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

The primary operator command is:

```bash
python -m app sync-full --provider wdasec_skill --site-id default
```

## Scraping Considerations

The source page is an ASP.NET WebForms application. Key implementation constraints:

- every interaction (category selection, pagination, detail navigation) is a full postback carrying `__VIEWSTATE`, `__EVENTVALIDATION`, and `__VIEWSTATEGENERATOR` fields
- the scraper must parse and replay these hidden fields on each request to maintain server-side session state
- pagination and row selection fire `__doPostBack` — the scraper must replicate the event target and argument
- a WAF guards the server; requests require proper `Referer` and `Origin` headers plus session cookies via `http.cookiejar.CookieJar`

## Normalization Rules

- all normalized records carry `provider_id = "wdasec_skill"`
- all public records map into one canonical bundle
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
- `data/sites/default/lootlabs-links.json`
- `bundles/sites/default/`

For compatibility during the migration, the `default` site may also refresh legacy root-level outputs such as `data/bundles.json` and `data/lootlabs-links.json`.
