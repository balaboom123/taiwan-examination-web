# Provider Spec: `hce_nchu`

## Summary

- `provider_id`: `hce_nchu`
- status: source-gated
- target site: `default`
- source family: National Chung Hsing University HCE admission archive
- Shuati bucket: `/exams/hce_nchu`
- Shuati subjects: 化學, 普通生物及生化概論, 物理, 英文
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Rule

The accepted source must be an official National Chung Hsing University page or an official admission system named by the university. Public direct downloads are required. Private mirrors and practice sites are rejected.

## Source Proof Status

- last rechecked: 2026-07-05
- checked source: `https://recruit.nchu.edu.tw/college-exam/medicine/index-medicine.aspx?examc=F`
- checked department source: `https://pbmed.nchu.edu.tw/`
- checked admissions detail: `https://recruit.nchu.edu.tw/college-exam/medicine/115/115PbMed_PAPER.aspx`
- checked paging/detail: `https://recruit.nchu.edu.tw/college-exam/medicine/index-medicine.aspx?examc=F&p=2`, `https://pbmed.nchu.edu.tw/news/detail?id=233`
- result: the official paths expose admissions forms, schedules, and an answer-dispute notice, but no official public full-paper archive was found in the checked source path.
- decision: no provider code is wired for `hce_nchu` in this pass because the source rule rejects answer-dispute-only and zero-file providers.

## Discovery Model

If accepted, the provider mirrors official paper assets by year and subject into:

- `data/providers/hce_nchu/`
- `mirror/providers/hce_nchu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_nchu --site-id default
```

## Normalization Rules

- `provider_id`: `hce_nchu`
- `canonical_id`: `hce-nchu`
- `canonical_name`: `國立中興大學 HCE 入學考試`

## Non-Goals

- no third-party mirrors
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
