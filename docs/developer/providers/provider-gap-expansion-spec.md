# Provider Gap Expansion Spec

## Goal

Move the known unsupported or partial topics into the website when an official public downloadable source exists. Do not create empty providers for schedule-only pages.

## Support Rule

A topic is implementable when the source is official, public, downloadable without login, and stable enough for a repeatable parser. Schedule pages, registration pages, and browser-only mock systems stay out of bundles until they expose direct downloadable assets.

## Current Decisions

| Topic | Decision | Provider work |
|---|---|---|
| 技術士技能檢定 | Implemented | Fixed `wdasec_skill` WebForms postback replay, refreshed official AD 2007–2024 sessions alongside existing 2025–2026 state, and published eligible `wdasec-skill` groups; 28 older events remain normalization gaps. |
| TOCFL 模擬試題 | Implemented | Extended `tocfl_cert` from reference downloads to official downloadable question/audio/answer/script assets. |
| 客語能力認證 audio | Implemented | Extended `hakka_cert` to include official audio ZIPs as `listening_audio` and published level bundles. |
| JLPT | Implemented | Added `jlpt_cert` for official JLPT practice workbook PDFs and listening audio from `https://www.jlpt.jp/e/samples/sampleindex.html`. |
| TOPIK | Source proof first | Add only after an official TOPIK page with direct downloadable past/sample papers is verified. |
| iCAP | Resource provider only | iCAP has official competency-resource/download surfaces, not exam papers. Add `icap_skill` only as competency resources if the product accepts non-paper downloads. |
| 軍校正期班/專業軍官班 | Source proof first | Add only after a stable official MND historical-paper or sample-paper download page is verified. |
| 教師甄試 remaining counties/schools | Source-index first | Keep the existing source-index gate. Add city/county providers only for official paper archives; do not crawl scattered school bulletins broadly. |

## Output Shape

New providers follow the existing provider contract:

- provider code under `app/providers/<provider_id>/`
- data under `data/providers/<provider_id>/`
- workflow under `.github/workflows/sync-<provider-id-kebab>.yml`
- default-site registration in `app/site_registry.py`
- classification route in `frontend/src/lib/exam-classification.ts` when the canonical prefix is new
- provider spec under `docs/developer/providers/<provider_id>-spec.md`

## Source-Proof Gates

- TOPIK: official `topik.go.kr` pages expose browser practice flows and streamed MP3 endpoints, but no stable direct downloadable PDF/past-paper archive was verified.
- iCAP: official `icap.wda.gov.tw` pages expose competency standards and resource downloads, not exam-paper archives. Keep out of provider code unless the product explicitly accepts non-paper competency-resource bundles.
- 軍校正期班/專業軍官班: official MND recruitment surfaces were checked for historical/sample-paper links, but no stable downloadable paper archive was verified.
- 教師甄試: use `teacher_recruit-source-index.md`; add providers only for official/public/downloadable archive rows.

## Non-Goals

- No private mirrors.
- No login/CAPTCHA/browser-only scraping.
- No generated bundles with zero downloadable files.
- No broad county/school crawler for teacher recruitment.
