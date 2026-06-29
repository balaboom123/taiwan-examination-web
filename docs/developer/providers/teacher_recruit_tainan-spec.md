# Provider Spec: `teacher_recruit_tainan`

## Summary

- `provider_id`: `teacher_recruit_tainan`
- status: active
- target site: `default`
- source family: Tainan city elementary and pre-K special-ed teacher joint recruitment
- source URL: `https://qualify.tn.edu.tw/trexamps/`

## Source Model

The source is an official ASP.NET WebForms site titled `臺南市國小教師甄選網`. The landing page lists current recruitment announcements with `view.aspx?id=<n>` links. The 115學年度 site exposes public attachment links under `./upload/`.

The provider is intentionally current-year scoped. Historical Tainan URLs were not found on the same host during source review, while the current site has direct public ZIP downloads for:

- `公告甄選試題及參考答案`
- `公告甄選試題正確答案`

## Output Model

- one exam per active school year: `teacher-recruit-tainan-<roc_year>`
- canonical bundle: `teacher-recruit-tainan`
- canonical name: `臺南市國小教師甄試`
- category: `臺南市國小教師甄試`
- file types:
  - `question`: question ZIP
  - `answer`: reference answer ZIP
  - `corrected_answer`: corrected answer ZIP
- provider data: `data/providers/teacher_recruit_tainan/`
- workflow: `.github/workflows/sync-teacher-recruit-tainan.yml`

## Plan

1. Fetch `https://qualify.tn.edu.tw/trexamps/`.
2. Parse the title for ROC school year.
3. Parse announcement links whose text contains `試題` or `答案`.
4. Fetch those detail pages and collect attachment links under `/trexamps/upload/`.
5. Keep only ZIP downloads related to question or answer materials.
6. Emit one `SourceExamPage` with one paper containing question, answer, and corrected-answer files when present.
7. Route `teacher-recruit-tainan-*` to the stable canonical bundle in normalization.
8. Add the provider to the default site with one-year publication allowed.

## Non-Goals

- No private cram-school mirror downloads.
- No scraping of non-paper notices such as seat maps, admission lists, vacancy lists, or registration pages.
- No historical reconstruction from unofficial archives.
