# Teacher Qualification And Recruitment Exams Design

## Goal

Support the topic "教師資格考試 / 教師甄試" in the default exam catalog without pretending the two source models are the same.

The product should:

- keep `teacher_qual` as the national, stable 教師資格考試 provider
- treat 教師甄試 as a high-demand but scattered source family
- add 教甄 only source-by-source, when an official county or school page exposes stable downloadable exam files

## Background

This topic has two user intents:

| User intent | Source shape | Product decision |
| --- | --- | --- |
| 教師資格考試 | National exam, Ministry of Education / national teacher qualification source | Supported by the existing `teacher_qual` provider |
| 教師甄試 | County, city, district, and school recruitment exams | Planned as a staged source index plus selective providers |

教師資格考試 is close to the existing product model: one official source, recurring years, one canonical bundle.

教師甄試 is different. Candidates search for a subject, school level, region, and year. The source material is scattered across county education bureaus, joint recruitment committees, individual schools, and short-lived announcement pages. A single `teacher_recruit` crawler would be brittle and misleading.

## Current State

- `teacher_qual` exists under `app/providers/teacher_qual/`.
- The official `teacher_qual` archive at `https://tqa.rcpet.edu.tw/TEA_Exam/TEA03.aspx` exposes ROC 094-115 / AD 2005-2026.
- The default site includes `teacher_qual` in `app/site_registry.py`.
- Normalization maps `teacher-qual-*` into the canonical bundle `teacher-qual`.
- `docs/developer/providers/teacher_qual-spec.md` already documents the national provider.
- `teacher_qual` handles ROC 108 / AD 2019 as first and second exam entries, ROC 107 / AD 2018 as a sample-only archive entry, and ROC 099-094 zero-padded headings.
- `teacher_recruit_tainan` implements the first 教甄 source from an official Tainan current-year recruitment site.
- `teacher_recruit_taipei_junior` implements official Taipei DOE junior-high 教甄 article pages.
- `teacher_recruit_taipei_elementary` implements the official Taipei City elementary 教甄 article page for 114學年度 combined question-and-answer PDFs.
- `teacher_recruit_newtaipei` implements the official New Taipei education personnel joint selection portal and its public 教甄公告 JSON API.
- `teacher_recruit_taoyuan_elementary` implements the official Taoyuan elementary selection site's `answer.aspx` paper page.
- `teacher_recruit_kaohsiung` implements official Kaohsiung elementary and special-education current-year exam sites.
- `teacher_recruit_central_alliance` implements the current-year Central Alliance question/answer site, with official provenance from Taichung, Keelung, and Hsinchu County selection pages.
- The official national recruitment portals checked so far (`personnel.k12ea.gov.tw/tsn/` and `tjn.moe.edu.tw/EduJin/Opening/Index`) are job/opening portals, not past-paper archives.
- `docs/developer/providers/requested-topic-support.md` marks 教甄 as partially implemented because broader county and school recruitment papers remain scattered.

The human-readable provider registry should distinguish implemented source-specific 教甄 providers from future source candidates.

## Scope

This design covers:

- the public topic shape for 教師資格考試 / 教師甄試
- provider topology
- bundle identity rules
- staged support for scattered 教甄 sources
- acceptance criteria for deciding when a 教甄 source is worth implementing

It does not cover:

- creating one generic 教甄 crawler across arbitrary county and school sites
- scraping social posts, cram-school mirrors, forums, or unofficial archives
- collecting job openings, registration deadlines, or admission lists
- building a search engine over school announcements

## Design Decisions

### 1. Keep 教師資格考試 As One Canonical Bundle

`teacher_qual` remains the national provider and the comprehensive official source for 教師資格考試 past papers.

| Field | Value |
| --- | --- |
| provider_id | `teacher_qual` |
| canonical_id | `teacher-qual` |
| canonical_name | `教師資格考試` |
| source family | national teacher qualification exam |
| consuming site | `default` |
| source coverage | ROC 094-115 / AD 2005-2026 from the live selector |
| bundle strategy | one bundle across available years |

No new provider is needed for 教師資格考試. The provider must keep the source-specific quirks in one place: ROC 108 first/second exam order, ROC 107 sample-only wording, and ROC 099-094 zero-padded headings.

### 2. Do Not Create One Generic 教甄 Provider

Do not create `teacher_recruit` as a crawler over arbitrary county and school pages.

Reason: 教甄 does not have one stable national archive. A generic crawler would need per-site parsing branches, short-lived URL handling, and broad failure recovery. That is more code than a set of explicit source providers, and it hides source ownership.

### 3. Start 教甄 With A Source Index

Create a small source-index document before implementing any 教甄 provider:

```text
docs/developer/providers/teacher_recruit-source-index.md
```

Each row records an official source candidate:

| Field | Meaning |
| --- | --- |
| `source_id` | stable slug, e.g. `taipei-teacher-recruit` |
| `source_name` | county, city, committee, or school name |
| `official_url` | entry page for past papers or recruitment announcements |
| `scope` | county-wide / school-specific / subject-specific |
| `has_downloadable_papers` | yes / no / indirect / unknown |
| `year_depth` | observed years with public downloadable files |
| `file_types` | PDF, ZIP, DOCX, etc. |
| `stability` | stable archive / annual page / unstable announcement |
| `decision` | implement / watch / reject |

This keeps research cheap and prevents a pile of half-working crawlers.

The accepted source-specific providers are `teacher_recruit_tainan`, `teacher_recruit_taipei_junior`, `teacher_recruit_taipei_elementary`, `teacher_recruit_newtaipei`, `teacher_recruit_taoyuan_elementary`, `teacher_recruit_kaohsiung`, and `teacher_recruit_central_alliance`. These providers are intentionally source-scoped rather than claiming national 教甄 coverage.

The checked national recruitment portals are rejected for paper crawling because they do not expose downloadable past-paper archives. Taipei elementary is implemented as a current-year scoped provider after source review confirmed the official article is published by 臺北市政府教育局國小教育科 and exposes direct `Download.ashx` PDFs whose filenames decode into subject names ending in `含答案`. New Taipei is stronger than a single article source because one official portal exposes a public list API, detail API, attachment metadata, and download-token API for multiple current-year teacher-selection notices.

Taoyuan, Kaohsiung, and Central Alliance are current-year source providers. They are useful because they expose direct paper files from official or officially linked selection sites, but they do not prove historical or national completeness. The Central Alliance vendor host is accepted only with official provenance: reviewed Taichung, Keelung, and Hsinchu County selection pages point candidates to that site for papers or answer appeals.

### 4. Implement 教甄 Source Providers Only When Stable

A 教甄 source is eligible for implementation only when it meets all of these:

- official public source
- downloadable exam paper or answer files
- at least two years of material, or one year with clear annual continuity
- stable URL pattern or stable archive page
- no login, CAPTCHA, or manual JavaScript-only flow

Eligible providers use one provider per source owner:

| Example provider_id | Source scope | Bundle strategy |
| --- | --- | --- |
| `teacher_recruit_taipei` | Taipei public teacher recruitment archive | one or more bundles by school level or subject group |
| `teacher_recruit_taipei_elementary` | Taipei elementary teacher recruitment article page | one bundle for current-year elementary papers |
| `teacher_recruit_newtaipei` | New Taipei public teacher recruitment archive | one or more bundles by school level or subject group |
| `teacher_recruit_taoyuan_elementary` | Taoyuan elementary teacher recruitment paper page | one bundle for current-year elementary papers |
| `teacher_recruit_kaohsiung` | Kaohsiung elementary and special-education teacher recruitment sites | one source bundle, split by scope only if needed |
| `teacher_recruit_central_alliance` | Central Alliance current-year question/answer site | one bundle by source, split by level only if needed |
| `teacher_recruit_k12_joint` | a stable joint recruitment committee | one bundle if the source is small |

Provider IDs should name the source owner, not the exam category.

### 5. Bundle 教甄 By User Search Intent

For 教甄, users usually care about level and subject more than the publishing office. Bundle granularity should follow what the source actually exposes:

| Source exposes | Bundle as |
| --- | --- |
| one ZIP/PDF set per year covering all subjects | one canonical bundle for that source |
| separate elementary / junior-high / senior-high files | one bundle per level |
| separate subject files with enough history | one bundle per source + subject |

Default to fewer bundles. Split only when a combined bundle becomes hard to scan or too large to download.

## Classification

Both 教師資格考試 and 教師甄試 belong in the existing education-facing public catalog, but they should not be merged into the MOEX civil-service default class by accident.

Planned frontend classification:

| Bundle prefix | Class | Subclass |
| --- | --- | --- |
| `teacher-qual` | 教育升學 / 教育考試 class, if added | 教師資格考試 |
| `teacher-recruit-` | 教育升學 / 教育考試 class, if added | 教師甄試 |

If the frontend taxonomy is not expanded yet, keep the current behavior and ship the data first. Classification cleanup can follow when multiple education providers justify a visible class.

## Publication Integration

All teacher-related bundles feed the existing `default` site.

No new public site is created.

| Scope | Owner |
| --- | --- |
| `data/providers/teacher_qual/` | `teacher_qual` provider |
| `mirror/providers/teacher_qual/` | `teacher_qual` provider |
| `data/providers/teacher_recruit_<source>/` | each future 教甄 provider |
| `mirror/providers/teacher_recruit_<source>/` | each future 教甄 provider |
| `data/sites/default/` | `default` site |
| `bundles/sites/default/` | `default` site |

Teacher recruitment providers should use the same site-owned release sharding as the rest of `default`.

## Implementation Sequence

1. Keep `teacher_qual` as the single national 教師資格考試 provider.
2. Recrawl `teacher_qual` from the official selector instead of limiting it to the latest year.
3. Maintain `docs/developer/providers/teacher_recruit-source-index.md`.
4. Record official county and school sources in that index before implementation.
5. Implement source-specific providers only when the index marks them `implement`.
6. Keep `teacher_recruit_tainan` and `teacher_recruit_taipei_junior` as source-specific 教甄 providers.
7. Keep `teacher_recruit_taipei_elementary` as a current-year scoped official article provider until a stable Taipei elementary archive or second reviewed official year is found.
8. Keep `teacher_recruit_newtaipei` current-year scoped until the official API exposes reviewed historical records.
9. Keep Taoyuan elementary, Kaohsiung, and Central Alliance current-year scoped until reviewed official archives or stable prior-year patterns are found.
10. Keep Taichung, Keelung, and Hsinchu County as Central Alliance provenance/watch rows unless they expose their own teacher paper downloads.
11. Add more 教甄 providers only after the source index marks them `implement`.

## Non-Goals

- No broad web crawler for every county and school.
- No unofficial paper mirrors.
- No job-posting calendar.
- No registration workflow.
- No automatic extraction from PDFs unless the existing bundle pipeline needs it.

## Risks

### Risk: 教甄 Sources Disappear Or Move

County and school recruitment pages often move after the recruitment year ends.

Mitigation: implement only stable archive pages, mirror source files, and keep source-index stability notes.

### Risk: Too Many Tiny Bundles

Per-school or per-subject bundles can explode catalog size.

Mitigation: default to source-level or level-level bundles. Split by subject only when the source has enough history and users would clearly search that way.

### Risk: Users Expect National Completeness

教甄 candidates may assume the product covers every county and school.

Mitigation: label 教甄 bundles by source owner and year coverage. Do not market 教甄 as nationally complete until the source index proves broad coverage.

## Acceptance Criteria

- The national 教師資格考試 path remains `teacher_qual` / `teacher-qual`.
- `teacher-qual` publishes all official archive years with downloadable files from ROC 094-115 / AD 2005-2026.
- 教甄 is documented as a staged source family, not a single national provider.
- `teacher_recruit_tainan`, `teacher_recruit_taipei_junior`, and `teacher_recruit_taipei_elementary` are documented as partial, source-specific 教甄 implementations.
- `teacher_recruit_newtaipei` is documented as an implemented official API-backed 教甄 source, with detail/list mismatch validation required before ingesting attachments.
- `teacher_recruit_taoyuan_elementary`, `teacher_recruit_kaohsiung`, and `teacher_recruit_central_alliance` are documented as implemented current-year source-specific providers.
- `teacher_recruit_taipei_elementary` is documented as an implemented current-year source-specific provider that mirrors official `含答案` PDFs as `question_answer`.
- Central Alliance documentation records official provenance from Taichung, Keelung, and Hsinchu County, and does not treat the vendor domain as a standalone official archive.
- A future engineer can decide whether a county or school source is implementable using the eligibility rules above.
- The default site can publish teacher bundles without a new public site.
- Additional implementation work is gated on a specific 教甄 source passing the source-index rule.
