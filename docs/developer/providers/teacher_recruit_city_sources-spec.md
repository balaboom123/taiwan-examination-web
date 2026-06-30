# Provider Spec: Additional City/County `teacher_recruit` Sources

## Summary

This spec records the next implementable city/county teacher-recruitment paper sources after Taipei, Tainan, and New Taipei.

Implemented provider candidates:

| provider_id | status | source family | source URL |
|---|---|---|---|
| `teacher_recruit_taipei_elementary` | implemented | Taipei city elementary teacher joint recruitment | `https://www.gov.taipei/News_Content.aspx?n=D0042A87C2F0270A&sms=78D644F2755ACCAA&s=0E5FFDCD602F05C2` |
| `teacher_recruit_taoyuan_elementary` | implemented | Taoyuan elementary teacher joint recruitment | `https://elementary.tyc.edu.tw/web/answer.aspx?openExternalBrowser=1` |
| `teacher_recruit_kaohsiung` | implemented | Kaohsiung elementary and special-education teacher recruitment | `https://exam.kh.edu.tw/teaexam/` and `https://exam.kh.edu.tw/special/index.jsp` |
| `teacher_recruit_central_alliance` | implemented | 115 Central Alliance teacher-selection questions and answers | `https://qa115-tse-cl.twrecruit.com.tw/Subject/news.php` and `https://qa115-tse-cl.twrecruit.com.tw/Ans2/news.php` |

Watch/provenance sources:

| source_id | role |
|---|---|
| `teacher_recruit_taichung_elementary_kindergarten` | official annual Taichung site that points paper users to Central Alliance |
| `teacher_recruit_keelung` | official Keelung selection system that links `試題疑義網址` to Central Alliance |
| `teacher_recruit_hsinchu_county` | official Hsinchu County bulletin that states teacher papers and answers are on Central Alliance |

## Source Model

### Taipei Elementary

The source is the official 臺北市政府 article for 114學年度公立國民小學教師聯合甄選初試試題:

```text
https://www.gov.taipei/News_Content.aspx?n=D0042A87C2F0270A&sms=78D644F2755ACCAA&s=0E5FFDCD602F05C2
```

The stable paper surface is the article's direct `Download.ashx` links on `www-ws.gov.taipei`. Official filenames are decoded from the base64 `n` query parameter and include:

- `1基礎類科知能_含答案.pdf`
- `2.1普通科_含答案.pdf`
- `2.2英語科_含答案.pdf`
- `2.3體育科_含答案.pdf`
- `2.4音樂科_含答案.pdf`
- `2.5視覺藝術科_含答案.pdf`
- `2.6輔導科_含答案.pdf`
- `2.7資訊科技科_含答案.pdf`
- `2.8閩南語_含答案.pdf`
- `2.9特教科(身障)_含答案.pdf`
- `2.10特教科(資優)_含答案.pdf`
- `2.11自然科_含答案.pdf`

Treat the source as current-year scoped. The city-wide Taipei news listing is not a stable teacher-paper archive.

### Taoyuan Elementary

The source is the official 桃園市115年度國民小學教師聯合甄選 site. The stable paper surface is:

```text
https://elementary.tyc.edu.tw/web/answer.aspx?openExternalBrowser=1
```

The page exposes direct `download_file.aspx?ids=<hash>` links for:

- question PDFs, for example `115桃教育A-試題.pdf`
- suggested-answer PDFs, for example `115桃教育A_建議答案.pdf`
- final-answer PDFs, for example `115桃教育A_正確答案.pdf`
- appeal/clarification material, which should be skipped unless a future product explicitly needs it

Use the anchor text as the official filename because the download URL uses opaque IDs.

### Kaohsiung

The source owner is Kaohsiung City. Use one provider because the regular elementary and special-education sites share the same owner and annual exam-site pattern.

Regular elementary source:

```text
https://exam.kh.edu.tw/teaexam/index.jsp?cnt=board/board.jsp&now_page=2
```

Current paper downloads are direct ZIP links under `/teaexam/upload/`:

- `試題.zip`
- `答案.zip`
- `正確答案.zip`

Special-education source:

```text
https://exam.kh.edu.tw/special/index.jsp
```

Current paper downloads are direct PDFs under `/special/upload/`, including:

- `身心障礙類試題教育局.pdf`
- `身心障礙類參考答案教育局.pdf`
- `正確答案-身心障礙類.pdf`
- `資賦優異類試題教育局.pdf`
- `資賦優異類參考答案教育局.pdf`
- `正確答案-資賦優異類.pdf`

Skip admission lists, venue maps, duplicate URL-encoded copies, teaching-demo topics, and brochure files.

### Central Alliance

The source is the current-year 115中區策略聯盟甄選試題疑義網站.

Question/reference-answer page:

```text
https://qa115-tse-cl.twrecruit.com.tw/Subject/news.php
```

Final-answer page:

```text
https://qa115-tse-cl.twrecruit.com.tw/Ans2/news.php
```

The subject page groups downloads by category:

| cate | level |
|---|---|
| `A` | 幼兒園 |
| `B` | 國小 |
| `C` | 國中 |

Question/reference downloads use:

```text
Subject/download.php?seq=<opaque>&type=question
Subject/download.php?seq=<opaque>&type=referenceanswer
```

Final-answer downloads use:

```text
Ans2/download.php?seq=<opaque>&type=finalanswer
```

This is a vendor domain, so the provider must preserve official provenance in docs and metadata. The source is accepted because official Taichung, Keelung, and Hsinchu County selection pages point candidates to it for papers or answer appeals. The `qa115-*` host is annual; do not assume `qa114-*` or older hosts exist.

## Output Model

| provider_id | canonical bundle | canonical name | default exam id pattern |
|---|---|---|---|
| `teacher_recruit_taipei_elementary` | `teacher-recruit-taipei-elementary` | `臺北市國小教師甄試` | `teacher-recruit-taipei-elementary-<roc_year>` |
| `teacher_recruit_taoyuan_elementary` | `teacher-recruit-taoyuan-elementary` | `桃園市國小教師甄試` | `teacher-recruit-taoyuan-elementary-<roc_year>` |
| `teacher_recruit_kaohsiung` | `teacher-recruit-kaohsiung` | `高雄市教師甄試` | `teacher-recruit-kaohsiung-<roc_year>-<scope>` |
| `teacher_recruit_central_alliance` | `teacher-recruit-central-alliance` | `中區策略聯盟教師甄試` | `teacher-recruit-central-alliance-<roc_year>-<level>` |

File types:

- `question`: question PDF/ZIP
- `question_answer`: combined question-and-answer PDF
- `answer`: suggested/reference answer PDF/ZIP
- `corrected_answer`: final/correct answer PDF/ZIP

Default to one canonical bundle per provider. Split into per-level bundles only after the first sync shows a combined bundle is hard to scan.

## Plan

1. Keep `teacher_recruit_taipei_elementary`, `teacher_recruit_taoyuan_elementary`, `teacher_recruit_kaohsiung`, and `teacher_recruit_central_alliance` current-year scoped until a reviewed official archive or stable prior-year pattern is found.
2. Keep Taichung, Keelung, and Hsinchu County as provenance/watch rows unless they begin hosting their own teacher paper files.
3. Add another provider only after its source-index row meets the official/public/downloadable eligibility rule.

## Non-Goals

- No private cram-school ZIP mirrors.
- No broad crawler across all county or school bulletin systems.
- No scraping login-only score, registration, or appeal submission pages.
- No automatic historical reconstruction from annual vendor domains that no longer resolve.
