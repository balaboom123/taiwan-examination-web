# Provider Spec: `tii_cert`

## Summary

- `provider_id`: `tii_cert`
- status: implemented; bounded listing discovery captured, live verification and historical breadth blocked
- target site: `default`
- canonical paper listings: `https://edu.tii.org.tw/exam/users/exam_message/1`, `https://edu.tii.org.tw/exam/users/exam_message/58785`, and `https://edu.tii.org.tw/exam/users/exam_message/58786`
- alternate history source: `https://edu.tii.org.tw/home/mpage/downloadfiles`
- machine-readable evidence: `data/providers/tii_cert/source-manifest.json`
- publication shape: three generated financial-certification bundles containing five files; one investment-insurance brochure is incorrectly published as a question

This audit is evidence-only. It does not change the adapter, retained state, mirrors, generated bundles, frontend feed, releases, or deployment.

## Authoritative source boundary

The current official message pages list 10 dated paper events and 24 question/answer entries across three exam families and AD 2024–2026:

| Official family | Listed events | Listed paper files |
| --- | ---: | ---: |
| 投資型保險商品業務員資格測驗 | 2 | 8 |
| 防制洗錢與打擊資恐專業人員測驗 | 2 | 4 |
| 永續發展基礎能力測驗 | 6 | 12 |

The investment-insurance page lists ROC 114 September 14 and ROC 115 January 11, with question and answer files for each of two sections. The AML page lists ROC 114 June 7 and ROC 115 June 28 question/answer pairs. The sustainability page lists six question/answer pairs: ROC 113 June 22 and August 17, ROC 114 February 22 and June 7, and ROC 115 January 24 and June 6.

This is not a complete historical denominator. The AML page also points to a download-center ZIP named `保發中心-防制洗錢測驗歷屆試題`. Its contents and year range cannot be enumerated while the source's certificate chain fails normal verification. The official navigation also exposes active financial-market-common-knowledge and policyholder-service exams, a discontinued property-insurance actuarial exam, and commissioned employment-service testing. No current official paper listing was established for those families, so they are recorded as reviewed source-family boundaries rather than silently counted as covered.

## Retained, normalized, and public state

Local state contains three raw events, five normalized records, five checksum-valid mirrors, zero failures, and three generated/public bundles.

- AML ROC 114 round 2 contributes two correctly identified retained papers.
- Sustainability ROC 115 round 3 contributes two correctly identified retained papers.
- Investment insurance ROC 115 round 1 contributes one 769,250-byte retained PDF. Its first page identifies it as the ROC 115 annual examination brochure, revised June 8, 2026—not a question paper.
- Twenty of the 24 currently listed paper entries are absent locally.
- Seven of the 10 listed paper events have no local event identity; the three overlapping identities do not imply file completeness.
- The public investment-insurance bundle publishes the brochure as its sole `question` file. Publication validation passes because normalized state, bundle metadata, frontend metadata, and release metadata inherited the same misclassification.

## Transport, rights, and source restrictions

Normal HTTPS verification currently fails for `edu.tii.org.tw`. `curl` exits 60 and OpenSSL reports verification error 20, `unable to get local issuer certificate`, for the presented `*.tii.org.tw` leaf. No unverified request, certificate bypass, or guessed direct-file crawl was used. Consequently the audit records official indexed listing labels but does not claim live bytes, sizes, checksums, response codes, or complete direct URLs for the 24 listed entries. `robots.txt` also remains unverified through the same transport path.

TII pages display a copyright notice. No exam-PDF republication grant was found. Public download/listing availability is not treated as permission to mirror files into GitHub releases; redistribution requires an operator/legal decision and a takedown process.

## Adapter gap and fail-closed discovery contract

The current adapter scans four exam-intro pages instead of their historical message pages. It takes the first ROC year/round-looking text from the whole page, accepts every `message_download` anchor, classifies every non-answer anchor as a question, and keeps only the first URL per `question`/`answer` role. This makes schedules, brochures, forms, and multiple sections indistinguishable and explains the published brochure.

A corrected discovery path must:

1. enumerate the reviewed exam navigation and preserve explicit source-family dispositions;
2. parse each historical message-page row, date, section, file role, label, and direct URL together;
3. reject brochures, schedules, forms, applications, textbooks, and venue notices from paper roles;
4. support multiple sections and multiple dated events rather than `setdefault`-collapsing them;
5. enumerate the AML history ZIP in an approved, certificate-validating environment and reconcile its contents without inventing years;
6. fail closed on unknown rows, duplicate URLs, category growth, missing answer pairs, and transport verification failure; and
7. require legal/takedown approval before mirror or release publication.

## Safe migration sequence

1. Keep `sync-tii-cert.yml` off releasable branches.
2. Preserve the three raw events, five normalized records, five mirrors, and current generated checksums as audit evidence.
3. Repair the official certificate chain or run from an approved trust environment; do not add a broad unverified-TLS exception.
4. Implement message-page and download-center discovery in isolation and snapshot exact URL/byte evidence.
5. Reconcile all 10 currently listed events, 24 direct entries, and the AML ZIP-expanded denominator.
6. Quarantine or reclassify the brochure, import only approved paper assets, and update raw, normalized, bundle, frontend, and release projections atomically.
7. Run focused tests plus aggregate inventory, strict catalog/history, publication, release-plan, frontend, production-build, browser, accessibility, and release-download gates before release.

No retained-file deletion, history rewrite, release upload, or deployment is authorized by this spec.

## Completion conditions

TII is complete only when:

- every official TII exam family has a reviewed paper-source disposition;
- the three current message pages and AML history ZIP have exact event/file inventories or current evidence-backed blockers;
- all listed files have certificate-verified response, byte, and checksum evidence before they are called covered;
- all 10 currently listed events and 24 paper entries trace through retained state or reviewed blocked/excluded evidence;
- the brochure is absent from question/answer publication or is explicitly reclassified outside the paper archive;
- no schedule, form, application, or textbook can enter a paper role;
- robots, redistribution, attribution, and takedown decisions are recorded; and
- aggregate release gates pass on the same commit.
