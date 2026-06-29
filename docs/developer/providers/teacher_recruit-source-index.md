# Teacher Recruitment Source Index

This index gates 教師甄試 provider work. Add only official public sources here; skip private cram-school mirrors even when they host convenient ZIP files.

| source_id | source_name | official_url | scope | has_downloadable_papers | year_depth | file_types | stability | decision | notes |
|---|---|---|---|---|---:|---|---|---|---|
| `k12ea-teacher-selection` | 全國高級中等以下學校教師選聘網 | `https://personnel.k12ea.gov.tw/tsn/` | national job and announcement portal | no | 0 | n/a | stable portal, not a paper archive | reject | Official Ministry/K-12 portal, but current public pages expose vacancies/news rather than downloadable past-paper archives. |
| `teacher_recruit_taipei_junior` | 臺北市政府教育局國中教師聯合甄選公告 | `https://www.doe.gov.taipei/News_Content.aspx?n=E831CA0A5CD0193D&sms=78D644F2755ACCAA&s=4A85C1A3A3BD7C48` | Taipei city junior-high formal teacher joint recruitment | yes | 2 | PDF, ODT | stable official article pages | implemented | Official DOE pages expose 113 and 114學年度 subject question/answer PDFs through direct `Download.ashx` links. |
| `teacher_recruit_tainan` | 臺南市國小教師甄選網 | `https://qualify.tn.edu.tw/trexamps/` | Tainan city elementary and pre-K special-ed teacher joint recruitment | yes | 1 | ZIP, PDF | stable current-year WebForms site | implemented | Official site exposes 115學年度 question ZIP, reference-answer ZIP, corrected-answer ZIP, and brochure/topic PDFs without login. Treat as current-year scoped. |

## Eligibility Rule

A source can move to `implement` or `implemented` only when it is official, public, downloadable, and stable enough to parse without login, CAPTCHA, or browser-only manual steps.
