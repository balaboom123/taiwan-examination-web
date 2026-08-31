# Teacher Exams Stable Source Expansion Spec

## 3. 教師資格考試 / 教師甄試

- 教師資格考 is national (教育部).
- 教甄 is per-county/school, scattered but high demand.

## Goal

Improve teacher-related coverage without weakening the source-quality rule. The catalog should keep the national `teacher_qual` provider as the stable 教師資格考試 source and add 教師甄試 only through reviewed official sources that expose public downloadable papers.

## Current Coverage

The public feed currently has these teacher-related canonical bundles:

| Bundle | Source shape |
|---|---|
| `teacher-qual` | national Ministry/national teacher qualification archive |
| `teacher-recruit-taipei-junior` | official Taipei junior-high article pages |
| `teacher-recruit-tainan` | official Tainan current-year selection site |
| `teacher-recruit-newtaipei` | official New Taipei public announcement API |
| `teacher-recruit-taoyuan-elementary` | official Taoyuan current-year paper page |
| `teacher-recruit-kaohsiung` | official Kaohsiung elementary and special-ed sites |
| `teacher-recruit-central-alliance` | officially linked Central Alliance current-year paper site |

This is intentionally partial. 教甄 has no single official national past-paper archive comparable to the teacher qualification exam.

## Source Review Result

External search still surfaces private cram-school mirrors ahead of official archives. Those mirrors are rejected because they obscure source ownership and can duplicate, rename, or repackage official files.

The best reviewed incremental official source is:

| provider_id | official source | decision |
|---|---|---|
| `teacher_recruit_taipei_elementary` | 臺北市政府 official article for 114學年度公立國民小學教師聯合甄選初試試題 | implement |

The source qualifies because:

- it is an official Taipei City Government page published by 臺北市政府教育局國小教育科
- it exposes direct `Download.ashx` public PDF links
- the PDF filenames decode to subject names and all end in `含答案`
- the parser can reject non-paper attachments by filename and extension
- it matches the existing source-specific 教甄 provider model

The source is still current-year scoped. It should be labeled as another partial 教甄 source, not as broad Taipei or national coverage.

## Provider Design

Add `teacher_recruit_taipei_elementary` as a source-specific provider:

- one mapped official article year: AD 2025 / ROC 114
- one exam id: `teacher-recruit-taipei-elementary-114`
- one canonical bundle: `teacher-recruit-taipei-elementary`
- canonical name: `臺北市國小教師甄試`
- one paper per subject
- file type: `question_answer`

The provider should not crawl the Taipei city-wide news listing. That listing is not a teacher exam archive and mixes unrelated announcements.

## Documentation Updates

Update these documents:

- `docs/developer/providers/teacher_recruit-source-index.md`
- `docs/developer/providers/teacher_recruit_taipei_elementary-spec.md`
- `docs/developer/providers/teacher_recruit_city_sources-spec.md`
- `docs/developer/providers/requested-topic-support.md`
- `docs/superpowers/spec/2026-06-28-teacher-exams-design.md`
- `docs/superpowers/plans/2026-06-30-teacher-recruit-taipei-elementary-provider.md`

## Acceptance Criteria

- `teacher_recruit_taipei_elementary` is registered in provider registry and the default site.
- `teacher-recruit-taipei-elementary-*` normalizes to `臺北市國小教師甄試`.
- The provider mirrors official `含答案` PDFs as `question_answer`.
- The default public feed includes the new canonical bundle with `public_min_years` override of 1.
- The source index records the provider as implemented and current-year scoped.
- No generic 教甄 crawler is introduced.
- No private cram-school or unofficial mirror source is crawled.
