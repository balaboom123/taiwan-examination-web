# Provider Spec: `ipas_cert`

## Summary

- `provider_id`: `ipas_cert`
- status: active
- target site: `default`
- source family: iPAS 經濟部產業人才能力鑑定 official certification downloads
- current canonical host: `https://ipd.nat.gov.tw/ipas/`
- compatibility host: `https://www.ipas.org.tw/`

## Source Model

The iPAS home page links certification sections at `/certification/<code>/news`. The provider keeps this topic scoped to IT-adjacent certifications:

| Code | Certification |
|---|---|
| `ISE` | 資訊安全工程師 |
| `OIA` | 營運智慧分析師 |
| `AIAP` | AI應用規劃師 |
| `AIOT` | AIoT應用工程師 |

For each included code, the provider fetches `/news`, `/exam-info`, `/learning-resources`, and `/downloads`, then mirrors public PDF links under `/api/proxy/uploads/`.

`/learning-resources` contains published question PDFs for `ISE` and `AIAP`; `OIA` and `AIOT` currently expose official learning guides/briefs but no visible past-question section. Downloaded files are official certification documents such as published questions, annual briefs, score-review rules, question-dispute notices, and assessment-scope references.

## Output Model

- one current-year exam per included code: `ipas-cert-<code>-<year_ad>`
- category: `iPAS產業人才能力鑑定官方下載_<cert_code>`
- file type: `question`
- provider data: `data/providers/ipas_cert/`
- workflow: `.github/workflows/sync-ipas-cert.yml`

## Plan

1. Keep source IDs split by `ISE`, `OIA`, `AIAP`, and `AIOT`.
2. Fetch each included code's `/news`, `/exam-info`, `/learning-resources`, and `/downloads` pages from the current canonical host.
3. Parse relative, current-host, and legacy-host PDF URLs.
4. Percent-encode non-ASCII filenames.
5. Deduplicate by normalized PDF URL.
6. Mirror PDFs through the standard sync pipeline.
