# Exam Classification

Frontend classification system that maps bundles into a two-tier taxonomy: **class** (考試類別) and **subclass** (考試子類別). Every bundle resolves to exactly one class and one subclass.

Source of truth: `frontend/src/lib/exam-classification.ts`.

## Design Decisions

- **Frontend-only.** Classification runs at bundle load time in the browser, not in the backend pipeline. The backend publishes provider-neutral bundle metadata (`id`, `name`, `years`, `fileCount`, `url`); the frontend enriches each bundle with `examClass` and `examSubclass` via `classifyBundle()`.
- **Why frontend?** Classification is a UI concern — it determines filter categories, not data pipeline behavior. Keeping it frontend-only avoids coupling the publication contract to display taxonomy, and lets the taxonomy evolve without re-publishing data.
- **100% coverage required.** Every bundle must classify. Uncategorized bundles are a bug. The fallback subclass per class ensures this, but new providers should still verify coverage explicitly.

## Taxonomy

| Class | Subclasses |
| --- | --- |
| 公職 | 行政類科, 法律類科, 商科類科, 技術類科, 資訊類科, 醫藥衛生, 警消海巡, 外交國際, 交通海事, 農林漁牧, 文教類科, 導遊領隊, 其他 |
| 升學 | 學測 |

Classes and subclasses are ordered. The order in `EXAM_CLASSES` and `CLASS_CONFIG[class].subclasses` is the display order in the UI.

## Algorithm

Classification follows a two-step process:

```
bundle(id, name)
  → step 1: provider routing (match id prefix → class)
  → step 2: subclass pattern matching (match name against class rules)
  → fallback: class-level default subclass
```

### Step 1: Provider Routing

`PROVIDER_ROUTES` maps bundle ID prefixes to classes. Each route specifies:

| Field | Required | Purpose |
| --- | --- | --- |
| `idPrefix` | yes | Bundle ID prefix to match (e.g. `"ceec-"`) |
| `examClass` | yes | The class this provider belongs to |
| `defaultSubclass` | no | If set, skip pattern matching and use this subclass directly |

Routes are checked in order; first match wins. If no route matches, the bundle falls through to `DEFAULT_CLASS` (currently `"公職"`).

Current routes:

| ID Prefix | Class | Default Subclass | Rationale |
| --- | --- | --- | --- |
| `ceec-` | 升學 | 學測 | CEEC bundles are university entrance exams; currently only 學測 exists |

All other bundles (moex provider) have no explicit route and fall through to `DEFAULT_CLASS = "公職"`.

### Step 2: Subclass Pattern Matching

Each class owns a `ClassConfig` with:

- `subclasses` — ordered list of subclass names (display order)
- `rules` — ordered list of `[RegExp, subclass]` pairs
- `fallback` — subclass to use when no rule matches

For each bundle, the engine iterates the class's rules in order and returns the first matching subclass. If no rule matches, the fallback subclass is returned.

**Rule priority matters.** Rules are ordered from most specific to most general. More specific patterns (e.g. `導遊人員`) are placed before broader patterns (e.g. `行政`) that could also match.

## Adding a New Provider (New Class)

When onboarding a new exam source that belongs to a different class:

### 1. Update `EXAM_CLASSES`

Add the new class to the tuple. Position determines UI display order.

```typescript
export const EXAM_CLASSES = ["公職", "升學", "新類別"] as const
```

### 2. Add a provider route

Add an entry to `PROVIDER_ROUTES` mapping the provider's ID prefix to the new class:

```typescript
const PROVIDER_ROUTES: readonly ProviderRoute[] = [
  { idPrefix: "ceec-", examClass: "升學", defaultSubclass: "學測" },
  { idPrefix: "newprovider-", examClass: "新類別" },
]
```

If the new provider has only one subclass (like ceec/升學), set `defaultSubclass` to skip pattern matching entirely.

### 3. Add class config

Add an entry to `CLASS_CONFIG` with subclasses, rules, and fallback:

```typescript
const CLASS_CONFIG: Record<ExamClass, ClassConfig> = {
  // ... existing ...
  新類別: {
    subclasses: ["子類A", "子類B", "其他"],
    rules: [
      [/patternA/, "子類A"],
      [/patternB/, "子類B"],
    ],
    fallback: "其他",
  },
}
```

### 4. Verify coverage

After adding the config, verify that every bundle from the new provider classifies correctly. Run the classification against all bundle names and check:

- Zero bundles fall to the fallback unexpectedly
- No bundle is misclassified due to pattern overlap
- The fallback subclass count is acceptable

No frontend component changes are needed — `CategoryFilter`, `SUBCLASS_ORDER`, and the filter logic in `App.tsx` all derive from `EXAM_CLASSES` and `CLASS_CONFIG` automatically.

## Adding a New Provider (Existing Class)

If a new provider's bundles belong to an existing class (e.g. another government exam source that should merge into 公職):

### 1. Add a provider route (optional)

If the new provider's bundles need different routing logic (e.g. a default subclass), add a route:

```typescript
{ idPrefix: "newgov-", examClass: "公職" }
```

If the new provider's bundles should simply use the existing class's pattern rules (same as moex), no route is needed — bundles with unmatched ID prefixes already fall through to `DEFAULT_CLASS`.

### 2. Update pattern rules if needed

If the new provider introduces bundle names not covered by existing patterns, add rules to the class's `rules` array. Place specific rules before general ones.

## Modifying Subclass Rules

### Adding a new subclass

1. Add the subclass name to `CLASS_CONFIG[class].subclasses` at the desired display position.
2. Add one or more `[RegExp, subclass]` entries to `CLASS_CONFIG[class].rules`.
3. Place the new rules according to specificity — before any broader rule that could match the same names.

### Adding patterns to an existing subclass

Extend the existing regex with additional alternations:

```typescript
// Before
[/醫師|護理/, "醫藥衛生"],
// After
[/醫師|護理|新職類/, "醫藥衛生"],
```

### Pattern priority guidelines

- More specific terms first (e.g. `食品(?!管理)` before the general `管理` in 行政類科)
- Use negative lookahead `(?!...)` when a term would otherwise match a broader rule (e.g. `食品(?!管理)` prevents 食品管理 from matching 醫藥衛生 when it should be 行政類科)
- Test edge cases: a bundle named "X管理" might match both a specific subclass (via X) and 行政類科 (via 管理). Whichever rule appears first wins.

## Current Pattern Coverage (公職)

As of the initial implementation, all 684 moex bundles classify without falling to "其他". The pattern rules cover:

| Subclass | Bundle Count | Key Patterns |
| --- | --- | --- |
| 行政類科 | ~120 | 行政, 民政, 戶政, 地政, 管理, 政風, 人事, 勞工, ... |
| 技術類科 | ~98 | 工程, 技師, 測量, 機械, 電子, 化學, 環境, ... |
| 醫藥衛生 | ~90 | 醫師, 護理, 藥師, 營養師, 物理治療, 食品(?!管理), ... |
| 交通海事 | ~87 | 船長, 航海, 飛航, 運輸, 交通工, 港灣, ... |
| 農林漁牧 | ~54 | 農業, 林業, 漁業, 畜牧, 獸醫, 園藝, ... |
| 外交國際 | ~48 | 外交, 國際經濟商務, 國際新聞, ... |
| 法律類科 | ~45 | 律師, 法官, 司法, 書記官, 檢察, 監獄, ... |
| 商科類科 | ~44 | 會計, 審計, 財務, 金融, 統計, 關稅, ... |
| 警消海巡 | ~37 | 警察, 消防, 海巡, 鑑識, 刑事, ... |
| 文教類科 | ~24 | 教育行政, 文化行政, 圖書, 新聞, ... |
| 導遊領隊 | ~20 | 導遊人員, 領隊人員 |
| 資訊類科 | ~17 | 資訊, 電腦打字 |
| 其他 | 0 | (fallback — should remain at 0) |

## File Ownership

| File | Owns |
| --- | --- |
| `frontend/src/lib/exam-classification.ts` | Taxonomy, provider routes, pattern rules, classification engine |
| `frontend/src/components/category-filter.tsx` | Two-tier filter UI (consumes `EXAM_CLASSES`, `SUBCLASS_ORDER`) |
| `frontend/src/hooks/use-bundles.ts` | Enrichment at load time (calls `classifyBundle()`) |
| `frontend/src/App.tsx` | Filter state management (consumes `EXAM_CLASSES`, `ExamClass`) |
| `frontend/src/types.ts` | `Bundle` interface with `examClass`/`examSubclass` fields |
