# Provider Spec: `teacher_recruit_taipei_junior`

## Summary

- `provider_id`: `teacher_recruit_taipei_junior`
- status: active
- target site: `default`
- source family: Taipei city junior-high formal teacher joint recruitment
- source URLs:
  - 114學年度: `https://www.doe.gov.taipei/News_Content.aspx?n=E831CA0A5CD0193D&sms=78D644F2755ACCAA&s=4A85C1A3A3BD7C48`
  - 113學年度: `https://www.doe.gov.taipei/News_Content.aspx?n=E831CA0A5CD0193D&sms=78D644F2755ACCAA&s=01ADD0497C10AC9C`

## Source Model

The source is official Taipei City Department of Education server-rendered HTML. Each article exposes direct `Download.ashx` PDF links for subject questions and answers.

The provider intentionally uses a fixed official article map instead of a brittle site search crawler. Add future years by adding a reviewed official DOE article URL.

## Output Model

- one exam per school year: `teacher-recruit-taipei-junior-<roc_year>`
- canonical bundle: `teacher-recruit-taipei-junior`
- canonical name: `臺北市國中教師甄試`
- category: `臺北市國中教師甄試`
- file types:
  - `question`: subject question PDF
  - `answer`: subject answer PDF
- provider data: `data/providers/teacher_recruit_taipei_junior/`
- workflow: `.github/workflows/sync-teacher-recruit-taipei-junior.yml`

## Plan

1. Fetch each reviewed Taipei DOE article URL.
2. Parse `Download.ashx` links.
3. Decode the `n` query parameter as the source filename.
4. Keep PDF filenames containing `試題` or `答案`; skip 疑義/ODT files.
5. Group files by subject into one `ParsedPaper` per subject.
6. Route `teacher-recruit-taipei-junior-*` to the stable canonical bundle.
7. Publish through the default site.

## Non-Goals

- No crawling private mirrors or unofficial reposts.
- No browser automation for Taipei DOE search pages.
- No automatic future-year discovery until a stable official listing endpoint is identified.
