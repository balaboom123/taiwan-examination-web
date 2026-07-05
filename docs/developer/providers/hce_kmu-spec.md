# Provider Spec: `hce_kmu`

## Summary

- `provider_id`: `hce_kmu`
- status: source-gated
- target site: `default`
- source family: Kaohsiung Medical University HCE admission archive
- Shuati bucket: `/exams/hce_kmu`
- Shuati subjects: 普通生物及生化概論, 有機化學, 物理及化學, 英文, 計算機概論與程式設計
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Rule

The accepted source must be an official Kaohsiung Medical University page or an official admission system named by the university. Public direct downloads are required. Private mirrors and practice sites are rejected.

## Source Proof Status

- last rechecked: 2026-07-05
- checked source: `https://enr.kmu.edu.tw/`
- checked admissions page: `https://enr.kmu.edu.tw/bac/bacm005.php`
- result: the official page exposes the current `學士後醫學系` admissions brief and schedule PDF, but no official public full-paper archive or direct paper/answer downloads were found in the checked source path.
- decision: no provider code is wired for `hce_kmu` in this pass because the source rule rejects non-paper admissions briefs and zero-file providers.

## Discovery Model

If accepted, the provider mirrors official paper assets by year and subject into:

- `data/providers/hce_kmu/`
- `mirror/providers/hce_kmu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_kmu --site-id default
```

## Normalization Rules

- `provider_id`: `hce_kmu`
- `canonical_id`: `hce-kmu`
- `canonical_name`: `高雄醫學大學 HCE 入學考試`

## Non-Goals

- no third-party mirrors
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
