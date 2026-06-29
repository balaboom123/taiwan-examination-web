# Requested Topic Support Matrix

This records the provider-scope decision for the 2026-06 request.

| Requested topic | Status | Provider / decision |
|---|---|---|
| 教師資格考試 | Implemented | `teacher_qual` mirrors official national teacher qualification past-paper bundles from `tqa.rcpet.edu.tw/TEA_Exam/TEA03.aspx`. |
| 教師甄試 | Partially implemented | `teacher_recruit_tainan`, `teacher_recruit_taipei_junior`, `teacher_recruit_newtaipei`, `teacher_recruit_taoyuan_elementary`, `teacher_recruit_kaohsiung`, and `teacher_recruit_central_alliance` mirror verified official/public source surfaces. County and school recruitment papers remain scattered, so additional 教甄 providers require source-index approval. |
| GEPT 全民英檢 | Implemented | `gept_cert` mirrors official LTTC/GEPT practice PDFs, ZIPs, and listening MP3 assets. |
| TOCFL 華語文能力測驗 | Implemented | `tocfl_cert` mirrors official TOCFL downloadable reference materials. Mock-test pages are HTML/interactive, not direct paper archives. |
| JLPT/TOPIK local schedules | Deferred | Local pages are schedules/registration information, not official downloadable past-paper archives. |
| TQC | Implemented | `tqc_cert` mirrors official TQC sample-paper PDFs. |
| iPAS | Implemented | `ipas_cert` mirrors official certification download PDFs. These are exam/download documents, not historical solved paper archives. |
| iCAP | Deferred | The WDA iCAP public site exposes resource/download listings via AJAX, but no public official exam-paper archive was identified. |
| 軍校正期班/專業軍官班 | Deferred | No stable official public historical paper archive was identified. |
| 警察特考 | Already supported | Covered by the existing `moex` provider, including general police and police personnel special exams. |
| 不動產經紀人、地政士 | Already supported | Covered by the existing `moex` provider under professional/technical examinations. |
