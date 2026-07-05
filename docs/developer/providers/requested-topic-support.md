# Requested Topic Support Matrix

This records the provider-scope decision for the 2026-06 request.

| Requested topic | Status | Provider / decision |
|---|---|---|
| 教師資格考試 | Implemented | `teacher_qual` mirrors official national teacher qualification past-paper bundles from `tqa.rcpet.edu.tw/TEA_Exam/TEA03.aspx`. |
| 教師甄試 | Partially implemented | `teacher_recruit_tainan`, `teacher_recruit_taipei_junior`, `teacher_recruit_taipei_elementary`, `teacher_recruit_newtaipei`, `teacher_recruit_taoyuan_elementary`, `teacher_recruit_kaohsiung`, and `teacher_recruit_central_alliance` mirror verified official/public source surfaces. County and school recruitment papers remain scattered, so additional 教甄 providers require source-index approval. |
| GEPT 全民英檢 | Implemented | `gept_cert` mirrors official LTTC/GEPT practice PDFs, ZIPs, and listening MP3 assets. |
| TOCFL 華語文能力測驗 | Implemented | `tocfl_cert` mirrors official TOCFL reference materials plus direct mock-test question, audio, answer, and listening-script downloads. |
| 客語能力認證 | Implemented | `hakka_cert` mirrors official Hakka certification vocabulary/question PDFs and audio ZIPs from 哈客網路學院. |
| 臺灣台語語言能力認證 | Implemented | `taigi_cert` mirrors official Taiwan Taiwanese certification sample papers and audio from the MOE certification site. |
| JLPT | Implemented | `jlpt_cert` mirrors official JLPT practice workbook PDFs and listening MP3 assets from `jlpt.jp`. |
| TOPIK local schedules/browser practice | Deferred | Official TOPIK pages expose schedules and browser practice flows, not a stable direct downloadable PDF/past-paper archive for this bundle pipeline. |
| TQC | Implemented | `tqc_cert` mirrors official paginated TQC sample-paper PDFs. |
| iPAS | Implemented | `ipas_cert` mirrors IT-adjacent iPAS official certification PDFs for `ISE`, `OIA`, `AIAP`, and `AIOT`, including learning-resource question PDFs where available. |
| iCAP 勞動部職能發展應用平台 | Deferred | Official iCAP sources expose competency standards, courses, workflows, and resource downloads, but no public IT exam-paper archive was identified. Keep it out unless non-paper competency-resource bundles become an explicit product requirement. |
| 軍校正期班/專業軍官班 | Deferred | No stable official public historical/sample-paper archive was identified on checked MND recruitment surfaces. |
| 警察特考 | Already supported | Covered by the existing `moex` provider, including general police and police personnel special exams. |
| 不動產經紀人、地政士 | Already supported | Covered by the existing `moex` provider under professional/technical examinations. |
