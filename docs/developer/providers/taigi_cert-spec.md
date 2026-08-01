# Provider Spec: `taigi_cert`

## Summary

- `provider_id`: `taigi_cert`
- status: active; audit-partial
- target site: `default`
- source family: Ministry of Education Taiwanese-language certification self-learning resources
- source URL: `https://ttg.moe.edu.tw/tmt/view.php?page=resource`

## Source Model

The official page currently lists 37 resources. Thirty-five are grouped under A, B, and C sample forms and are accepted by this provider; `學習地圖` and `就是各門派比較啦` are general self-learning references and are explicitly outside the exam-material scope.

The A/B/C groups are undated. The current provider assigns the process year to all three events, so the retained AD 2026 identities are synthetic capture identities rather than source-declared examination years. Generic automated mirroring is also blocked: the official `robots.txt` disallows the site for wildcard agents and disallows `/tmt/src/`, where the downloadable assets live, even for named search bots that receive a narrower allowance. Do not bypass that policy.

## Output Model

- retained source exams: `taigi-cert-a-2026`, `taigi-cert-b-2026`, `taigi-cert-c-2026`
- intended source grouping: separate stable undated A/B/C identities
- file types: `question`, `listening_audio`
- provider data: `data/providers/taigi_cert/`
- workflow: `.github/workflows/sync-taigi-cert.yml`

The current site projection merges all 35 A/B/C records into one bundle titled `臺灣台語語言能力認證 A卷` through legacy canonical IDs. This is not a trustworthy public representation of the source taxonomy.

## Safe Next Steps

1. Obtain written permission or a source-policy change before another automated mirror refresh.
2. Replace process-year identity with reviewed stable undated resource identities.
3. Preserve A/B/C grouping through normalization and publication.
4. Record a redistribution/takedown decision before republishing.
