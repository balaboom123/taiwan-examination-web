# IT Certifications Topic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `電腦/資訊證照` topic classification and tighten source coverage for the existing TQC and IT-adjacent iPAS providers.

**Architecture:** Reuse the existing provider/site pipeline. Add frontend classification routes, split iPAS output by certification code before routing, and keep iCAP documented as deferred because it is not an exam-paper source.

**Tech Stack:** Python provider clients and unittest tests, TypeScript frontend classification, Markdown docs.

**Implementation status (2026-07-03):** Implemented. Public site data now contains `tqc-cert`, `ipas-cert-ise`, `ipas-cert-oia`, `ipas-cert-aiap`, and `ipas-cert-aiot` with GitHub release download URLs; the broad `ipas-cert` bundle is no longer listed in the public frontend bundle data.

---

## Files

- Modify: `frontend/src/lib/exam-classification.ts`
- Modify: `docs/developer/exam-classification.md`
- Modify: `app/providers/tqc_cert/client.py`
- Modify: `tests/test_tqc_cert.py`
- Modify: `app/providers/ipas_cert/client.py`
- Modify: `tests/test_ipas_cert.py`
- Modify: `docs/developer/providers/tqc_cert-spec.md`
- Modify: `docs/developer/providers/ipas_cert-spec.md`
- Modify: `docs/developer/providers/requested-topic-support.md`

## Task 1: Add IT Certification Classification

**Files:**

- Modify: `frontend/src/lib/exam-classification.ts`
- Modify: `docs/developer/exam-classification.md`

- [ ] **Step 1: Add class to `EXAM_CLASSES`**

Add `電腦/資訊證照` after the existing language-certification class. Keep all existing class label strings exactly as they are in the file; only append the new class.

```typescript
export const EXAM_CLASSES = ["公職", "升學", "國營事業", "技檢", "金融證照", "教師資格考試", "語言檢定", "電腦/資訊證照"] as const
```

- [ ] **Step 2: Add provider routes**

Add these routes after the language-certification routes and before broad pattern-routed providers:

```typescript
{ idPrefix: "tqc-cert", examClass: "電腦/資訊證照", defaultSubclass: "TQC 電腦技能基金會" },
{ idPrefix: "ipas-cert-ise", examClass: "電腦/資訊證照", defaultSubclass: "iPAS 資訊安全工程師" },
{ idPrefix: "ipas-cert-oia", examClass: "電腦/資訊證照", defaultSubclass: "iPAS 營運智慧分析師" },
{ idPrefix: "ipas-cert-aiap", examClass: "電腦/資訊證照", defaultSubclass: "iPAS AI應用規劃師" },
{ idPrefix: "ipas-cert-aiot", examClass: "電腦/資訊證照", defaultSubclass: "iPAS AIoT應用工程師" },
```

- [ ] **Step 3: Add class config**

Add:

```typescript
"電腦/資訊證照": {
  subclasses: [
    "TQC 電腦技能基金會",
    "iPAS 資訊安全工程師",
    "iPAS 營運智慧分析師",
    "iPAS AI應用規劃師",
    "iPAS AIoT應用工程師",
  ],
  rules: [],
  fallback: "TQC 電腦技能基金會",
},
```

- [ ] **Step 4: Update classification docs**

In `docs/developer/exam-classification.md`, add a taxonomy row:

| Class | Subclasses |
|---|---|
| 電腦/資訊證照 | TQC 電腦技能基金會, iPAS 資訊安全工程師, iPAS 營運智慧分析師, iPAS AI應用規劃師, iPAS AIoT應用工程師 |

Add route rows:

| ID Prefix | Class | Default Subclass | Rationale |
|---|---|---|---|
| `tqc-cert` | 電腦/資訊證照 | TQC 電腦技能基金會 | CSF TQC sample-paper PDFs. |
| `ipas-cert-ise` | 電腦/資訊證照 | iPAS 資訊安全工程師 | iPAS 資訊類 certification with published question PDFs. |
| `ipas-cert-oia` | 電腦/資訊證照 | iPAS 營運智慧分析師 | iPAS 資訊類 certification with official briefs and learning resources. |
| `ipas-cert-aiap` | 電腦/資訊證照 | iPAS AI應用規劃師 | iPAS cross-domain AI certification with published question PDFs. |
| `ipas-cert-aiot` | 電腦/資訊證照 | iPAS AIoT應用工程師 | iPAS electronic-communications certification with AIoT/IoT content. |

## Task 2: Harden `tqc_cert` Source Coverage

**Files:**

- Modify: `app/providers/tqc_cert/client.py`
- Modify: `tests/test_tqc_cert.py`
- Modify: `docs/developer/providers/tqc_cert-spec.md`

- [ ] **Step 1: Add parser test for multiple sample-paper pages**

In `tests/test_tqc_cert.py`, add a small fixture with two page links and two PDF links. The test should prove the parser can separate sample PDFs from pagination links.

```python
def test_parse_exam_papers_keeps_only_sample_pdfs():
    html = """
    <h4>資訊科技Python</h4>
    <p>專業知識領域類</p>
    <p>2020/08/13</p>
    <a href="../user/Example/python.pdf">範例試卷下載</a>
    <a href="javascript:__doPostBack('pager','Page$2')">2</a>
    """

    papers = parse_exam_papers(html)

    assert [paper.title for paper in papers] == ["資訊科技Python"]
    assert papers[0].category == "專業知識領域類"
    assert papers[0].published_year == 2020
    assert papers[0].url.endswith("/user/Example/python.pdf")
```

- [ ] **Step 2: Add pagination discovery**

Add a helper in `app/providers/tqc_cert/client.py` that returns page fetch actions from the TQC sample-paper listing. Keep it local to this provider.

```python
@dataclass(frozen=True)
class TqcPageRequest:
    event_target: str
    event_argument: str
```

Parse `javascript:__doPostBack(...)` pagination anchors and fetch each page once. If the live site exposes plain links instead, normalize those links and fetch them once. Deduplicate by URL or `(event_target, event_argument)`.

- [ ] **Step 3: Use all pages in `_entries()`**

Update `_entries()` so it fetches the first page, discovers additional pages, fetches them, and deduplicates papers by final PDF URL.

- [ ] **Step 4: Update provider spec**

In `docs/developer/providers/tqc_cert-spec.md`, record:

- source URL: `https://www.tqc.org.tw/TQCNet/ExamPaper.aspx`
- source has paginated sample-paper listing
- only `/user/Example/*.pdf` links are mirrored
- TQC+ was evaluated but is not part of `tqc_cert`

## Task 3: Split And Harden `ipas_cert` Source Coverage

**Files:**

- Modify: `app/providers/ipas_cert/client.py`
- Modify: `tests/test_ipas_cert.py`
- Modify: `docs/developer/providers/ipas_cert-spec.md`
- Modify: `app/normalizer.py`
- Modify: `app/site_registry.py`

- [ ] **Step 1: Support current and legacy hosts**

Keep `HOME_URL = "https://www.ipas.org.tw/"`, but normalize redirects and parsed links so these hosts both work:

```python
IPAS_HOSTS = ("www.ipas.org.tw", "ipd.nat.gov.tw")
CURRENT_BASE_URL = "https://ipd.nat.gov.tw/ipas/"
```

- [ ] **Step 2: Limit this topic to IT-adjacent iPAS codes**

Add this provider-local map:

```python
IPAS_IT_CERTS = {
    "ISE": "資訊安全工程師",
    "OIA": "營運智慧分析師",
    "AIAP": "AI應用規劃師",
    "AIOT": "AIoT應用工程師",
}
```

When discovering certification codes from the iPAS home page, keep only these codes for the `電腦/資訊證照` implementation. Do not route all iPAS certifications to this class.

- [ ] **Step 3: Return one exam option per included code**

Change `discover_exams()` to return code-specific source exam IDs:

```python
return [
    ExamOption(
        code=f"ipas-cert-{code.lower()}-{year_ad}",
        year_ad=year_ad,
        year_roc=year_ad - 1911,
        label=f"iPAS {name}",
    )
    for code, name in IPAS_IT_CERTS.items()
]
```

- [ ] **Step 4: Fetch source pages per certification code**

For each discovered certification code, fetch:

```python
(
    "news",
    "exam-info",
    "learning-resources",
    "downloads",
)
```

Use the current canonical base:

```python
f"https://ipd.nat.gov.tw/ipas/certification/{code}/{section}"
```

- [ ] **Step 5: Add tests for learning-resource question PDFs**

In `tests/test_ipas_cert.py`, add a fixture with `歷屆考題` and `公告試題` labels.

```python
def test_parse_pdf_downloads_extracts_learning_resource_questions():
    html = """
    <section>歷屆考題</section>
    <a href="/ipas/api/proxy/uploads/115-1公告試題_資訊安全管理概論.pdf">下載</a>
    <a href="https://ipd.nat.gov.tw/ipas/api/proxy/uploads/iPAS經濟部產業人才能力鑑定_疑義考題處理需知.pdf">下載</a>
    """

    downloads = parse_pdf_downloads(html, cert_code="ISE")

    labels = [download.label for download in downloads]
    assert "115-1公告試題_資訊安全管理概論.pdf" in labels
    assert "iPAS經濟部產業人才能力鑑定_疑義考題處理需知.pdf" in labels
```

- [ ] **Step 6: Add tests for code filtering and source IDs**

Add:

```python
def test_discover_exams_returns_only_it_adjacent_codes():
    client = IpasCertClient()

    exams = client.discover_exams(2026)

    assert [exam.code for exam in exams] == [
        "ipas-cert-ise-2026",
        "ipas-cert-oia-2026",
        "ipas-cert-aiap-2026",
        "ipas-cert-aiot-2026",
    ]
```

- [ ] **Step 7: Deduplicate downloads across pages**

Deduplicate by normalized URL. Keep the first label and `cert_code`.

- [ ] **Step 8: Add normalizer entries**

In `app/normalizer.py`, add specific iPAS entries before the broad `ipas-cert-` fallback:

```python
"ipas-cert-ise-": ("ipas-cert-ise", "iPAS 資訊安全工程師"),
"ipas-cert-oia-": ("ipas-cert-oia", "iPAS 營運智慧分析師"),
"ipas-cert-aiap-": ("ipas-cert-aiap", "iPAS AI應用規劃師"),
"ipas-cert-aiot-": ("ipas-cert-aiot", "iPAS AIoT應用工程師"),
```

- [ ] **Step 9: Add site min-year overrides**

In `app/site_registry.py`, add:

```python
"ipas-cert-ise": 1,
"ipas-cert-oia": 1,
"ipas-cert-aiap": 1,
"ipas-cert-aiot": 1,
```

Leave the existing broad `ipas-cert` override only if legacy already-published data still needs compatibility.

- [ ] **Step 10: Update provider spec**

In `docs/developer/providers/ipas_cert-spec.md`, record:

- current canonical host: `https://ipd.nat.gov.tw/ipas/`
- compatibility host: `https://www.ipas.org.tw/`
- primary material pages: `/learning-resources`, `/exam-info`, `/downloads`
- IT-adjacent codes in this topic: `ISE`, `OIA`, `AIAP`, `AIOT`
- `learning-resources` contains published question PDFs for `ISE` and `AIAP`; `OIA` and `AIOT` currently expose official learning guides/briefs but no visible past-question section

## Task 4: Keep iCAP Deferred And Document Why

**Files:**

- Modify: `docs/developer/providers/requested-topic-support.md`

- [ ] **Step 1: Keep iCAP status as deferred**

Use this row text:

| Requested topic | Status | Provider / decision |
|---|---|---|
| iCAP 勞動部職能發展應用平台 | Deferred | Official iCAP sources expose competency standards, certified competency-oriented courses, certification workflows, and data downloads, but no public IT exam-paper archive was identified. Add an iCAP provider only if the product supports non-paper competency metadata or an official exam-paper archive appears. |

- [ ] **Step 2: Keep `wdasec_skill` separate**

Do not route `wdasec-skill` to `電腦/資訊證照`. It covers all technical-skill trades, not only IT.

## Task 5: Verify

- [ ] **Step 1: Run provider tests**

```bash
uv run python -m unittest tests.test_tqc_cert tests.test_ipas_cert -v
```

Expected: both test modules pass.

- [ ] **Step 2: Run focused frontend build**

```bash
cd frontend
npm run build
```

Expected: TypeScript build passes and classification config has no missing class keys.

- [ ] **Step 3: Run frontend tests**

```bash
cd frontend
npm test
```

Expected: existing frontend tests pass.

- [ ] **Step 4: Manual classification check**

Confirm:

- `tqc-cert` resolves to `電腦/資訊證照 / TQC 電腦技能基金會`
- `ipas-cert-ise` resolves to `電腦/資訊證照 / iPAS 資訊安全工程師`
- `ipas-cert-oia` resolves to `電腦/資訊證照 / iPAS 營運智慧分析師`
- `ipas-cert-aiap` resolves to `電腦/資訊證照 / iPAS AI應用規劃師`
- `ipas-cert-aiot` resolves to `電腦/資訊證照 / iPAS AIoT應用工程師`
- `wdasec-skill` stays in its existing technical-skill class
- no `icap` route exists

## Skipped

- Skipped TQC+ provider implementation; add `tqcplus_cert` only when CSF TQC+ is explicitly in scope.
- Skipped broad iPAS classification; iPAS includes non-IT certifications, so this plan only routes IT-adjacent codes.
- Skipped iCAP provider implementation; add only when there is compatible public exam-paper content or a metadata catalog.
