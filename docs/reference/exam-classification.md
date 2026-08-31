# Frontend display classification

Status: compatibility/presentation reference
Owner: frontend maintainers
This document is not the official exam-identity source.

Official identity is resolved in the backend by app/classification.py from catalog/ mappings and is persisted in the v2 feed. frontend/src/lib/exam-classification.ts maps published bundles to display classes/subclasses for filtering and provides a compatibility fallback only when it receives a legacy v1 feed without structured facets.

## Responsibilities

Backend/catalog owns:

- exam domain, family, series, level, track, variants, and stage;
- bundle membership and purity;
- historical mappings, confidence, review, and migration;
- stable v2 bundle_id.

Frontend owns:

- display class/subclass labels;
- ordering and filter presentation;
- compatibility behavior for legacy feeds;
- no official identity inference for v2 records.

A v2 bundle must expose structured facets such as seriesId, levelId, and trackId. New UI code should render those fields and use the display classifier only to choose presentation grouping. Do not add a frontend regex to repair a backend bundle.

## Current display taxonomy

The existing two-tier UI taxonomy remains useful as a navigation projection:

| Class | Examples of subclasses |
| --- | --- |
| 公職 | 行政類科, 法律類科, 技術類科, 資訊類科, 醫藥衛生, 警消海巡, 外交國際, 交通海事, 農林漁牧, 文教類科 |
| 升學 | 學測, 分科測驗, 國中教育會考 |
| 國營事業 | 國營事業聯招, 台電僱員, 中油甄試, 台水甄試, 台糖甄試 |
| 技檢 | 技術士技能檢定 |
| 金融證照 | 證券期貨, 銀行金融, 保險 |
| 語言檢定 | GEPT, TOCFL, 客語, 臺灣台語 |
| 電腦/資訊證照 | TQC, iPAS and related certifications |

Exact display order and fallback rules remain in frontend/src/lib/exam-classification.ts. They are not a replacement for catalog concepts.

## Adding or changing UI categories

1. Confirm that the backend feed already carries the required structured facets.
2. Change frontend display configuration and add UI tests.
3. Do not change bundle grouping or release assets in a UI-only change.
4. For a new provider, add backend mapping/catalog coverage first, then add a display route if the UI needs a new class.
5. Run the whole-catalog audit so the new provider is not hidden by a frontend fallback.
