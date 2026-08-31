# Provider Spec: `hce_isu`

## Summary

- `provider_id`: `hce_isu`
- status: source-gated
- target site: `default`
- source family: I-Shou University HCE admission archive
- Shuati bucket: `/exams/hce_isu`
- Shuati subjects: 化學, 國文, 生物學, 英文
- publication shape: one canonical bundle asset owned by the `default` site if source proof passes

## Source Rule

The accepted source must be an official I-Shou University page or an official admission system named by the university. Public direct downloads are required. Private mirrors and practice sites are rejected.

## Source Proof Status

- last rechecked: 2026-07-05
- checked source: `https://www.isu.edu.tw/`
- checked admissions portal: `https://www.isu.edu.tw/admissions`
- result: the official admissions page exposes `學士後中醫學系` as an admission item, but no official public full-paper archive or direct paper/answer downloads were found in the checked source path.
- decision: no provider code is wired for `hce_isu` in this pass because the source rule rejects Shuati crawling and zero-file providers.

## Discovery Model

If accepted, the provider mirrors official paper assets by year and subject into:

- `data/providers/hce_isu/`
- `mirror/providers/hce_isu/`

The primary operator command is:

```bash
python -m app sync-full --provider hce_isu --site-id default
```

## Normalization Rules

- `provider_id`: `hce_isu`
- `canonical_id`: `hce-isu`
- `canonical_name`: `義守大學 HCE 入學考試`

## Non-Goals

- no third-party mirrors
- no broad crawling of university news pages
- no provider that would publish zero files
- no Shuati crawling
