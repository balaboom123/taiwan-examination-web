# Provider Spec: `teacher_qual`

## Summary

- `provider_id`: `teacher_qual`
- status: active
- target site: `default`
- source family: Ministry of Education national teacher qualification exam
- source URL: `https://tqa.rcpet.edu.tw/TEA_Exam/TEA03.aspx`

## Source Model

The source is an ASP.NET WebForms page. Available years are listed in the `schyy` select box. Historical papers require two postbacks:

1. select the ROC year in `ctl00$ContentPlaceHolder1$schyy`
2. select `99` in `ctl00$ContentPlaceHolder1$exid` when available, meaning all categories

The provider parses `ShowPicOut2.aspx` direct download links under the selected year section and mirrors the all-category paper/reference-answer bundle.

## Output Model

- one exam per ROC year: `teacher-qual-<roc_year>`
- category: `教師資格考試`
- file type: `question`
- provider data: `data/providers/teacher_qual/`
- workflow: `.github/workflows/sync-teacher-qual.yml`

## Plan

1. Discover available ROC years from the public year selector.
2. Replay WebForms hidden fields and postback events for the requested year.
3. Prefer the `全部類科` selector (`exid=99`) to avoid category fragmentation.
4. Parse direct `ShowPicOut2.aspx` links in the year section.
5. Mirror the downloaded PDF/ZIP payloads through the standard sync pipeline.
