# Provider Spec: `ipas_cert`

## Summary

- `provider_id`: `ipas_cert`
- status: active
- target site: `default`
- source family: iPAS 經濟部產業人才能力鑑定 official certification downloads
- source domain: `www.ipas.org.tw`

## Source Model

The iPAS home page links certification sections at `/certification/<code>/news`. Each section has a `/downloads` page with direct PDF references under `/api/proxy/uploads/`.

These downloads are official exam/certification documents such as annual briefs, score-review rules, question-dispute notices, and assessment-scope references. They are not a historical solved-paper archive.

## Output Model

- one current-year exam: `ipas-cert-downloads`
- category: `iPAS產業人才能力鑑定官方下載_<cert_code>`
- file type: `question`
- provider data: `data/providers/ipas_cert/`
- workflow: `.github/workflows/sync-ipas-cert.yml`

## Plan

1. Fetch the iPAS home page.
2. Discover certification codes from `/certification/<code>/news` links.
3. Fetch each `/certification/<code>/downloads` page.
4. Parse direct PDF URLs and percent-encode non-ASCII filenames.
5. Mirror PDFs through the standard sync pipeline.
