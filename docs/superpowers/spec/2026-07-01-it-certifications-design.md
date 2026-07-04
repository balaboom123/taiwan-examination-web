# Computer / IT Certifications Design

## Goal

Support the requested topic "5. 電腦/資訊證照 (IT Certifications)" in the default exam catalog with a clear frontend class, accurate provider scope, and source decisions for:

- TQC (電腦技能基金會 CSF)
- iPAS 經濟部產業人才能力鑑定
- iCAP 勞動部職能發展應用平台

## Source Research

Sources were checked on 2026-07-01. Official sources are preferred; non-official sources are not needed for implementation decisions.

### TQC / CSF

| Source | URL | Use |
|---|---|---|
| TQC certification intro | https://www.tqc.org.tw/TQCNet/CertIntro.aspx | Defines TQC as a CSF enterprise talent skills certification. |
| TQC subjects | https://www.tqc.org.tw/TQCNet/Certificate.aspx | Lists official certification subjects, including professional knowledge, OS, database, office software, and related IT application categories. |
| TQC sample papers | https://www.tqc.org.tw/TQCNet/ExamPaper.aspx | Primary implemented source: public PDF sample papers by subject/category/publication date. |
| TQC file downloads | https://www.tqc.org.tw/TQCNet/Download.aspx | Administrative forms only; not a primary paper source. |
| TQC+ certification intro | https://www.tqcplus.org.tw/CertIntro.aspx | Related CSF certification family for design/software/engineering topics. |
| TQC+ subjects | https://www.tqcplus.org.tw/Certificate.aspx | Large official subject list, including software design and programming subjects. |
| TQC+ sample papers | https://www.tqcplus.org.tw/ExamPaper.aspx | Official CSF sample PDFs, but outside the initial requested TQC scope. |
| ITE home | https://www.itest.org.tw/ | Adjacent CSF information-professional certification family; useful future source, not part of the requested TQC/iPAS/iCAP scope. |

### iPAS / MOEA

| Source | URL | Use |
|---|---|---|
| iPAS home | https://www.ipas.org.tw/ | Redirects to the current iPAS site and lists certification categories, including 資訊類. |
| Current iPAS site | https://ipd.nat.gov.tw/ipas/ | Current canonical host after redirect; provider should tolerate both old and current hosts. |
| Plan goals | https://ipd.nat.gov.tw/ipas/plan/goal | Describes the MOEA talent assessment program and its training-assessment-employment loop. |
| Competency standards | https://ipd.nat.gov.tw/ipas/job-standards | Links iPAS competency standards and points users to iCAP for broader competency lookup. |
| Information security news | https://ipd.nat.gov.tw/ipas/certification/ISE/news | Shows current certification section shape and public test-question announcements. |
| Information security exam info | https://ipd.nat.gov.tw/ipas/certification/ISE/exam-info | Includes exam dates, subjects, pass conditions, briefs, and downloadable exam documents. |
| Information security learning resources | https://ipd.nat.gov.tw/ipas/certification/ISE/learning-resources | Contains current/past published question PDFs; this is a primary iPAS paper source. |
| Information security downloads | https://ipd.nat.gov.tw/ipas/certification/ISE/downloads | Administrative and exam-info downloads; useful but not enough alone. |
| OIA exam info | https://ipd.nat.gov.tw/ipas/certification/OIA/exam-info | 資訊類 certification page for 營運智慧分析師; has exam subjects, brief, and official downloads. |
| OIA learning resources | https://ipd.nat.gov.tw/ipas/certification/OIA/learning-resources | Has learning guides, references, and cloud courses; no public past-question section was visible on 2026-07-01. |
| AIAP exam info | https://ipd.nat.gov.tw/ipas/certification/AIAP/exam-info | Cross-domain AI certification page; has computer-test details, briefs, scope references, and downloads. |
| AIAP learning resources | https://ipd.nat.gov.tw/ipas/certification/AIAP/learning-resources | Contains public published question PDFs for 初級 and 中級 AI應用規劃師. |
| AIOT news | https://ipd.nat.gov.tw/ipas/certification/AIOT/news | Electronic-communications certification with AIoT/IoT content and CSF exam-service contact. |
| AIOT exam info | https://ipd.nat.gov.tw/ipas/certification/AIOT/exam-info | Contains AIoT exam subjects, computerized-test/practical-test split, brief, and downloads. |
| AIOT learning resources | https://ipd.nat.gov.tw/ipas/certification/AIOT/learning-resources | Has learning guides and cloud courses; no public past-question section was visible on 2026-07-01. |

### iCAP / MOL WDA

| Source | URL | Use |
|---|---|---|
| iCAP about | https://icap.wda.gov.tw/ap/about.php | Defines iCAP as a competency-development and application platform under WDA. |
| Competency standard query | https://icap.wda.gov.tw/ap/resources_datum.php | Search surface for competency standards, including fields for domain, industry, occupation, education classification, and source type. |
| Competency-oriented course query | https://icap.wda.gov.tw/Resources/resources_Class.aspx | Lists quality-certified competency-oriented courses; not exam papers. |
| Competency standard quality certification | https://icap.wda.gov.tw/ap/quality_1.php | Certification workflow for competency standard quality. |
| Course quality certification | https://icap.wda.gov.tw/ap/quality_2.php | Certification workflow for course quality. |
| Data downloads | https://icap.wda.gov.tw/ap/knowledge_downLoad.php | Public document downloads; not an IT exam-paper archive. |
| MOL legal basis | https://laws.mol.gov.tw/FLAW/FLAWDAT0201.aspx?id=FL070293 | States WDA may build the competency platform and publish competency standards, certified courses, and related resources. |

### Local Project Sources

| File | Current finding |
|---|---|
| `docs/developer/providers/tqc_cert-spec.md` | `tqc_cert` is active and mirrors TQC sample-paper PDFs. |
| `docs/developer/providers/ipas_cert-spec.md` | `ipas_cert` is active but documented as downloads-focused; source research shows learning-resource pages should also be included. |
| `docs/developer/providers/wdasec_skill-spec.md` | Labor technical-skill exams are already covered separately by `wdasec_skill`; this is not the same as iCAP. |
| `docs/developer/providers/requested-topic-support.md` | TQC and iPAS are implemented; iCAP is deferred because no official exam-paper archive was found. |
| `app/site_registry.py` | `tqc_cert` and `ipas_cert` already feed the `default` site. |
| `app/normalizer.py` | `tqc-cert-` and `ipas-cert-` canonical maps already exist. |
| `frontend/src/lib/exam-classification.ts` | No explicit `tqc-cert` or `ipas-cert` routes yet, so they fall through the default class. |

## Current State

Implemented on 2026-07-03.

| Source | Provider status | Publication status | Result |
|---|---|---|---|
| TQC | Active: `tqc_cert` | Included in `default` site | Explicit IT-cert classification is active; paginated `/user/Example/*.pdf` sample papers are mirrored and published as `tqc-cert`. |
| iPAS | Active: `ipas_cert` | Included in `default` site | IT-adjacent certifications are split into `ipas-cert-ise`, `ipas-cert-oia`, `ipas-cert-aiap`, and `ipas-cert-aiot`; learning-resource PDFs are included. |
| iCAP | Deferred | No provider | iCAP remains documented as competency metadata/course quality, not a public exam-paper archive. |
| WDA technical skill certification | Active: `wdasec_skill` | Included in `default` site | Stays under the technical-skill class; it is not routed wholesale into IT certifications. |

## Scope

This design covers:

- a new public frontend class: `電腦/資訊證照`
- routes for existing `tqc-cert` bundles and IT-scoped iPAS bundles
- provider-source refinements for TQC and iPAS
- a documented no-provider decision for iCAP

This design does not cover:

- implementing TQC+ as part of the initial topic
- turning iCAP competency/course metadata into exam bundles
- scraping registration, result lookup, certificate validation, or employment pages
- mirroring unofficial cram-school materials, private question banks, or login-only resources

## Design Decisions

### 1. Add `電腦/資訊證照` As A Frontend Class

TQC and IT-adjacent iPAS certifications should not fall through the generic default class. They are not civil-service exams, entrance exams, financial certifications, language certifications, or general technical-skill archives.

| Bundle prefix | Class | Subclass |
|---|---|---|
| `tqc-cert` | `電腦/資訊證照` | `TQC 電腦技能基金會` |
| `ipas-cert-ise` | `電腦/資訊證照` | `iPAS 資訊安全工程師` |
| `ipas-cert-oia` | `電腦/資訊證照` | `iPAS 營運智慧分析師` |
| `ipas-cert-aiap` | `電腦/資訊證照` | `iPAS AI應用規劃師` |
| `ipas-cert-aiot` | `電腦/資訊證照` | `iPAS AIoT應用工程師` |

No subclass regex rules are needed. These sources use `defaultSubclass`.

Important scope correction: iPAS also includes non-IT certifications under 電子通訊類, 智慧機械類, 綠能科技類, 生技醫藥類, and other categories. A broad `ipas-cert` route would misclassify those materials as IT. The provider should either split iPAS bundles by certification code or restrict this topic to the IT-adjacent codes above.

### 2. Keep TQC And iPAS As Separate Providers

The existing provider split is correct:

- `tqc_cert` owns the CSF TQC sample-paper source.
- `ipas_cert` owns the MOEA iPAS certification section source.

Merging them would only hide source-specific scraping rules. Each provider has its own host, page shape, and update cadence.

### 3. Do Not Add iCAP As An Exam Provider Yet

iCAP is an official WDA platform, but the checked sources expose:

- competency standards
- competency-oriented course quality certification
- certified course search
- data/download resources
- legal and process documents

No official public IT exam-paper archive was identified. Creating an `icap_cert` paper provider now would publish non-exam metadata as if it were exam material, which is wrong for the current catalog model.

Future iCAP work is eligible only if one of these becomes true:

- an official public exam/practice-paper archive appears on iCAP
- the product adds a separate non-paper metadata catalog for competency standards and certified courses

### 4. Keep `wdasec_skill` Separate

`wdasec_skill` covers Workforce Development Agency technical-skill certification past questions across many trades and levels. Some trades are IT-adjacent, but the provider is a broad technical-skill archive, not a computer/IT certification provider. Moving the whole bundle into `電腦/資訊證照` would misclassify non-IT trades.

### 5. Evaluate TQC+ Separately

TQC+ is official CSF material and has many sample PDFs, including software design/programming topics. It is a valid future source, but it is a sibling certification family with its own domain and larger pagination surface. Initial implementation should not silently expand `TQC` to mean `TQC + TQC+`.

If requested later, add a separate provider such as `tqcplus_cert`.

## Provider Refinements

### `tqc_cert`

Keep the source URL:

- `https://www.tqc.org.tw/TQCNet/ExamPaper.aspx`

Refinement:

- enumerate all TQC sample-paper pages, not only the first visible page
- keep PDF-only filtering under `/user/Example/`
- preserve subject title, source category, publication date, and direct PDF URL
- keep one provider-owned output root: `data/providers/tqc_cert/`
- keep one mirror root: `mirror/providers/tqc_cert/`

### `ipas_cert`

Treat the current host as canonical while keeping old host compatibility:

- preferred: `https://ipd.nat.gov.tw/ipas/`
- compatibility: `https://www.ipas.org.tw/`

Refinement:

- discover certification codes and official category labels from home/category links
- initially keep only IT-adjacent codes for this topic: `ISE`, `OIA`, `AIAP`, `AIOT`
- fetch each included certification's `/news`, `/exam-info`, `/learning-resources`, and `/downloads` pages
- mirror public PDF downloads from learning resources and exam/download pages
- prioritize `歷屆考題` / `公告試題` PDFs as exam-question material when those sections exist
- include exam briefs and rules only when they are official downloadable certification documents
- preserve each certification code in the source exam ID so frontend classification can distinguish iPAS subclasses
- keep one provider-owned output root: `data/providers/ipas_cert/`
- keep one mirror root: `mirror/providers/ipas_cert/`

## Publication Integration

No new site is needed. Both active providers already feed `default`.

| Scope | Owner |
|---|---|
| `data/providers/tqc_cert/` | `tqc_cert` |
| `mirror/providers/tqc_cert/` | `tqc_cert` |
| `data/providers/ipas_cert/` | `ipas_cert` |
| `mirror/providers/ipas_cert/` | `ipas_cert` |
| `data/sites/default/` | `default` site |
| `bundles/sites/default/` | `default` site |

No release-shard or gating change is required.

## Documentation Updates

Update or create:

- `docs/developer/exam-classification.md`
- `docs/developer/providers/tqc_cert-spec.md`
- `docs/developer/providers/ipas_cert-spec.md`
- `docs/developer/providers/requested-topic-support.md`

The iCAP row should stay deferred with the source-research evidence above.

## Risks

### TQC Pagination May Be ASP.NET Postback-Based

The visible sample-paper page has pagination. If page links are JavaScript postbacks, the scraper needs to preserve hidden form fields rather than guessing query parameters.

Mitigation: add a small pagination parser test before changing scraping behavior.

### iPAS Host Migration Could Break Link Regexes

iPAS now redirects from `www.ipas.org.tw` to `ipd.nat.gov.tw/ipas/`. Existing code that matches only old absolute upload URLs may miss current relative or new-host links.

Mitigation: normalize URLs after parsing and support both hosts in tests.

### iPAS Is Broader Than IT

The iPAS home page lists multiple official categories beyond 資訊類. Routing the entire existing `ipas-cert` bundle to `電腦/資訊證照` would be too coarse.

Mitigation: split iPAS output by certification code before classification, or filter this provider's public IT-topic output to `ISE`, `OIA`, `AIAP`, and `AIOT`.

### iCAP User Expectations

Users may expect iCAP under this topic because it is in the requested bullet list.

Mitigation: list iCAP as a researched deferred source, not an omitted source. Only add implementation when there is compatible content.

## Acceptance Criteria

- `電腦/資訊證照` exists as a frontend class.
- `tqc-cert` bundles classify as `電腦/資訊證照 / TQC 電腦技能基金會`.
- iPAS IT-adjacent bundles classify as `電腦/資訊證照` with code-specific subclasses for `ISE`, `OIA`, `AIAP`, and `AIOT`.
- Non-IT iPAS certification material is not silently routed into `電腦/資訊證照`.
- TQC source coverage includes all public TQC sample-paper pages available from `ExamPaper.aspx`.
- iPAS source coverage includes public question PDFs from `learning-resources`, not only administrative downloads.
- iCAP remains documented as deferred unless an official public exam-paper archive is found.
- `wdasec_skill` remains under its existing technical-skill classification.
- The support matrix remains accurate for TQC, iPAS, and iCAP.
