# Provider Spec: `teacher_qual`

## Summary

- `provider_id`: `teacher_qual`
- status: active
- target site: `default`
- source family: Ministry of Education national teacher qualification exam
- source URL: `https://tqa.rcpet.edu.tw/TEA_Exam/TEA03.aspx`

## Source Model

The source is an ASP.NET WebForms page. Available years are listed in the `schyy` select box. The live archive currently exposes ROC 094-115 / AD 2005-2026.

Most historical papers require two postbacks:

1. select the ROC year in `ctl00$ContentPlaceHolder1$schyy`
2. select `99` in `ctl00$ContentPlaceHolder1$exid` when available, meaning all categories

ROC 108 / AD 2019 is a format transition year. It exposes `ctl00$ContentPlaceHolder1$ddlOrder` first, with first and second exam options, then exposes the `exid` category selector. ROC 107 / AD 2018 is labeled as a sample-only year (`107年僅有範例題`). ROC 099-094 headings are zero-padded.

The provider parses `ShowPicOut2.aspx` direct download links under the selected year section and mirrors the all-category paper/reference-answer bundle.

## Output Model

- one exam per ROC year: `teacher-qual-<roc_year>`
- ROC 108 split exams: `teacher-qual-108-1`, `teacher-qual-108-2`
- category: `教師資格考試`
- file type: `question`
- provider data: `data/providers/teacher_qual/`
- workflow: `.github/workflows/sync-teacher-qual.yml`

## Plan

1. Discover available ROC years from the public year selector.
2. Replay WebForms hidden fields and postback events for the requested year.
3. When `ddlOrder` is present, create one exam per official exam order.
4. Prefer the `全部類科` selector (`exid=99`) to avoid category fragmentation.
5. Parse direct `ShowPicOut2.aspx` links in the year section, including zero-padded and sample-only headings.
6. Mirror the downloaded PDF/ZIP payloads through the standard sync pipeline.
