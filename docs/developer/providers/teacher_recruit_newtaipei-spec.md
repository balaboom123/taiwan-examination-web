# Provider Spec: `teacher_recruit_newtaipei`

## Summary

- `provider_id`: `teacher_recruit_newtaipei`
- status: implemented
- target site: `default`
- source family: New Taipei city education personnel joint selection announcements
- source URLs:
  - portal: `https://career.ntpc.edu.tw/`
  - public 教甄公告 route: `https://career.ntpc.edu.tw/module/newtea/module/newtea/ap/out-announce?c=01`
  - public list API: `https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/temopn_newtea_list`
  - public detail API pattern: `https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/temopn_edu/uuid/<uuid>`
  - public download-token API pattern: `https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/download/<fileUuid>`
  - public token download pattern: `https://career.ntpc.edu.tw/web-elec-bulletin/open/oauth_data/op_api/d/<token>`

## Source Model

The source is the official New Taipei City education personnel joint selection portal. The landing page is a JavaScript app that redirects to the `newtea` public announcement route, and that route embeds the official `elec-bulletin` public 教甄公告 app.

The stable crawler surface is the JSON API behind that bulletin app, not the rendered JavaScript UI. As of 2026-06-29, the list API exposes current ROC 115 / AD 2026 teacher-selection notices. Matching paper notices include:

- `【初試試題】新北市公立高級中等學校115學年度教師聯合甄選初試各該甄選科目試題及答案`
- `【初試試題】新北市立國民中學115學年度教師聯合甄選初試試題及答案`
- `公告本市115學年度國小暨幼兒園教師甄選試題與建議答案`
- `【公告】新北市115學年度公立幼兒園契約進用教保員甄選筆試試題及建議答案`
- `新北市115年度學校護理人員聯合甄選-公告初試題目及答案`

Detail records expose `attachment2` entries with `fileName`, `fileSize`, and `fileUuid`. Downloads require one extra public request: call the download-token API with `fileUuid`, then fetch the token download URL.

One sampled list UUID for the elementary/kindergarten notice returned a mismatched detail record. The provider must therefore validate that detail `opn_title` or `opn_tag` still matches the list record before accepting attachments.

## Output Model

- one exam per source tag and school year: `teacher-recruit-newtaipei-<roc_year>-<scope>`
- canonical bundle: `teacher-recruit-newtaipei`
- canonical name: `新北市教師甄試`
- category: `新北市教師甄試`
- file types:
  - `question`: question PDF/ZIP/RAR when the filename is question-only
  - `answer`: answer PDF/ZIP/RAR when the filename is answer-only
  - `question_answer`: combined question-and-answer PDF/ZIP/RAR
- provider data: `data/providers/teacher_recruit_newtaipei/`
- workflow: `.github/workflows/sync-teacher-recruit-newtaipei.yml`

Default to one canonical New Taipei bundle. Split by level only when file volume makes the bundle hard to scan.

## Plan

1. Fetch the public list API with a browser user agent.
2. Keep notices whose title contains `試題`, `題目`, or `答案`; skip `疑義`, `成績`, `錄取`, `試場`, and registration-only notices.
3. Parse ROC school year from the title or tag.
4. Fetch the detail API for each candidate UUID.
5. Accept the detail only when its title or tag matches the list record.
6. Collect `attachment2` files with names containing `試題`, `題目`, or `答案`.
7. Convert each `fileUuid` to a temporary token through the public download-token API during download.
8. Download from the token URL and preserve the official filename from `Content-Disposition` when present.
9. Group files by source tag into one `SourceExamPage` paper per notice.
10. Route `teacher-recruit-newtaipei-*` to the stable canonical bundle.
11. Publish through the default site.

## Non-Goals

- No browser automation for the Angular UI.
- No scraping private mirrors or cram-school reposts.
- No job-opening, score-query, registration, admission-list, or seat-map downloads.
- No historical reconstruction unless the official API exposes older public records with matching detail records.
