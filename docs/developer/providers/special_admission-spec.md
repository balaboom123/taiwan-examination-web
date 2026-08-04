# Provider Spec: `special_admission`

## Summary

- `provider_id`: `special_admission`
- status: implemented
- target site: `default`
- source family: official special-admission or special-selection exam archive
- Shuati bucket: `/exams/special`
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Overview

Source proof passed on 2026-07-05 and was fully rechecked on 2026-07-30.

- accepted source owner: 115學年度身心障礙學生升學大專校院甄試委員會, hosted by National Central University
- source page: `https://cis.ncu.edu.tw/EnableSys/admissionInfo/examInfo/question`
- official selector coverage: 102-115學年度 / 2013-2026, 14 year events
- accepted scope: 大學組 / 共同, limited to the nine Shuati-listed subjects
- accepted assets: 216 public question/answer PDF links; all matched local state on 2026-07-30
- source policy: `robots.txt` explicitly allows `/EnableSys/`; no blanket redistribution license or copyright terms were linked from the archive page

Shuati lists the bucket with subjects such as 國文, 英文, 數A, 數B, 物理, 化學, 生物, 歷史, and 地理. The official organizer and archive URL must be proven before provider code exists.

Accepted source properties:

- source owner: official education, university-admission, or commissioned exam body
- source access: public pages plus direct downloadable files
- authentication: none
- rejection rule: no provider if the bucket only maps to a private mirror or an unnamed practice source

## Discovery Model

The provider mirrors official subject paper assets by year and subject. The manifest records one official event per selector year. The asset reconciliation separately checks every accepted subject/file URL because event-level manifest agreement alone does not prove paper completeness.

The same official pages also contain 二技組 and 四技二專組 rows. They are intentionally excluded from this provider because the accepted Shuati mapping is specifically 大學組 / 共同; they require distinct archive-family scope decisions rather than silent inclusion.

Provider-owned outputs live under:

- `data/providers/special_admission/`
- `mirror/providers/special_admission/`

The scheduled workflow for routine refresh is:

- `.github/workflows/sync-special-admission.yml`

The primary operator command is:

```bash
python -m app sync-full --provider special_admission --site-id default
```

## Normalization Rules

- all normalized records carry `provider_id = "special_admission"`
- all public records map into one canonical bundle
- canonical bundle identity:
  - `canonical_id`: `special-admission`
  - `canonical_name`: `特殊選才或特殊招生`

## Implementation Status

- provider package: `app/providers/special_admission/`
- focused tests: `tests/test_special_admission.py`
- published bundle: `special-admission`
- source manifest: 14/14 official selector events for 102-115學年度 / 2013-2026, captured 2026-07-30
- per-year evidence stores accepted asset counts and URL hashes; HTML hashes are capture evidence only because dynamic page markup can change
- local synced coverage: 14 events and 216 normalized files; all accepted live subject/file URLs match exactly

## Non-Goals

- no 二技組 or 四技二專組 rows without a separate documented source-family decision
- no third-party mirrors
- no browser automation
- no Shuati crawling
