# Design

Visual system for the 考選部歷屆試題 archive site. Direction: 國家檔案室 archive editorial — a well-kept national archives reading room. Light theme only (daytime civic reference surface). Source of truth for tokens: `frontend/src/index.css`.

## Color

All colors are OKLCH, warm-tinted toward the paper hue. Never pure black or white.

| Token | Value | Role |
|---|---|---|
| `paper` | `oklch(0.967 0.007 90)` | Page background |
| `cream` | `oklch(0.985 0.005 95)` | Raised surfaces: inputs, hover rows, light text on dark/seal |
| `paper-deep` | `oklch(0.945 0.009 88)` | Sunken surfaces: segmented-control track, subtle hover |
| `line` | `oklch(0.885 0.012 85)` | Hairline rules, dividers, default borders |
| `line-strong` | `oklch(0.72 0.015 75)` | Emphasized borders (secondary buttons) |
| `ink-950` | `oklch(0.205 0.014 50)` | Headings, selected states, masthead rule |
| `ink-800` | `oklch(0.3 0.016 50)` | Body text |
| `ink-600` / `ink-500` | `oklch(0.44/0.5 …)` | Secondary text, metadata |
| `ink-400` | `oklch(0.6 0.015 62)` | Placeholders, tertiary/decorative text only |
| `seal-600` | `oklch(0.5 0.165 29)` | Vermillion seal red. Download actions, focus outline, stamps. Nothing else. |
| `seal-700` | `oklch(0.45 0.155 29)` | Seal hover |

Strategy: restrained. Seal red is the only accent and is reserved for the download action (the product's destination), the focus ring, and the stamp motif. Filter/selection states use ink, not seal.

## Typography

- **Display (`font-serif`)**: Noto Serif TC 600/700/900 — masthead, page title, bundle names, stamps.
- **Body (`font-sans`)**: Noto Sans TC 400/500/700 — UI labels, body copy.
- **Figures (`font-mono`)**: JetBrains Mono 400/500 — all numbers: years, counts, pagination, stats.

Chinese-first: tracking-wide on serif titles, letterspaced (0.2em+) small labels for subtitles. ROC years always mono, with AD year as a smaller suffix.

## Surfaces & layout

- Content container: `max-w-4xl`, single column.
- **Ruled ledger, not cards.** The bundle list is a `ul` with `border-y` + `divide-y` hairlines, extended `-mx-4` past the text edge. Rows hover to `cream`. No card borders, no shadows on the list.
- Masthead: 3px ink-950 rule at the very top, seal mark (試 on seal-600 square, 4px radius), hairline below. Sticky with `bg-paper/95 backdrop-blur-sm`.
- Stats are a colophon `dl` line between hairlines, not hero-metric blocks.
- Hero has a vertical `writing-mode: vertical-rl` ornament on desktop.
- Radii: 3–4px on stamps/tags/buttons (`rounded-[3px]`), `rounded-sm` on inputs. Nothing pill-shaped.
- Paper grain: fixed, pointer-events-none SVG turbulence overlay at 3.5% opacity, multiply blend (`.texture-paper`).

## Components

- **Download action**: seal-600 block, white Download icon + mono "ZIP" label (icon-only 44px square on mobile), hover seal-700, `active:translate-y-px`.
- **Stamp** (`components/stamp.tsx`): rotated −5° bordered seal-red serif mark, used for empty ("查無資料") and error ("載入失敗") states. Decorative, `aria-hidden`.
- **Filters**: square tags; selected = ink-950 fill with cream text; `aria-pressed` on all toggles.
- **Pagination**: mono folio numbers, current page = ink-950 square with `aria-current="page"`.
- **Skeleton**: ruled rows matching the list layout, shimmer in paper tones.

## Motion

Product register: no page-load choreography. Single 240ms fade-in when the list resolves; 150–250ms color transitions on interactive elements; `prefers-reduced-motion` disables all animation globally (see `index.css`).

## Accessibility

Focus ring: 2px seal-600 outline, 2px offset, on `:focus-visible`. Result counts in an `aria-live="polite"` region. Touch targets 44px for primary actions. Text contrast ≥ 4.5:1 (`ink-500` is the floor for informative text; `ink-400` is decorative only).
