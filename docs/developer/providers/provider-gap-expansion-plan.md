# Provider Gap Expansion Plan

## Completed

1. `wdasec_skill`: fixed WebForms postback hidden-field replay, synced 2024-2026, and published eligible `wdasec-skill` groups; 128 older events remain explicitly tracked as normalization gaps.
2. `tocfl_cert`: added official mock-test question/audio/answer/script downloads and published `tocfl-cert`.
3. `hakka_cert`: added official audio ZIPs as `listening_audio` and published level bundles.
4. `jlpt_cert`: added official JLPT practice workbook PDFs/MP3s and published `jlpt-cert`.

## Gated

1. TOPIK stays out until an official direct downloadable paper archive is verified.
2. iCAP stays out unless non-paper competency-resource bundles become an explicit product requirement.
3. 軍校正期班/專業軍官班 stays out until an official historical/sample-paper archive is verified.
4. Remaining 教師甄試 sources must pass `teacher_recruit-source-index.md` before provider code is added.

## Verification

- `python -m pytest -q`: 459 passed, 63 subtests passed.
- `npm --prefix frontend test`: 19 passed.
- `npm --prefix frontend run lint`: passed.
- `npm --prefix frontend run build`: passed.
- `frontend-bundles.json` contains `wdasec-skill`, `tocfl-cert`, three `hakka-cert-*` bundles, and `jlpt-cert` with release URLs.
