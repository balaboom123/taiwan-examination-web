# Provider Spec: `ipas_cert`

## Summary

- `provider_id`: `ipas_cert`
- status: active; audit-partial
- target site: `default`
- source family: iPAS 經濟部產業人才能力鑑定 official certification downloads
- current canonical host: `https://ipd.nat.gov.tw/ipas/`
- compatibility host: `https://www.ipas.org.tw/`

## Source Model

The iPAS home page currently links 16 certification sections at `/certification/<code>/news`. The provider keeps only four IT-adjacent certifications:

| Code | Certification |
|---|---|
| `ISE` | 資訊安全工程師 |
| `OIA` | 營運智慧分析師 |
| `AIAP` | AI應用規劃師 |
| `AIOT` | AIoT應用工程師 |

For each included code, the provider fetches `/news`, `/exam-info`, `/learning-resources`, and `/downloads`, then mirrors public PDF links under `/api/proxy/uploads/`.

`/learning-resources` contains published question PDFs for `ISE` and `AIAP`; `OIA` and `AIOT` currently expose official learning guides/briefs but no visible past-question section. Downloaded files are official certification documents such as published questions, annual briefs, score-review rules, question-dispute notices, and assessment-scope references.

That four-family boundary is not an approved complete source scope. The other 12 official families (`3DP`, `ANT`, `CPM`, `CV`, `EMC`, `EVM`, `FQA`, `MDMT`, `NZ`, `PCB`, `PMAE`, and `SPE`) expose 120 PDFs, including 34 paper-like files. Across all 16 families, the current pages expose 50 paper-like PDFs. Only 16 are in the four selected families; 46 of the 62 retained PDFs are non-paper briefs, rules, forms, guides, or scope references currently labeled `question`.

The four events also use the process year even though individual documents contain mixed 2025/2026 round labels or no event year. No blanket redistribution grant was established, and the canonical robots request disconnected during the audit; do not infer permission from either condition.

## Output Model

- one current-year exam per included code: `ipas-cert-<code>-<year_ad>`
- category: `iPAS產業人才能力鑑定官方下載_<cert_code>`
- file type: `question`
- provider data: `data/providers/ipas_cert/`
- workflow: `.github/workflows/sync-ipas-cert.yml`

## Safe Next Steps

1. Decide whether scope is all 16 official families or a documented subset with explicit exclusions.
2. Fetch each included code's `/news`, `/exam-info`, `/learning-resources`, and `/downloads` pages from the current canonical host.
3. Parse relative, current-host, and legacy-host PDF URLs.
4. Percent-encode non-ASCII filenames.
5. Deduplicate by normalized PDF URL.
6. Separate actual papers/answers from briefs, rules, forms, guides, and scope references before publication.
7. Derive event identity from source metadata rather than the process date.
8. Record redistribution/takedown authority before republishing.
