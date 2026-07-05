# Provider Spec: `special_admission`

## Summary

- `provider_id`: `special_admission`
- status: implemented
- target site: `default`
- source family: official special-admission or special-selection exam archive
- Shuati bucket: `/exams/special`
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Overview

Source proof passed on 2026-07-05.

- accepted source owner: 115學年度身心障礙學生升學大專校院甄試委員會, hosted by National Central University
- source page: `https://cis.ncu.edu.tw/EnableSys/admissionInfo/examInfo/question`
- accepted coverage in local data: 102-115學年度 / 2013-2026
- accepted scope: 大學組 / 共同, limited to Shuati-listed subjects
- accepted file type: public direct PDF links

Shuati lists the bucket with subjects such as 國文, 英文, 數A, 數B, 物理, 化學, 生物, 歷史, and 地理. The official organizer and archive URL must be proven before provider code exists.

Accepted source properties:

- source owner: official education, university-admission, or commissioned exam body
- source access: public pages plus direct downloadable files
- authentication: none
- rejection rule: no provider if the bucket only maps to a private mirror or an unnamed practice source

## Discovery Model

The provider, if accepted, mirrors official subject paper assets by year and subject.

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
- local synced coverage: 102-115學年度 / 2013-2026, 216 files

## Non-Goals

- no provider before the organizer is proven
- no third-party mirrors
- no browser automation
- no Shuati crawling
