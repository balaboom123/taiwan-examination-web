# Product

## Register

product

## Users

Taiwanese national-exam candidates (nurses, lawyers, accountants, civil-service applicants, technicians) preparing for 考選部 (Ministry of Examination, MOEX) exams. They arrive with one job: find their exam category (類科) and download every past paper for it as a single ZIP. Secondary users: tutors and cram-school staff collecting materials for students. Visits are short and task-driven, often from a search-engine link, on both desktop and mobile. Users read Traditional Chinese; year figures use the ROC calendar (民國).

## Product Purpose

A searchable index of pre-bundled past exam papers mirrored from the MOEX exam search site. Each bundle is a multi-year ZIP hosted on GitHub Releases. Success: a first-time visitor finds their 類科 and starts the download in under fifteen seconds, and trusts that the archive is complete and current. The site replaces the slow, form-driven official search with a single fast page.

## Brand Personality

沉穩、可靠、典藏 (composed, dependable, archival). The feel of a beautifully kept national archives reading room: quiet civic authority, paper and ink, official without bureaucratic clutter. Never playful, never corporate-SaaS.

## Anti-references

- Generic Tailwind SaaS: stone/teal defaults, gradient hero metrics, identical icon-card grids.
- The actual government portal look: cluttered notice boards, dated table chrome, banner carousels.
- Cutesy edtech (mascots, exclamation-mark copy, candy colors).
- Dark "developer tool" aesthetics; this is a daytime civic reference surface.

## Design Principles

1. **The download is the destination.** Every element on screen either helps the user find their 類科 or get the ZIP. Anything else is removed.
2. **Archive, not app.** Document-flavored details: ruled rows, paper-warm neutrals, seal-red accent used like an official stamp, serif display type (Noto Serif TC) over functional sans body.
3. **Density with dignity.** Hundreds of categories must scan fast: ruled-list rhythm, tabular/mono figures, restrained row height, no card bloat.
4. **Chinese-first typography.** Hierarchy and spacing are designed for Traditional Chinese text first; Latin and numerals are the supporting cast.
5. **Quiet authority.** Trust comes from completeness cues (counts, year ranges, data source) stated plainly, not from marketing flourish.

## Accessibility & Inclusion

WCAG 2.1 AA. Full keyboard operability for search, filters, and downloads; visible focus rings; `aria-live` result counts; respects `prefers-reduced-motion`; text contrast ≥ 4.5:1 on paper-tinted backgrounds; touch targets ≥ 44px on mobile.
